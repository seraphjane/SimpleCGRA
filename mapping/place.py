import sys
import random
import math
sys.path.append(".")

import numpy as np
import cvxpy as cp

import common.utils as utils
from common.utils import Base
from common.graph import HyperGraph
from arch.protocols import *
from mapping.route import *

class AnalyticPlacer: 

    MAXITER = 1024 * 12
    PATIENCE = 1024
    MEMOPT = True
    MEMOPTITER = 16

    def __init__(self, RRG: HyperGraph, filename: str, fixed: dict = {}, temper: float = 5.0, silent: bool = False): 
        self._silent = silent
        self._fixed = fixed
        self._temper = temper
        self._RRG = RRG
        self._coords = {}
        self._types = {}
        self._dmys = {}
        self._mems = {}
        self._ios = {}
        self._categories = {}
        self._grid = {}
        self._gridFUs = {}
        self._fuTypes = {}
        self._fu2coords = {}
        self._placement = {}
        self._routing = {}
        self._router = MazeRouter(self._RRG)
        # self._router = CliqueRouter(self._RRG)

        with open(filename, "r") as fin: 
            lines = fin.readlines()
        for line in lines: 
            splited = line.split()
            if len(splited) < 4: 
                continue
            fuName = splited[0]
            fuType = splited[1]
            self._fuTypes[fuName] = fuType
            x, y = int(splited[2]), int(splited[3])
            self._coords[fuName] = (x, y)
            self._types[fuName] = fuType
            if not (x, y) in self._grid: 
                self._grid[(x, y)] = {}
                self._gridFUs[(x, y)] = []
            if not fuType in self._grid[(x, y)]: 
                self._grid[(x, y)][fuType] = 0
            self._grid[(x, y)][fuType] += 1
            self._gridFUs[(x, y)].append(fuName)
            if not fuType in self._fu2coords: 
                self._fu2coords[fuType] = []
            self._fu2coords[fuType].append((x, y))
                
        for name, coord in self._coords.items(): 
            fuType = self._types[name]
            if not fuType in self._categories: 
                self._categories[fuType] = {}
            self._categories[fuType][name] = coord
            if fuType == "DUMMY": 
                self._dmys[name] = coord
            if fuType == "MEM": 
                self._mems[name] = coord
            if fuType in ["IO", "INPUT", "OUTPUT"]: 
                self._ios[name] = coord
    
    def place(self, DFG: HyperGraph, compat: dict, fixed: dict = {}, thread=1): 
        self._DFG = DFG
        self._contracted = HyperGraph()
        self._compat = compat
        self._fixed = fixed
        self._placement = {}
        self._routing = {}
        self._ops = {}
        self._opList = []
        self._numOps = 0
        self._name2index = {}
        for name, vertex in self._DFG.vertices().items(): 
            if len(name.split(".")) == 1: 
                self._ops[name] = vertex.attr("optype")
                self._opList.append(name)
                self._contracted.addVertex(name)
                self._name2index[name] = len(self._name2index)
                self._numOps += 1 
        for vname, vertex in self._DFG.vertices().items(): 
            for net in self._DFG.netsOut(vname): 
                source = net.fr().split(".")[0]
                sink   = net.to()[0].split(".")[0]
                if net.fr().split(".")[0] == net.fr() or net.to()[0].split(".")[0] == net.to()[0]: 
                    continue
                self._contracted.addNet([source, sink])
        self._distMat = self._contracted.distMat()

        return self.solve()

    def solve(self): 
        self._cost = 0.0
        self._cons = []
        self._cons2 = {}
        self._lbXs = {}
        self._lbYs = {}
        self._ubXs = {}
        self._ubYs = {}
        self._lbXsOri = {}
        self._lbYsOri = {}
        self._ubXsOri = {}
        self._ubYsOri = {}
        self._xs = cp.Variable(shape=(1, self._numOps), integer=True, boolean=False, name="x[i]") 
        self._ys = cp.Variable(shape=(1, self._numOps), integer=True, boolean=False, name="y[i]") 
        # self._distX = cp.abs(self._xs.T - self._xs) 
        # self._distY = cp.abs(self._ys.T - self._ys) 

        self._fuXs = {}
        self._fuYs = {}
        for fuType, info in self._categories.items(): 
            array = np.array(list(info.values()))
            self._fuXs[fuType] = array[:, 0:1].T
            self._fuYs[fuType] = array[:, 1:].T

        # Assign fixed positions (MEM, in ["IO", "INPUT", "OUTPUT"]?)
        self._dmyOps = []
        self._memOps = []
        self._ioOps  = []
        for name, op in self._ops.items(): 
            if "DUMMY" in self._compat[name]: 
                self._dmyOps.append(name)
            if "MEM" in self._compat[name]: 
                self._memOps.append(name)
            if "INPUT" in self._compat[name] or "OUTPUT" in self._compat[name] or "IO" in self._compat[name]: 
                self._ioOps.append(name)
        if len(self._dmyOps) > len(self._dmys): 
            print("FAILED: Not enough dummy resources. ")
            return {}, {}, {}
        if len(self._memOps) > len(self._mems): 
            print("FAILED: Not enough memory resources. ")
            return {}, {}, {}
        if len(self._ioOps) > len(self._ios): 
            print("FAILED: Not enough IO resources. ")
            return {}, {}, {}
        coordDmys = list(self._dmys.values())
        coordMems = list(self._mems.values())
        coordIOs  = list(self._ios.values())
        random.shuffle(coordDmys)
        random.shuffle(coordMems)
        random.shuffle(coordIOs)

        if AnalyticPlacer.MEMOPT: 
            # self._memOps & coordMems
            distMat1 = np.zeros([len(self._memOps), len(self._memOps)])
            for idx in range(len(self._memOps)): 
                for jdx in range(len(self._memOps)): 
                    distMat1[idx][jdx] = self._distMat[self._name2index[self._memOps[idx]]][self._name2index[self._memOps[jdx]]]
            distMat2 = np.zeros([len(self._memOps), len(self._memOps)])
            for idx in range(len(self._memOps)): 
                for jdx in range(len(self._memOps)): 
                    distMat2[idx][jdx] = abs(coordMems[idx][0] - coordMems[jdx][0]) + abs(coordMems[idx][1] - coordMems[jdx][1])
            last = np.sum(distMat1 * distMat2)
            for idx in range(AnalyticPlacer.MEMOPTITER): 
                tmp = coordMems.copy()
                random.shuffle(tmp)
                distMat2 = np.zeros([len(self._memOps), len(self._memOps)])
                for idx in range(len(self._memOps)): 
                    for jdx in range(len(self._memOps)): 
                        distMat2[idx][jdx] = abs(coordMems[idx][0] - coordMems[jdx][0]) + abs(coordMems[idx][1] - coordMems[jdx][1])
                curr = np.sum(distMat1 * distMat2)
                if curr > last: 
                    coordMems = tmp
                    last = curr

        for idx in range(len(self._dmyOps)): 
            assert self._dmyOps[idx] in self._fixed
            assert self._fixed[self._dmyOps[idx]] in self._coords
            x = self._coords[self._fixed[self._dmyOps[idx]]][0]
            y = self._coords[self._fixed[self._dmyOps[idx]]][1]
            index = self._name2index[self._dmyOps[idx]]
            assert self._opList[index] == self._dmyOps[idx]
            self._cons.append(self._xs[0, index] == x)
            self._cons.append(self._ys[0, index] == y)
            self._lbXs[self._dmyOps[idx]] = x
            self._lbYs[self._dmyOps[idx]] = y
            self._ubXs[self._dmyOps[idx]] = x
            self._ubYs[self._dmyOps[idx]] = y
            self._lbXsOri[self._dmyOps[idx]] = x
            self._lbYsOri[self._dmyOps[idx]] = y
            self._ubXsOri[self._dmyOps[idx]] = x
            self._ubYsOri[self._dmyOps[idx]] = y
        for idx in range(len(self._memOps)): 
            x = coordMems[idx][0]
            y = coordMems[idx][1]
            index = self._name2index[self._memOps[idx]]
            assert self._opList[index] == self._memOps[idx]
            self._cons.append(self._xs[0, index] == x)
            self._cons.append(self._ys[0, index] == y)
            self._lbXs[self._memOps[idx]] = x
            self._lbYs[self._memOps[idx]] = y
            self._ubXs[self._memOps[idx]] = x
            self._ubYs[self._memOps[idx]] = y
            self._lbXsOri[self._memOps[idx]] = x
            self._lbYsOri[self._memOps[idx]] = y
            self._ubXsOri[self._memOps[idx]] = x
            self._ubYsOri[self._memOps[idx]] = y
        for idx in range(len(self._ioOps)): 
            x = coordIOs[idx][0]
            y = coordIOs[idx][1]
            index = self._name2index[self._ioOps[idx]]
            assert self._opList[index] == self._ioOps[idx]
            self._cons.append(self._xs[0, index] == -1)
            self._cons.append(self._ys[0, index] >= 0)
            self._cons.append(self._ys[0, index] <= 3)
            self._lbXs[self._ioOps[idx]] = -1
            self._lbYs[self._ioOps[idx]] = 0
            self._ubXs[self._ioOps[idx]] = -1
            self._ubYs[self._ioOps[idx]] = 3
            self._lbXsOri[self._ioOps[idx]] = -1
            self._lbYsOri[self._ioOps[idx]] = 0
            self._ubXsOri[self._ioOps[idx]] = -1
            self._ubYsOri[self._ioOps[idx]] = 3
        for name in self._ops: 
            if not name in self._memOps and not name in self._ioOps: 
                index = self._name2index[name]
                assert self._opList[index] == name
                self._cons.append(self._xs[0, index] >= 0)
                self._cons.append(self._xs[0, index] <= 3)
                self._cons.append(self._ys[0, index] >= 0)
                self._cons.append(self._ys[0, index] <= 3)
                self._lbXs[name] = 0
                self._lbYs[name] = 0
                self._ubXs[name] = 3
                self._ubYs[name] = 3
                self._lbXsOri[name] = 0
                self._lbYsOri[name] = 0
                self._ubXsOri[name] = 3
                self._ubYsOri[name] = 3

        self._distXs = []
        self._distYs = []
        for vname, vertex in self._DFG.vertices().items(): 
            for net in self._DFG.netsOut(vname): 
                source = net.fr().split(".")[0]
                sink   = net.to()[0].split(".")[0]
                if source == sink: 
                    continue
                index1 = self._name2index[source]
                assert self._opList[index1] == source
                index2 = self._name2index[sink]
                assert self._opList[index2] == sink
                fu1 = self._compat[source][0] #TODO
                fu2 = self._compat[sink][0] #TODO
                distX = cp.abs(self._xs[0, index1] - self._xs[0, index2])
                distY = cp.abs(self._ys[0, index1] - self._ys[0, index2])
                if fu1 == "MEM" or fu2 == "MEM": 
                    distX = 4.0 * distX
                    distY = 1.0
                if fu1 in ["IO", "INPUT", "OUTPUT"] or fu2 in ["IO", "INPUT", "OUTPUT"]: 
                    distX = 1.0
                    distY = 4.0 * distY
                self._distXs.append(distX)
                self._distYs.append(distY)
        assert len(self._distXs) == len(self._distYs)

        for idx in range(len(self._distXs)): 
            self._cost = self._cost + self._distXs[idx]
            self._cost = self._cost + self._distYs[idx]

        MaxIter = 64
        results = []
        overuses = []
        objectives = []
        for iter in range(MaxIter): 
            # Global placement 
            obj  = cp.Minimize(self._cost)
            prob = cp.Problem(obj, self._cons + list(self._cons2.values()))
            # prob.solve(solver=cp.GUROBI, verbose=False)
            # prob.solve(solver=cp.GLPK_MI, verbose=False)
            prob.solve(solver=cp.SCIP, verbose=False)
            if prob.status != "optimal": 
                if not self._silent: 
                    print("Iteration:", iter, "; Status:", prob.status, "; Value:", prob.value)
                return {}, {}, {}
            if not self._silent: 
                print("Iteration:", iter, "; Status:", prob.status, "; Value:", prob.value)
            xs = self._xs.value.astype(np.int32)
            ys = self._ys.value.astype(np.int32)
            results.append((xs, ys))
            objectives.append(prob.value)
            for name in self._ops: 
                index = self._name2index[name]
                assert self._opList[index] == name
                # if not self._silent: 
                #     print(" -> " + name + "\t(" + str(xs[0, index]) + ", " + str(ys[0, index]) + ")")
            # print(self._grid)

            # Legalization
            gridOps = {}
            gridOpCount = {}
            for key, _ in self._grid.items(): 
                gridOps[key] = []
                gridOpCount[key] = {}
            for idx in range(xs.shape[1]): 
                x = xs[0, idx]
                y = ys[0, idx]
                op = self._opList[idx]
                fu = self._compat[op][0] #TODO
                assert (x, y) in gridOps
                gridOps[(x, y)].append(op)
                if not fu in gridOpCount[(x, y)]: 
                    gridOpCount[(x, y)][fu] = 0
                gridOpCount[(x, y)][fu] += 1
            # print(utils.dict2str(gridOps))
            # print(utils.dict2str(gridOpCount))
            
            def overuse(op, coord): 
                fu = self._compat[op][0] #TODO
                if gridOpCount[coord][fu] > self._grid[coord][fu]: 
                    return True
                return False

            okay = True
            needToMove = {}
            for op in self._opList: 
                index = self._name2index[op]
                assert self._opList[index] == op
                x = xs[0, index]
                y = ys[0, index]
                needToMove[op] = False
                if overuse(op, (x, y)): 
                    needToMove[op] = True
                    okay = False
            # print(utils.dict2str(needToMove))
            if okay: 
                overuses.append(0)
                break

            overuses.append(0)
            for name, need in needToMove.items(): 
                overuses[-1] += 1 if need else 0
            
            for coord, ops in gridOps.items(): 
                assert coord in gridOpCount
                toMove = {}
                distances = {}
                for op in ops: 
                    fu = self._compat[op][0]
                    if needToMove[op]: 
                        if not fu in toMove: 
                            toMove[fu] = []
                            distances[fu] = []
                        toMove[fu].append(op)
                        distances[fu].append(HyperGraph.MAX)
                for fu, ops in toMove.items(): 
                    distsAvg = {}
                    distsMin = {}
                    distsMax = {}
                    counts   = {}
                    for op in ops: 
                        index        = self._name2index[op]
                        distsAvg[op] = HyperGraph.MAX
                        distsMin[op] = HyperGraph.MAX
                        distsMax[op] = HyperGraph.MAX
                        assert self._opList[index] == op
                        counts[op] = 0
                        for op2 in self._opList: 
                            jndex = self._name2index[op2]
                            assert self._opList[jndex] == op2
                            if op2 != op and not needToMove[op2] and self._distMat[index][jndex] < HyperGraph.MAX: 
                                distsAvg[op]  += self._distMat[index][jndex]
                                distsMin[op]  = min(distsMin[op], self._distMat[index][jndex])
                                distsMax[op]  = max(distsMax[op], self._distMat[index][jndex])
                                counts[op] += 1
                        if counts[op] > 0: 
                            distsAvg[op] = distsAvg[op] / counts[op]
                        else: 
                            distsAvg[op] = HyperGraph.MAX
                    # tmp = sorted(ops, key=lambda x: distsAvg[x])
                    tmp = sorted(ops, key=lambda x: distsMin[x])
                    needToMove[tmp[0]] = False
                    for idx in range(1, len(tmp) - 1): 
                        needToMove[tmp[idx]] = None
            # print(utils.dict2str(needToMove))
            
            for name, need in needToMove.items(): 
                fu = self._compat[name][0] #TODO
                index = self._name2index[name]
                assert self._opList[index] == name
                if need is None: 
                    if name + "_X" in self._cons2: 
                        del self._cons2[name + "_X"]
                    if name + "_Y" in self._cons2: 
                        del self._cons2[name + "_Y"]
                elif need: 
                    # if name + "_X" in self._cons2: 
                    #     del self._cons2[name + "_X"]
                    # if name + "_Y" in self._cons2: 
                    #     del self._cons2[name + "_Y"]
                    densityX = [0, 0, ]
                    densityY = [0, 0, ]
                    countX = [0, 0, ]
                    countY = [0, 0, ]
                    totalX = [0, 0, ]
                    totalY = [0, 0, ]

                    if xs[0, index] > self._lbXs[name]: 
                        for coord in self._grid: 
                            counts = self._grid[coord]
                            if coord[0] < xs[0, index] and fu in counts: 
                                totalX[0] += counts[fu]
                        for idx in range(len(xs[0, :])): 
                            fu2 = self._compat[self._opList[idx]][0] #TODO
                            if xs[0, idx] < xs[0, index] and fu == fu2: 
                                countX[0] += 1

                    if xs[0, index] < self._ubXs[name]: 
                        for coord in self._grid: 
                            counts = self._grid[coord]
                            if coord[0] > xs[0, index] and fu in counts: 
                                totalX[1] += counts[fu]
                        for idx in range(len(xs[0, :])): 
                            fu2 = self._compat[self._opList[idx]][0] #TODO
                            if xs[0, idx] > xs[0, index] and fu == fu2: 
                                countX[1] += 1
                    
                    if ys[0, index] > self._lbYs[name]: 
                        for coord in self._grid: 
                            counts = self._grid[coord]
                            if coord[1] < ys[0, index] and fu in counts: 
                                totalY[0] += counts[fu]
                        for idx in range(len(ys[0, :])): 
                            fu2 = self._compat[self._opList[idx]][0] #TODO
                            if ys[0, idx] < ys[0, index] and fu == fu2: 
                                countY[0] += 1

                    if ys[0, index] < self._ubYs[name]: 
                        for coord in self._grid: 
                            counts = self._grid[coord]
                            if coord[1] > ys[0, index] and fu in counts: 
                                totalY[1] += counts[fu]
                        for idx in range(len(ys[0, :])): 
                            fu2 = self._compat[self._opList[idx]][0] #TODO
                            if ys[0, idx] > ys[0, index] and fu == fu2: 
                                countY[1] += 1

                    if totalX[0] > 0: 
                        densityX[0] = countX[0] / totalX[0]
                    else: 
                        densityX[0] = HyperGraph.MAX
                    if totalX[1] > 0: 
                        densityX[1] = countX[1] / totalX[1]
                    else: 
                        densityX[1] = HyperGraph.MAX
                    if totalY[0] > 0: 
                        densityY[0] = countY[0] / totalY[0]
                    else: 
                        densityY[0] = HyperGraph.MAX
                    if totalY[1] > 0: 
                        densityY[1] = countY[1] / totalY[1]
                    else: 
                        densityY[1] = HyperGraph.MAX

                    if densityX[0] == HyperGraph.MAX and densityX[1] == HyperGraph.MAX and \
                       densityY[0] == HyperGraph.MAX and densityY[1] == HyperGraph.MAX: 
                        if not self._silent: 
                            print("WARNING: No space available for " + name)
                        self._lbXs[name] = self._lbXsOri[name]
                        self._ubXs[name] = self._ubXsOri[name]
                        self._lbYs[name] = self._lbYsOri[name]
                        self._ubYs[name] = self._ubYsOri[name]
                        if name + "_X" in self._cons2: 
                            del self._cons2[name + "_X"]
                        if name + "_Y" in self._cons2: 
                            del self._cons2[name + "_Y"]
                        continue

                    if min(densityX) < min(densityY): 
                        if densityX[0] < densityX[1]: 
                            self._cons2[name + "_X"] = (self._xs[0, index] <= xs[0, index] - 1)
                            self._ubXs[name] = xs[0, index] - 1
                        else: 
                            self._cons2[name + "_X"] = (self._xs[0, index] >= xs[0, index] + 1)
                            self._lbXs[name] = xs[0, index] + 1
                    else: 
                        if densityY[0] < densityY[1]: 
                            self._cons2[name + "_Y"] = (self._ys[0, index] <= ys[0, index] - 1)
                            self._ubYs[name] = ys[0, index] - 1
                        else: 
                            self._cons2[name + "_Y"] = (self._ys[0, index] >= ys[0, index] + 1)
                            self._lbYs[name] = ys[0, index] + 1
                else: 
                    if name + "_X" in self._cons2: 
                        del self._cons2[name + "_X"]
                    if name + "_Y" in self._cons2: 
                        del self._cons2[name + "_Y"]
                    self._cons2[name + "_X"] = (self._xs[0, index] == xs[0, index])
                    self._cons2[name + "_Y"] = (self._ys[0, index] == ys[0, index])

        if not self._silent: 
            print("")
            print("==================================================")
            # for iter in range(len(results)): 
            #     print("Iteration " + str(iter) + "; Overuse " + str(overuses[iter]) + "; Cost " + str(objectives[iter]))
            #     for name in self._ops: 
            #         index = self._name2index[name]
            #         print(" -> " + name + "\t(" + str(results[iter][0][0, index]) + ", " + str(results[iter][1][0, index]) + ")")
            # print("==================================================")
            lbX = HyperGraph.MAX
            ubX = 0
            lbY = HyperGraph.MAX
            ubY = 0
            for coord in self._grid: 
                if coord[0] < lbX: 
                    lbX = coord[0]
                if coord[0] > ubX: 
                    ubX = coord[0]
                if coord[1] < lbY: 
                    lbY = coord[1]
                if coord[1] > ubY: 
                    ubY = coord[1]
            print("Overuse " + str(overuses[iter]) + "; Cost " + str(objectives[iter]))
            print("\t", end="")
            for idx in range(lbX, ubX+1): 
                print("C(" + str(idx) + ")\t\t", end="")
            print("")
            for idx in range(lbX, ubX+1): 
                print("R(" + str(idx) + ")\t", end="")
                line = ""
                for jdx in range(lbY, ubY+1): 
                    coord = (idx, jdx)
                    if coord in gridOps: 
                        if len(gridOps[coord]) > 0: 
                            ops = ""
                            for op in gridOps[coord]: 
                                ops += op + ","
                            if len(ops) < 8: 
                                ops += "\t"
                            line += ops + "\t"
                        else: 
                            line += "EMPTY\t\t"
                    else: 
                        line += "\t\t"
                print(line)
        
        bestOveruse = HyperGraph.MAX
        bestIter = 0
        for iter in range(len(results)): 
            if overuses[iter] < bestOveruse: 
                bestIter = iter
                bestOveruse = overuses[iter]
        
        if bestOveruse > 0: 
            print("WARNING: Final overuse:", bestOveruse)
            return {}, {}, {}

        # Detailed Placement
        xs = results[bestIter][0]
        ys = results[bestIter][1]
        for name in self._ops: 
            index = self._name2index[name]
            assert self._opList[index] == name
            # if not self._silent: 
            #     print(" -> " + name + "\t(" + str(xs[0, index]) + ", " + str(ys[0, index]) + ")")

        def evaluate(): 
            distXs = []
            distYs = []
            for vname, vertex in self._DFG.vertices().items(): 
                for net in self._DFG.netsOut(vname): 
                    source = net.fr().split(".")[0]
                    sink   = net.to()[0].split(".")[0]
                    if source == sink: 
                        continue
                    index1 = self._name2index[source]
                    assert self._opList[index1] == source
                    index2 = self._name2index[sink]
                    assert self._opList[index2] == sink
                    fu1 = self._compat[source][0] #TODO
                    fu2 = self._compat[sink][0] #TODO
                    distX = abs(xs[0, index1] - xs[0, index2])
                    distY = abs(ys[0, index1] - ys[0, index2])
                    if fu1 == "MEM" or fu2 == "MEM": 
                        distX = 4.0 * distX
                        distY = 1.0
                    if fu1 in ["IO", "INPUT", "OUTPUT"] or fu2 in ["IO", "INPUT", "OUTPUT"]: 
                        distX = 1.0
                        distY = 4.0 * distY
                    distXs.append(distX)
                    distYs.append(distY)
            assert len(distXs) == len(distYs)

            cost = 0.0
            for value in distXs: 
                cost += value
            for value in distYs: 
                cost += value
            return cost
            
        if not self._silent: 
            print("==================================================")

        temper = self._temper
        last = evaluate()
        lastAccepted = 0
        init = last
        for iter in range(AnalyticPlacer.MAXITER): 
            backupX = xs.copy()
            backupY = ys.copy()
            temper = temper * 0.9996

            gridOps = {}
            gridOpCount = {}
            for key, _ in self._grid.items(): 
                gridOps[key] = []
                gridOpCount[key] = {}
            for idx in range(xs.shape[1]): 
                x = xs[0, idx]
                y = ys[0, idx]
                op = self._opList[idx]
                fu = self._compat[op][0] #TODO
                assert (x, y) in gridOps
                gridOps[(x, y)].append(op)
                if not fu in gridOpCount[(x, y)]: 
                    gridOpCount[(x, y)][fu] = 0
                gridOpCount[(x, y)][fu] += 1

            pos = random.randint(0, xs.shape[1] - 1)
            x = xs[0, pos]
            y = ys[0, pos]
            op = self._opList[pos]
            if op in self._fixed: 
                continue
            fu = self._compat[op][0] #TODO
            assert fu in self._fu2coords
            if len(self._fu2coords[fu]) <= 1: 
                print("NOTE:", fu, "has only one candidate position.")
            x2, y2 = self._fu2coords[fu][random.randint(0, len(self._fu2coords[fu]) - 1)]
            while x2 == x and y2 == y: 
                x2, y2 = self._fu2coords[fu][random.randint(0, len(self._fu2coords[fu]) - 1)]
            if not fu in gridOpCount[(x2, y2)] or gridOpCount[(x2, y2)][fu] == 0: 
                xs[0, pos] = x2
                ys[0, pos] = y2
            else: 
                candidates = []
                for op2 in gridOps[(x2, y2)]: 
                    fu2 = self._compat[op2][0] #TODO 
                    if fu2 == fu: 
                        candidates.append(op2)
                assert len(candidates) == gridOpCount[(x2, y2)][fu]
                index = random.randint(0, len(candidates) - 1)
                op2 = candidates[index]
                fu2 = self._compat[op2][0] #TODO 
                pos2 = self._name2index[op2]
                assert self._opList[pos2] == op2
                if op2 in self._fixed: 
                    continue
                xs[0, pos] = x2
                ys[0, pos] = y2
                xs[0, pos2] = x
                ys[0, pos2] = y
            
            cost = evaluate()
            if not self._silent: 
                print("\rIteration:", iter, "; cost:", cost, "vs.", last, "; prob:", str(prob)[0:min(4, len(str(prob)))], "; T =", str(temper)[0:min(4, len(str(temper)))], end="")
            # else: 
            #     print("\rIteration:", iter, "; cost:", cost, "vs.", last, "; prob:", str(prob)[0:min(4, len(str(prob)))], "; T =", str(temper)[0:min(4, len(str(temper)))], end="")
            if cost < last: 
                last = cost
                if not self._silent: 
                    lastAccepted = iter
                    print(" -> Accepted", end="")
            elif cost == last: 
                if random.randint(0, 1) == 0: 
                    last = cost
                    if not self._silent: 
                        lastAccepted = iter
                        print(" -> Accepted", end="")
                else: 
                    xs = backupX
                    ys = backupY
                    if not self._silent: 
                        print(" -> Rejected", end="")
            else: 
                delta = cost - last
                prob = math.exp(-delta / temper)
                if random.random() < prob: 
                    last = cost
                    if not self._silent: 
                        lastAccepted = iter
                        print(" -> Accepted", end="")
                else: 
                    xs = backupX
                    ys = backupY
                    if not self._silent: 
                        print(" -> Rejected", end="")
            
            if iter - lastAccepted > AnalyticPlacer.PATIENCE: 
                break
        if last > init: 
            xs = results[bestIter][0]
            ys = results[bestIter][1]
            # print("\nNo improvement. ")
        for name in self._ops: 
            index = self._name2index[name]
            assert self._opList[index] == name
            x = xs[0, index]
            y = ys[0, index]
            fus = self._gridFUs[(x, y)]
            for fu in fus: 
                if self._fuTypes[fu] in self._compat[name]: 
                    self._placement[name] = fu
                    break
        for vertex in self._DFG.vertices().keys(): 
            splited = vertex.split(".")
            if len(splited) > 1: 
                assert len(splited) == 2
                pos = self._placement[splited[0]] + "." + splited[1]
                self._placement[vertex] = pos

        def getToRoute(): 
            toRoute = []
            for fr in self._DFG.vertices().keys(): 
                for net in self._DFG.netsOut(fr): 
                    for to in net.to(): 
                        frSplited = fr.split(".")
                        toSplited = to.split(".")
                        frFU = self._placement[frSplited[0]]
                        toFU = self._placement[toSplited[0]]
                        frRRG = frFU + "." + frSplited[1] if len(frSplited) > 1 else frFU
                        toRRG = toFU + "." + toSplited[1] if len(toSplited) > 1 else toFU
                        if not (frSplited[0] == to or toSplited[0] == fr): 
                            toRoute.append((frRRG, toRRG))
                        else: 
                            assert len(frSplited) == 1 or len(toSplited) == 1
            return toRoute
        
        if not self._silent: 
            print("")
        conflicts = self._router.route(getToRoute())
        self._routing = {}
        if conflicts == 0: 
            for link, path in self._router.results().items(): 
                self._routing[link] = path
        if not self._silent: 
            print("Routing conflicts:", conflicts)

        return self._placement, self._routing, evaluate()



