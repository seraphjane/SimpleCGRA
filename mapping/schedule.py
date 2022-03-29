import sys
sys.path.append(".")

import time
import random
import math
import multiprocessing as mp

import networkx as nx
from networkx.algorithms import isomorphism as iso

import common.utils as utils
from common.utils import Base
from common.graph import HyperGraph
from arch.protocols import *
from mapping.place import *

def failed(): 
    return {}, {}, {}

class Scheduler: 
    # Default
    MAXNUM   = 4
    NUMSTATUSES = 32
    NJOBS  = 32
    MAXOPS   = 0.9
    MAXEDGES = 0.6
    FULLNUM  = 1

    # -> 0: Analytic + Annealing
    # -> 1: Annealing
    PLACER = 0

    # -> 0: Sort by vertices
    # -> 1: Sort by vertices + inner distance
    SORTBY = 0

    # Memory additional delay
    MEMDELAY = False
    # MEMDELAY = True

    def __init__(self, RRG, DFG, compat, resfile): 
        self._addThreads = True
        self._RRG = RRG
        self._DFG = DFG
        self._placer1 = AnalyticPlacer(self._RRG, resfile, silent=True, temper=0.25)
        self._placer2 = AnnealingPlacer(self._RRG, resfile, silent=True, patience=1024, temper=0.20, maxDist=2, early=128)
        self._placer3 = AnnealingPlacer(self._RRG, resfile, silent=True)
        # self._placer1 = AnalyticPlacer(self._RRG, resfile, silent=True)
        # self._placer2 = AnnealingPlacer(self._RRG, resfile, silent=True, patience=1024, temper=0.25, early=64, maxDist=2)
        # self._placer3 = AnnealingPlacer(self._RRG, resfile, silent=True, patience=1812, temper=0.25, early=256, maxDist=8)
        self._contracted = HyperGraph()
        self._compat = compat
        self._coords = {}
        self._types = {}
        self._mems = {}
        self._ios = {}
        self._categories = {}
        self._grid = {}
        self._gridFUs = {}
        self._fuTypes = {}
        self._ops = {}
        self._opList = []
        self._numOps = 0
        self._name2index = {}
        self._countFUs = {}

        with open(resfile, "r") as fin: 
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
            if not fuType in self._countFUs: 
                self._countFUs[fuType] = 0
            self._countFUs[fuType] += 1
                
        for name, coord in self._coords.items(): 
            fuType = self._types[name]
            if not fuType in self._categories: 
                self._categories[fuType] = {}
            self._categories[fuType][name] = coord
            if fuType == "MEM": 
                self._mems[name] = coord
            elif fuType in ["INPUT", "OUTPUT", "IO"]: 
                self._ios[name] = coord
        
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
        self._distMatDi = self._contracted.distMatDi()
        self._topoSeq = self._contracted.topologic()
    
    def schedule(self): 
        self._used = {}
        self._placed = []

        def statistics(pack): 
            countFUs = {}
            countAll = 0
            countEdges = 0
            for op in pack: 
                fu = self._compat[op][0] #TODO
                if not fu in countFUs: 
                    countFUs[fu] = 0
                countFUs[fu] += 1
                countAll += 1
                for net in self._contracted.netsOut(op): 
                    for to in net.to(): 
                        if to in pack: 
                            countEdges += 1

            overflow = False
            allFull = True
            fullCount = 0
            for fu, count in countFUs.items(): 
                assert fu in self._countFUs and self._countFUs[fu] > 0
                if count <= int(self._countFUs[fu] * Scheduler.MAXOPS): 
                    allFull = False
                else: 
                    fullCount += 1
                    if count > self._countFUs[fu]: 
                        overflow = True
            if countEdges <= int(len(self._coords) * Scheduler.MAXEDGES): 
                allFull = False
            else: 
                fullCount += 1
                if countEdges > countAll: 
                    overflow = True
            
            return countFUs, countAll, countEdges, overflow, allFull, fullCount

        # Initialization: generate several packs with 1-S seeds
        history = []
        histPlaced = []
        histRouted = []
        MAXII = 64
        ii = 0
        go = True
        while ii < MAXII: 
            if go: 
                topo = HyperGraph.MAX
                for name, index in self._topoSeq.items(): 
                    if not name in self._used and index < topo: 
                        topo = index
                if topo >= HyperGraph.MAX: 
                    assert len(self._used) == len(self._contracted.vertices())
                    break
                possible = []
                for name, index in self._topoSeq.items(): 
                    if index == topo and not name in self._used: 
                        possible.append(name)
                    
                packs = []
                for _ in range(Scheduler.NUMSTATUSES): 
                    seeds = set()
                    num = random.randint(1, min(len(possible), Scheduler.MAXNUM))
                    while len(seeds) < num: 
                        pos = random.randint(0, len(possible) - 1)
                        while possible[pos] in seeds: 
                            pos = random.randint(0, len(possible) - 1)
                        seeds.add(possible[pos])
                    packs.append(seeds)
                
                iter = 0
                updated = True
                while updated: 
                    # print("Iteration:", iter)
                    iter += 1

                    updated = False
                    for idx in range(len(packs)): 
                        # Resource utilization
                        countFUs, countAll, countEdges, overflow, allFull, fullCount = statistics(packs[idx])
                        
                        # print(" -> Pack", idx, "; FUs:", countFUs, "; Edges:", countEdges, "; Full?", allFull or overflow or fullCount > Scheduler.FULLNUM)
                        if allFull or overflow or fullCount > Scheduler.FULLNUM: 
                            print(" -> Invalid Pack", idx, "; FUs:", countFUs, "; Edges:", countEdges, "; Full?", allFull or overflow or fullCount > Scheduler.FULLNUM)
                            continue

                        nexts = set()
                        for vertex in packs[idx]: 
                            for net in self._contracted.netsOut(vertex): 
                                for to in net.to(): 
                                    if not Scheduler.MEMDELAY: 
                                        if not to in packs[idx] and not to in self._used: 
                                            nexts.add(to)
                                    else: 
                                        if not to in packs[idx] and not to in self._used: 
                                            fu = self._compat[to][0] #TODO
                                            if fu != "MEM": 
                                                valid = True
                                                for net in self._contracted.netsIn(to): 
                                                    fr = net.fr()
                                                    frFU = self._compat[fr][0] #TODO
                                                    if frFU == "MEM" and not fr in self._used: 
                                                        valid = False
                                                if valid: 
                                                    nexts.add(to)
                        
                        if len(nexts) == 0: 
                            topoTmp = HyperGraph.MAX
                            for name, index in self._topoSeq.items(): 
                                if not name in self._used and not name in packs[idx] and index < topoTmp: 
                                    topoTmp = index

                            possibleTmp = []
                            for name, index in self._topoSeq.items(): 
                                if not Scheduler.MEMDELAY: 
                                    if index == topoTmp and not name in self._used and not name in packs[idx]: 
                                        possibleTmp.append(name)
                                else: 
                                    if index == topoTmp and not name in self._used and not name in packs[idx]: 
                                        valid = True
                                        for net in self._contracted.netsIn(name): 
                                            fr = net.fr()
                                            frFU = self._compat[fr][0] #TODO
                                            if frFU == "MEM" and not fr in self._used: 
                                                valid = False
                                        if valid: 
                                            possibleTmp.append(name)
                            if len(possibleTmp) > 0: 
                                indexTmp = random.randint(0, len(possibleTmp) - 1)
                                nexts.add(possibleTmp[indexTmp])
                        
                        if len(nexts) > 0: 
                            backup = packs[idx].copy()

                            selected = random.randint(0, len(nexts) - 1)
                            op = list(nexts)[selected]
                            fu = self._compat[op][0] #TODO
                            if not fu in countFUs or countFUs[fu] < self._countFUs[fu]: 
                                packs[idx].add(op)
                            else: 
                                continue

                            added = True
                            prevs = set()
                            while added: 
                                added = False
                                tmp = set(list(prevs) + list(packs[idx]))
                                for vertex in tmp: 
                                    for net in self._contracted.netsIn(vertex): 
                                        if not net.fr() in tmp and not net.fr() in self._used: 
                                            prevs.add(net.fr())
                                            added = True
                                            
                            if len(prevs) > 0: 
                                for prev in prevs: 
                                    packs[idx].add(prev)

                            countFUs, countAll, countEdges, overflow, allFull, fullCount = statistics(packs[idx])

                            if allFull or overflow or fullCount > Scheduler.FULLNUM: 
                                packs[idx] = backup
                            else: 
                                updated = True
                        else: 
                            continue
                
                # Uniquify
                if Scheduler.SORTBY == 0: 
                    packs = sorted(packs, key=lambda x: len(x), reverse=True)
                elif Scheduler.SORTBY == 1: 
                    packs = sorted(packs, key=lambda x: (len(x), self._innerDistance(x)), reverse=True)
                else: 
                    assert 0, "Scheduler.SORTBY"

                updated = True
                strs = []
                for pack in packs: 
                    strs.append(str(sorted(list(pack))))
                
                indices = []
                idx1 = 0 
                idx2 = 0
                while idx1 < len(packs): 
                    while idx2 < len(packs) and strs[idx1] == strs[idx2]: 
                        idx2 += 1
                    indices.append(idx1)
                    idx1 = idx2

                tmp = []
                for index in indices: 
                    tmp.append(packs[index])
                packs = tmp

                pool = mp.Pool(processes=Scheduler.NJOBS)
                processes = []
                tmpgs = []
                valids = []
                placements = []
                routings = []
                costs = []
                for idx in range(len(packs)): 
                    countFUs, countAll, countEdges, overflow, allFull, fullCount = statistics(packs[idx])

                    if allFull or overflow or fullCount > Scheduler.FULLNUM: 
                        continue
                    else: 
                        valids.append(packs[idx])
                        print("Time", ii, "; Packed; FUs:", countFUs, "; Edges:", countEdges, "; Full?", allFull or overflow or fullCount > Scheduler.FULLNUM)
                        print(" -> ", packs[idx])

                    tmpg = HyperGraph()
                    for vertex in packs[idx]: 
                        tmpg.addVertex(vertex)
                    for vertex in self._DFG.vertices(): 
                        splited = vertex.split(".")
                        if splited[0] in packs[idx]: 
                            tmpg.addVertex(vertex)
                    if ii > 0: 
                        assert len(self._placed) == ii
                        for v1, v2 in self._placed[-1].items(): 
                            needed = False
                            for net in self._DFG.netsOut(v1): 
                                for to in net.to(): 
                                    if to.split(".")[0] in packs[idx]: 
                                        needed = True
                                        break
                                if needed: 
                                    break
                            if needed: 
                                tmpg.addVertex(v1.split(".")[0])
                                tmpg.addVertex(v1)
                    for vertex in tmpg.vertices(): 
                        for net in self._DFG.netsOut(vertex): 
                            nodes = [net.fr(), ]
                            for to in net.to():
                                if to in tmpg.vertices(): 
                                    nodes.append(to)
                            if len(nodes) > 1: 
                                tmpg.addNet(nodes)
                    fixed = {}
                    usedFUs = set()
                    if ii > 0: 
                        notok = False
                        # Deal with recurrent connections
                        recurrent = set()
                        for vertex in self._placed[-1]: 
                            if len(vertex.split(".")) == 1: 
                                assert vertex in self._contracted.vertices(), vertex + " not found"
                                for net in self._contracted.netsOut(vertex): 
                                    for to in net.to(): 
                                        if to in self._used and self._distMatDi[self._name2index[to]][self._name2index[vertex]] < HyperGraph.MAX: 
                                            recurrent.add(vertex)
                                            # print(" -> Recurrent connection:", net.fr(), to)
                                            assert vertex in self._placed[-1]
                        # Deal with other connections
                        assert len(self._placed) == ii
                        for v1, v2 in self._placed[-1].items(): 
                            v3 = ""
                            if (v1 in recurrent) or (v1 in tmpg.vertices() and len(v1.split(".")) == 1): 
                                if ".ALU0" in v2 or ".CONST0" in v2 or ".MEM0" in v2 or ".INPUT0" in v2 or ".OUTPUT0" in v2 or ".IO0" in v2: 
                                    v3 = "CGRA0.__" + v2.split(".")[-2]
                                elif ".__" in v2: 
                                    v3 = v2
                                else: 
                                    print("ERROR: Undealt case:", v1, ":", v2)
                                    notok = True
                                    break
                            if len(v3) > 0: 
                                if not v3 in usedFUs: 
                                    fixed[v1] = v3
                                    usedFUs.add(v3)
                                else: 
                                    print("FAILED: Overused FU:", v1, ":", v2, ":", v3)
                                    notok = True
                                    break
                        if notok: 
                            tmpgs.append(tmpg)
                            process = pool.apply_async(failed)
                            processes.append(process)
                            continue

                    tmpgs.append(tmpg)

                    dfg    = tmpg
                    compat = self._compat.copy()
                    for key, value in fixed.items(): 
                        compat[key] = ["DUMMY", ]

                    process = pool.apply_async(self._place, (dfg, compat, fixed))
                    processes.append(process)

                if self._addThreads: 
                    tmpidx = 0
                    while len(valids) < Scheduler.NJOBS: 
                        tmpg = tmpgs[tmpidx]
                        fixed = {}
                        usedFUs = set()
                        if ii > 0: 
                            notok = False
                            # Deal with recurrent connections
                            recurrent = set()
                            for vertex in self._placed[-1]: 
                                if len(vertex.split(".")) == 1: 
                                    assert vertex in self._contracted.vertices(), vertex + " not found"
                                    for net in self._contracted.netsOut(vertex): 
                                        for to in net.to(): 
                                            if to in self._used and self._distMatDi[self._name2index[to]][self._name2index[vertex]] < HyperGraph.MAX: 
                                                recurrent.add(vertex)
                                                # print(" -> Recurrent connection:", net.fr(), to)
                                                assert vertex in self._placed[-1]
                            # Deal with other connections
                            assert len(self._placed) == ii
                            for v1, v2 in self._placed[-1].items(): 
                                v3 = ""
                                if (v1 in recurrent) or (v1 in tmpg.vertices() and len(v1.split(".")) == 1): 
                                    if ".ALU0" in v2 or ".CONST0" in v2 or ".MEM0" in v2 or ".INPUT0" in v2 or ".OUTPUT0" in v2 or ".IO0" in v2: 
                                        v3 = "CGRA0.__" + v2.split(".")[-2]
                                    elif ".__" in v2: 
                                        v3 = v2
                                    else: 
                                        print("ERROR: Undealt case:", v1, ":", v2)
                                        notok = True
                                        break
                                if len(v3) > 0: 
                                    if not v3 in usedFUs: 
                                        fixed[v1] = v3
                                        usedFUs.add(v3)
                                    else: 
                                        print("FAILED: Overused FU:", v1, ":", v2, ":", v3)
                                        notok = True
                                        break
                            if notok: 
                                valids.append(valids[tmpidx])
                                process = pool.apply_async(failed)
                                processes.append(process)
                                tmpidx = (tmpidx + 1) % len(tmpgs)
                                continue
                        dfg    = tmpg
                        compat = self._compat.copy()
                        for key, value in fixed.items(): 
                            compat[key] = ["DUMMY", ]
                        valids.append(valids[tmpidx])
                        process = pool.apply_async(self._place, (dfg, compat, fixed))
                        processes.append(process)
                        tmpidx = (tmpidx + 1) % len(tmpgs)

                pool.close()
                pool.join()

                filtered = []
                for idx in range(len(valids)): 
                    res = processes[idx].get()
                    if len(res[0]) > 0: 
                        filtered.append(valids[idx])
                        placements.append(res[0])
                        routings.append(res[1])
                        costs.append(res[2])
                packs = filtered

                indices = [idx for idx in range(len(packs))]
                if Scheduler.SORTBY == 0: 
                    indices = sorted(indices, key=lambda x: (len(packs[x]), -costs[x]), reverse=True)
                elif Scheduler.SORTBY == 1: 
                    indices = sorted(indices, key=lambda x: (len(packs[x]), self._innerDistance(packs[x]), -costs[x]), reverse=True)
                else: 
                    assert 0, "Scheduler.SORTBY"
                tmp1 = []
                tmp2 = []
                tmp3 = []
                tmp4 = []
                tmp5 = set()
                for index in indices: 
                    info = str(packs[index])
                    if not info in tmp5: 
                        tmp1.append(packs[index])
                        tmp2.append(placements[index])
                        tmp3.append(routings[index])
                        tmp4.append(costs[index])
                        tmp5.add(info)
                packs = tmp1
                placements = tmp2
                routings = tmp3
                costs = tmp4

                for idx in range(len(packs)): 
                    countFUs, countAll, countEdges, overflow, allFull, fullCount = statistics(packs[idx])
                    print("Time", ii, "; Valid Pack", idx, "; FUs:", countFUs, "; Edges:", countEdges)
                
                history.append(packs)
                histPlaced.append(placements)
                histRouted.append(routings)
            else: 
                if len(history) == 0: 
                    print("RE-SCHEDULE: 0")
                    go = True
                    continue

                history = history[:-1]
                histPlaced = histPlaced[:-1]
                histRouted = histRouted[:-1]
                if len(history) == 0: 
                    placed = {}
                    self._placed = []
                    ii = 0
                    print("RE-SCHEDULE: 1")
                    go = True
                    continue
                placed = self._placed[-1]
                self._placed = self._placed[:-1]
                for vertex in placed: 
                    if len(vertex.split(".")) == 1: 
                        self._used[vertex] -= 1
                        if self._used[vertex] == 0: 
                            del self._used[vertex]
                ii -= 1
                skip = False
                while len(history) > 0 and len(history[-1]) == 1:
                    history = history[:-1]
                    histPlaced = histPlaced[:-1]
                    histRouted = histRouted[:-1]
                    if len(history) == 0: 
                        placed = {}
                        self._placed = []
                        ii = 0
                        print("RE-SCHEDULE: 2")
                        go = True
                        skip = True
                        break
                    placed = self._placed[-1]
                    self._placed = self._placed[:-1]
                    for vertex in placed: 
                        if len(vertex.split(".")) == 1: 
                            self._used[vertex] -= 1
                            if self._used[vertex] == 0: 
                                del self._used[vertex]
                    ii -= 1
                if skip: 
                    continue

                assert len(history[-1]) > 1
                history[-1] = history[-1][1:]
                histPlaced[-1] = histPlaced[-1][1:]
                histRouted[-1] = histRouted[-1][1:]
                packs = history[-1]
                placements = histPlaced[-1]
                routings = histRouted[-1]

            if len(packs) == 0: 
                # Rollback
                print(" -> Failed. ")
                if go: 
                    go = False
                else: 
                    pass
            else: 
                placement, routing = placements[0], routings[0]
                assert len(placement) > 0
                countFUs, countAll, countEdges, overflow, allFull, fullCount = statistics(packs[0])
                print("Time", ii, "; Placed Pack; FUs:", countFUs, "; Edges:", countEdges)
                print(" -> ", placement)

                go = True
                ii += 1
                self._placed.append(placement)
                for vertex in placement: 
                    if len(vertex.split(".")) == 1: 
                        if not vertex in self._used: 
                            self._used[vertex] = 0
                        self._used[vertex] += 1
        
        for idx in range(len(self._placed)): 
            print(utils.dict2str(self._placed[idx]))
        print("II:", len(self._placed))
                
        return len(self._placed)
    
    def placed(self): 
        return self._placed

    def _place(self, dfg, compat, fixed): 
        start = time.process_time()
        if Scheduler.PLACER == 0: 
            placement, routing, cost = self._placer1.place(dfg, compat, fixed=fixed)
            if len(placement) > 0: 
                placement, routing, cost = self._placer2.place(dfg, compat, init=placement, fixed=fixed)
            # else: #IMP
            #     placement, routing, cost = self._placer3.place(dfg, compat, fixed=fixed)
        elif Scheduler.PLACER == 1: 
            placement, routing, cost = self._placer3.place(dfg, compat, fixed=fixed)
        else: 
            assert 0, "Scheduler.PLACER"
        if len(placement) > 0: 
            end = time.process_time()
            print("Mapping Time: %.3fs" % (end-start))

        return placement, routing, cost

    def _innerDistance(self, pack): 
        dist = 0.0
        for v1 in pack: 
            for v2 in pack: 
                dist += self._distMat[self._name2index[v1]][self._name2index[v2]]
        return dist / 2
                