class AnnealingPlacer: 

    def __init__(self, RRG: HyperGraph, filename: str = "", fixed: dict = {}, patience: int = 1812, temper: float = 0.5, early: int = 512, maxDist: int = 8, silent: bool = False): 
        self._silent = silent
        self._temper = temper
        self._early  = early
        self._patience = patience
        self._maxDist = maxDist
        self._fixed = fixed
        self._RRG = RRG
        self._router = MazeRouter(self._RRG)
        # self._router = CliqueRouter(self._RRG)
        self._placement = {}
        self._routing = {}

        self._coords = {}
        self._types = {}
        self._dmys = {}
        self._mems = {}
        self._ios = {}
        self._categories = {}
        self._grid = {}
        self._gridFUs = {}
        self._fuTypes = {}
        self._fu2coords = {}

        if filename == "": 
            return
        with open(filename, "r") as fin: 
            lines = fin.readlines()
        for line in lines: 
            splited = line.split()
            if len(splited) < 4: 
                continue
            fuName = splited[0]
            fuType = splited[1]
            self._fuTypes[fuName] = fuType
            x, y = int(splited[2]), int(splited[3])
            self._coords[fuName] = (x, y)
            self._types[fuName] = fuType
            if not (x, y) in self._grid: 
                self._grid[(x, y)] = {}
                self._gridFUs[(x, y)] = []
            if not fuType in self._grid[(x, y)]: 
                self._grid[(x, y)][fuType] = 0
            self._grid[(x, y)][fuType] += 1
            self._gridFUs[(x, y)].append(fuName)
            if not fuType in self._fu2coords: 
                self._fu2coords[fuType] = []
            self._fu2coords[fuType].append((x, y))
                
        for name, coord in self._coords.items(): 
            fuType = self._types[name]
            if not fuType in self._categories: 
                self._categories[fuType] = {}
            self._categories[fuType][name] = coord
            if fuType == "DUMMY": 
                self._dmys[name] = coord
            if fuType == "MEM": 
                self._mems[name] = coord
            if fuType in ["IO", "INPUT", "OUTPUT"]: 
                self._ios[name] = coord
    
    def place(self, DFG: HyperGraph, compat: dict, init: dict = {}, fixed: dict = {}): 
        self._DFG = DFG
        self._contracted = HyperGraph()
        self._compat = compat
        self._fixed = fixed
        self._placement = {}
        self._routing = {}
        self._ops = {}
        self._opList = []
        self._numOps = 0
        self._name2index = {}
        for name, vertex in self._DFG.vertices().items(): 
            if len(name.split(".")) == 1: 
                if not name in self._fixed: 
                    self._ops[name] = vertex.attr("optype")
                    self._opList.append(name)
                    self._name2index[name] = len(self._name2index)
                    self._numOps += 1 
                self._contracted.addVertex(name)
        for vname, vertex in self._DFG.vertices().items(): 
            for net in self._DFG.netsOut(vname): 
                source = net.fr().split(".")[0]
                sink   = net.to()[0].split(".")[0]
                if net.fr().split(".")[0] == net.fr() or net.to()[0].split(".")[0] == net.to()[0]: 
                    continue
                self._contracted.addNet([source, sink])
        self._distMat = self._contracted.distMat()

        return self.solve(init)

    def solve(self, init: dict = {}): 
        candidates = {}
        for op in self._opList: 
            if not op in candidates: 
                candidates[op] = []
            for name, vertex in self._RRG.vertices().items(): 
                if vertex.attr("device") in self._compat[op]: 
                    candidates[op].append(name)

        ops = self._opList.copy()
        random.shuffle(ops)
        
        # Initialization
        places = self._fixed.copy()
        used = set()
        count = 0
        for op in ops: 
            pos = random.randint(0, len(candidates[op]) - 1)
            while candidates[op][pos] in used: 
                pos = random.randint(0, len(candidates[op]) - 1)
                count += 1
                if count > 1024: 
                    print("FAILED: Not enough candidates:", op, candidates[op], self._fixed, places)
                    return {}, {}, {}
            places[op] = candidates[op][pos]
            used.add(candidates[op][pos])
        if len(init) > 0: 
            for v1, v2 in init.items(): 
                if len(v1.split(".")) > 1: 
                    continue
                assert v1 in self._fixed or v2 in candidates[v1]
                places[v1] = v2

        def getToRoute(): 
            toRoute = []
            for fr in self._DFG.vertices().keys(): 
                for net in self._DFG.netsOut(fr): 
                    for to in net.to(): 
                        frSplited = fr.split(".")
                        toSplited = to.split(".")
                        frFU = places[frSplited[0]]
                        toFU = places[toSplited[0]]
                        frRRG = frFU + "." + frSplited[1] if len(frSplited) > 1 else frFU
                        toRRG = toFU + "." + toSplited[1] if len(toSplited) > 1 else toFU
                        if not (frSplited[0] == to or toSplited[0] == fr): 
                            toRoute.append((frRRG, toRRG))
                        else: 
                            assert len(frSplited) == 1 or len(toSplited) == 1
            return toRoute
        
        temper = self._temper
        iter = 0
        lastImp = 0
        last = self._router.route(getToRoute())
        if not self._silent: 
            print("Routing conflicts:", last)
        while last > 0: 
            if iter > self._patience: 
                return {}, {}, {}

            backup = places.copy()

            index = random.randint(0, len(self._opList) - 1)
            op = self._opList[index]
            count = 0
            while len(candidates[op]) <= 1: 
                index = random.randint(0, len(self._opList) - 1)
                op = self._opList[index]
                count += 1
                if count > 1024: 
                    print("FAILED: Not enough candidates. ")
                    return {}
            
            op = self._opList[index]
            jndex = -1
            for idx, candidate in enumerate(candidates[op]): 
                if places[op] == candidate: 
                    jndex = idx
                    break
            assert jndex > -1

            kndex = random.randint(0, len(candidates[op]) - 1)
            fu = candidates[op][kndex]
            count = 0
            while jndex == kndex: 
                kndex = random.randint(0, len(candidates[op]) - 1)
                fu = candidates[op][kndex]
                count += 1
                if count > 1024: 
                    print("FAILED: Not enough candidates. ")
                    return {}, {}, {}

            op2 = ""
            fu2 = places[op]
            for name in list(places.keys()): 
                if name != op and places[name] == fu: 
                    op2 = name

            x1, y1 = self._coords[fu]
            x2, y2 = self._coords[fu2]
            if abs(x1 - x2) + abs(y1 - y2) > self._maxDist: 
                places = backup
                continue

            if op2 == "": 
                places[op] = fu
            else: 
                places[op2] = fu2
                places[op] = fu

            conflicts = self._router.route(getToRoute())
            prob = math.exp((last - conflicts) / temper)
            if not self._silent: 
                print("\rIteration:", iter, "; conflicts:", conflicts, "vs.", last, "; prob:", str(prob)[0:min(4, len(str(prob)))], "; T =", str(temper)[0:min(4, len(str(temper)))], end="")
            # else: 
            #     print("\rIteration:", iter, "; conflicts:", conflicts, "vs.", last, "; prob:", str(prob)[0:min(4, len(str(prob)))], "; T =", str(temper)[0:min(4, len(str(temper)))], end="")

            if conflicts < last: 
                lastImp = iter
            elif iter - lastImp > self._early: 
                if not self._silent: 
                    print("FAILED: Early stopping. ")
                return {}, {}, {}
            iter += 1
            temper *= 0.9995

            if conflicts == 0: 
                if not self._silent: 
                    print(" -> OK", end="")
                break
            elif conflicts < last: 
                if not self._silent: 
                    print(" -> Accepted", end="")
                last = conflicts
                continue
            elif conflicts == last: 
                if random.randint(0, 1) == 0: 
                    if not self._silent: 
                        print(" -> Accepted", end="")
                    last = conflicts
                    continue
                else: 
                    if not self._silent: 
                        print(" -> Rejected", end="")
                    places = backup
                    continue
            else: 
                delta = conflicts - last
                if random.random() < math.exp((-delta) / temper): 
                    if not self._silent: 
                        print(" -> Accepted", end="")
                    last = conflicts
                    continue
                else: 
                    if not self._silent: 
                        print(" -> Rejected", end="")
                    places = backup
                    continue

        self._placement = {}
        self._routing = {}
        
        for vertex in self._DFG.vertices(): 
            splited = vertex.split(".")
            fu = places[splited[0]]
            if len(splited) > 1: 
                fu += "." + splited[1]
            self._placement[vertex] = fu

        for link, path in self._router.results().items(): 
            self._routing[link] = path

        # print(utils.dict2str(self._placement))
        # print(utils.dict2str(self._routing))

        cost = 0.0
        if len(self._coords) > 0: 
            distXs = []
            distYs = []
            for vname, vertex in self._DFG.vertices().items(): 
                for net in self._DFG.netsOut(vname): 
                    source = net.fr().split(".")[0]
                    sink   = net.to()[0].split(".")[0]
                    if source == sink: 
                        continue
                    fu1 = self._compat[source][0] #TODO
                    fu2 = self._compat[sink][0] #TODO
                    x1, y1 = self._coords[self._placement[source]]
                    x2, y2 = self._coords[self._placement[sink]]
                    distX = abs(x1 - x2)
                    distY = abs(y1 - y2)
                    if fu1 == "MEM" or fu2 == "MEM": 
                        distX = 4.0 * distX
                        distY = 1.0
                    if fu1 in ["IO", "INPUT", "OUTPUT"] or fu2 in ["IO", "INPUT", "OUTPUT"]: 
                        distX = 1.0
                        distY = 4.0 * distY
                    distXs.append(distX)
                    distYs.append(distY)
            assert len(distXs) == len(distYs)

            for value in distXs: 
                cost += value
            for value in distYs: 
                cost += value
            if not self._silent: 
                print("\nCost:", cost)

        # Validate 
        used = set()
        for vertex in self._DFG.vertices(): 
            if not vertex in self._placement: 
                print("ERROR: Unmapped vertex:", vertex)
            else: 
                if self._placement[vertex] in used: 
                    print("ERROR: Overused RRG FU:", self._placement[vertex])
                else: 
                    used.add(self._placement[vertex])
                    
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                if self._placement[net.fr()] in self._placement[net.to()[0]] or self._placement[net.to()[0]] in self._placement[net.fr()]: 
                    continue
                if not (self._placement[net.fr()], self._placement[net.to()[0]]) in self._routing: 
                    print("ERROR: Unrouted edge:", (self._placement[net.fr()], self._placement[net.to()[0]]))

        for link1, path1 in self._routing.items(): 
            for link2, path2 in self._routing.items(): 
                if link1[0] != link2[0]: 
                    used = set(path1)
                    for vertex in path2: 
                        if vertex in used: 
                            print("ERROR: Overused RRG vertex:", vertex, "in", link1, "and", link2)

        if not self._silent: 
            print("")
        return self._placement, self._routing, cost

        
                


        








