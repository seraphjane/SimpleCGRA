import sys 
sys.path.append(".")

import time
import random
import subprocess as sp

import optuna
import numpy as np 
from sklearn.cluster import SpectralClustering

from common.utils import *
from common.graph import *

def suggestInt(trial:optuna.Trial, numVars:int = 1, fromVal:int = 0, toVal:int = 1, prefix:str = "i"): 
    variables = []
    for idx in range(numVars): 
        variables.append(trial.suggest_int(prefix + "{}".format(idx), fromVal, toVal))
    return variables

def suggestFloat(trial:optuna.Trial, numVars:int = 1, fromVal:float = 0, toVal:float = 1, prefix:str = "f"): 
    variables = []
    for idx in range(numVars): 
        variables.append(trial.suggest_float(prefix + "{}".format(idx), fromVal, toVal))
    return variables

class BOPart: 
    def __init__(self, DFG:HyperGraph, compat:dict, RRG:HyperGraph, FUs:dict, minWays:int = 2, maxWays:int = 2, scheme:str = "random"): 
        self._DFG     = DFG
        self._compat  = compat
        self._RRG     = RRG
        self._FUs     = FUs
        self._minWays = minWays
        self._maxWays = maxWays
        self._scheme  = scheme
        self._opsDFG  = []
        for vertex in self._DFG.vertices(): 
            if getPrefix(vertex) == vertex: 
                self._opsDFG.append(vertex)
        self._coarseDFG = HyperGraph()
        for vertex in self._opsDFG: 
            self._coarseDFG.addVertex(vertex)
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                tmp = [getPrefix(net.fr()), ]
                for sink in net.to(): 
                    if getPrefix(sink) == getPrefix(net.fr()) and \
                       (getPrefix(sink) == sink or getPrefix(net.fr()) == net.fr()): 
                        continue
                    tmp.append(getPrefix(sink))
                if len(tmp) > 1: 
                    self._coarseDFG.addNet(tmp)
        self._initPartition = []
        self.initialize(self._scheme)
        self._partition = self._initPartition
        self._subgraphs = HyperGraph()
        self._subcompats = []
        self.getSubgraphs(self._partition)

    def initialize(self, scheme = "random"): 
        if scheme == "random": 
            for idx in range(len(self._opsDFG)): 
                self._initPartition.append(random.randint(0, self._maxWays-1))
        elif scheme == "spectral": 
            names, adjMat = self._coarseDFG.getMatrix()
            name2index = {}
            for idx in range(len(names)): 
                name2index[names[idx]] = idx
            solver = SpectralClustering(n_clusters=self._maxWays, n_init=64, affinity='precomputed')
            clustered = solver.fit_predict(adjMat)
            name2cluster = {}
            for idx in range(len(clustered)): 
                index = clustered[idx]
                name2cluster[names[idx]] = index
            self._initPartition = []
            for vertex in self._opsDFG: 
                self._initPartition.append(name2cluster[vertex])

    def subgraphs(self): 
        return self._subgraphs

    def subcompats(self): 
        return self._subcompats

    def names(self): 
        return self._opsDFG

    def coarse(self): 
        return self._coarseDFG

    def getClusters(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        names = self.names()
        name2cluster = {}
        for idx in range(len(partition)): 
            index = partition[idx]
            name2cluster[names[idx]] = index
        return name2cluster

    def getSubgraphs(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        self._subgraphs = []
        self._subcompats = []
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        name2cluster = self.getClusters(partition)
        for idx in range(numClusters): 
            self._subgraphs.append(HyperGraph())
        self._subcompats = [{} for _ in range(len(self._subgraphs))]
        for vertex in self._DFG.vertices(): 
            opName = getPrefix(vertex)
            index = name2cluster[opName]
            self._subgraphs[index].addVertex(vertex, self._DFG.vertex(vertex).attrs())
            if not opName in self._subcompats[index]: 
                self._subcompats[index][opName] = self._compat[opName]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cluster = name2cluster[getPrefix(net.fr())]
                okay = True
                for sink in net.to(): 
                    if name2cluster[getPrefix(sink)] != cluster: 
                        okay = False
                        break
                if okay: 
                    self._subgraphs[cluster].addNet(net.nodes())
        return self._subgraphs

    def getExtendedSubgraphs(self, partition=None): 
        name2cluster = self.getClusters(partition)
        self._subgraphs = self.getSubgraphs(self._partition)
        insertedInputs = [set() for _ in range(len(self._subgraphs))]
        insertedOutputs = [set() for _ in range(len(self._subgraphs))]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cut = False
                cluster = name2cluster[getPrefix(net.fr())]
                for sink in net.to(): 
                    sinkCluster = name2cluster[getPrefix(sink)]
                    if sinkCluster != cluster: 
                        cut = True
                    break
                if cut: 
                    insertedOutputs[cluster].add(net.fr())
                    for sink in net.to(): 
                        sinkCluster = name2cluster[getPrefix(sink)]
                        insertedInputs[sinkCluster].add(net.fr())
        
        for idx, inputs in enumerate(insertedInputs): 
            originalVertices = list(self._subgraphs[idx].vertices().keys())
            for elem in inputs: 
                nameLoad = "load_" + "_".join(elem.split("."))
                self._subgraphs[idx].addVertex(nameLoad + ".in0")
                self._subgraphs[idx].addVertex(nameLoad)
                self._subgraphs[idx].addVertex(nameLoad + ".out0")
                self._subgraphs[idx].addNet([nameLoad + ".in0", nameLoad])
                self._subgraphs[idx].addNet([nameLoad, nameLoad + ".out0"])
                self._subcompats[idx][nameLoad] = ["MEM", ]
                for vertex in originalVertices: 
                    for net in self._DFG.netsIn(vertex): 
                        if net.fr() == elem: 
                            self._subgraphs[idx].addNet([nameLoad + ".out0", vertex])
        
        for idx, outputs in enumerate(insertedOutputs): 
            originalVertices = list(self._subgraphs[idx].vertices().keys())
            for elem in outputs: 
                nameStore = "store_" + "_".join(elem.split("."))
                self._subgraphs[idx].addVertex(nameStore + ".in0")
                self._subgraphs[idx].addVertex(nameStore + ".in1")
                self._subgraphs[idx].addVertex(nameStore)
                self._subgraphs[idx].addVertex(nameStore + ".out0")
                self._subgraphs[idx].addNet([nameStore + ".in0", nameStore])
                self._subgraphs[idx].addNet([nameStore + ".in1", nameStore])
                self._subgraphs[idx].addNet([nameStore, nameStore + ".out0"])
                self._subgraphs[idx].addNet([elem, nameStore + ".in0"])
                self._subcompats[idx][nameStore] = ["mem_unit", ]
        
        return self._subgraphs

    def cutMatLegacy(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        self._subgraphs = self.getSubgraphs(self._partition)
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        name2cluster = self.getClusters(partition)
        cutMat = [[0 for _ in range(numClusters)] for _ in range(numClusters)]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cluster = name2cluster[getPrefix(net.fr())]
                for sink in net.to(): 
                    sinkCluster = name2cluster[getPrefix(sink)]
                    if sinkCluster != cluster: 
                        cutMat[cluster][sinkCluster] += 1
        return cutMat

    def cutMat(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        self._subgraphs = self.getSubgraphs(self._partition)
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        name2cluster = self.getClusters(partition)
        cutVertices = [[set() for _ in range(numClusters)] for _ in range(numClusters)]
        cutMat = [[0 for _ in range(numClusters)] for _ in range(numClusters)]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cluster = name2cluster[getPrefix(net.fr())]
                for sink in net.to(): 
                    sinkCluster = name2cluster[getPrefix(sink)]
                    if sinkCluster != cluster: 
                        cutVertices[cluster][sinkCluster].add(net.fr())
                        # cutMat[cluster][sinkCluster] += 1
        for idx in range(numClusters): 
            for jdx in range(numClusters): 
                cutMat[idx][jdx] = len(cutVertices[idx][jdx])
        return cutMat

    def cutLegacy(self, partition=None): 
        return np.sum(self.cutMatLegacy(partition))

    def cut(self, partition=None): 
        return np.sum(self.cutMat(partition))

    def balance(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        self._subgraphs = self.getSubgraphs(self._partition)
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        count = [0 for _ in range(numClusters)]
        for elem in partition: 
            count[elem] += 1
        return max(count) - min(count)

    def cutBalance(self, partition=None): 
        cutMat = np.array(self.cutMat(partition))
        if cutMat.shape[0] <= 2: 
            return 0
        return cutMat.max()

    # def validity(self, partition=None): 
    #     count = 0
    #     mat = self.cutMat(partition)
    #     for idx in range(len(mat)): 
    #         for jdx in range(len(mat[idx])): 
    #             if mat[idx][jdx] > 0 and mat[jdx][idx] > 0: 
    #                 count += mat[idx][jdx] + mat[jdx][idx]
    #     return count

    def validity(self, partition=None): 
        mat = self.cutMat(partition)
        que = []
        cycles = set()
        for idx in range(len(mat)): 
            que.append([idx, ])
        while len(que) > 0: 
            tmp = que[0]
            que = que[1:]
            for jdx, value in enumerate(mat[tmp[-1]]): 
                if value > 0: 
                    if jdx == tmp[0]: 
                        cycles.add(str(tmp + [jdx, ]))
                    elif not jdx in tmp: 
                        que.append(tmp + [jdx, ])
        return len(cycles)

    def cost(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        self._subgraphs = self.getSubgraphs(self._partition)

class BOPartC: 
    def __init__(self, DFG:HyperGraph, compat:dict, RRG:HyperGraph, FUs:dict, minWays:int = 2, maxWays:int = 2, scheme:str = "random"): 
        self._DFG     = DFG
        self._compat  = compat
        self._RRG     = RRG
        self._FUs     = FUs
        self._minWays = minWays
        self._maxWays = maxWays
        self._scheme  = scheme
        self._opsDFG  = []
        for vertex in self._DFG.vertices(): 
            if getPrefix(vertex) == vertex: 
                self._opsDFG.append(vertex)
        self._coarseDFG = HyperGraph()
        for vertex in self._opsDFG: 
            self._coarseDFG.addVertex(vertex)
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                tmp = [getPrefix(net.fr()), ]
                for sink in net.to(): 
                    if getPrefix(sink) == getPrefix(net.fr()) and \
                       (getPrefix(sink) == sink or getPrefix(net.fr()) == net.fr()): 
                        continue
                    tmp.append(getPrefix(sink))
                if len(tmp) > 1: 
                    self._coarseDFG.addNet(tmp)
        self._packedDFG = HyperGraph()
        self.getPackedGraph()
        self._opsPacked = []
        for vertex in self._packedDFG.vertices(): 
            self._opsPacked.append(vertex)
        self._initPartition = []
        self.initialize(self._scheme)
        self._partition = self._initPartition
        self._partitionFinal = self.unfold(self._partition)
        self._subgraphs = HyperGraph()
        self._subcompats = []
        self.getSubgraphs(self._partition)

    def initialize(self, scheme = "random"): 
        if scheme == "random": 
            for idx in range(len(self._opsPacked)): 
                self._initPartition.append(random.randint(0, self._maxWays-1))
        elif scheme == "spectral": 
            names, adjMat = self._packedDFG.getMatrix()
            name2index = {}
            for idx in range(len(names)): 
                name2index[names[idx]] = idx
            solver = SpectralClustering(n_clusters=self._maxWays, n_init=64, affinity='precomputed')
            clustered = solver.fit_predict(adjMat)
            name2cluster = {}
            for idx in range(len(clustered)): 
                index = clustered[idx]
                name2cluster[names[idx]] = index
            self._initPartition = []
            for vertex in self._opsPacked: 
                self._initPartition.append(name2cluster[vertex])

    def subgraphs(self): 
        return self._subgraphs

    def subcompats(self): 
        return self._subcompats

    def names(self): 
        return self._opsDFG

    def namesPacked(self): 
        return self._opsPacked

    def coarse(self): 
        return self._coarseDFG

    def getPackedGraph(self): 
        topoOriginal = self._coarseDFG.topologic()
        indexOriginal = {}
        for idx, elem in enumerate(topoOriginal): 
            indexOriginal[elem] = idx
        index = {}       # need update
        vertices = set() # need update
        packs = {}       # need update
        vertex2pack = {} # need update
        for elem in topoOriginal: 
            name = "pack_" + str(len(packs))
            index[name] = indexOriginal[elem]
            packs[name] = set([elem, ])
            vertices.add(name)
            vertex2pack[elem] = name
        while True: 
            packed = False
            for elem in sorted(list(index.keys()), key = lambda x: index[x]): 
                inCut = 0
                outCut = 0
                toMerge = set()
                for vertex in packs[elem]: 
                    for net in self._coarseDFG.netsIn(vertex): 
                        if not net.fr() in packs[elem]: 
                            inCut += 1
                    for net in self._coarseDFG.netsOut(vertex): 
                        for sink in net.to(): 
                            if not sink in packs[elem]: 
                                outCut += 1
                                toMerge.add(sink)
                                break
                nextInCut = -1
                nextOutCut = -1
                if outCut == 1: 
                    nextV = self._coarseDFG.netsOut(vertex)[0].to()[0]
                    nextPack = vertex2pack[nextV]
                    nextInCut = 0
                    nextOutCut = 0
                    for vertex in packs[nextPack]: 
                        for net in self._coarseDFG.netsIn(vertex): 
                            if not net.fr() in packs[nextPack]: 
                                nextInCut += 1
                        for net in self._coarseDFG.netsOut(vertex): 
                            for sink in net.to(): 
                                if not sink in packs[nextPack]: 
                                    nextOutCut += 1
                                    break
                if ((inCut == 0 or inCut == 1) and (outCut == 1 and len(toMerge) == 1)) or False: 
                # if (inCut == 0 and outCut == 1) or (outCut == 1 and nextInCut == 1 and nextOutCut <= 2): 
                # if (outCut == 1 and nextInCut == 1): 
                # if False: 
                    pack = set(packs[elem])
                    packsToDel = set([elem, ])
                    for vertex in toMerge: 
                        packsToDel.add(vertex2pack[vertex])
                        for subvertex in packs[vertex2pack[vertex]]: 
                            pack.add(subvertex)
                    name = "pack_" + str(len(packs))
                    # index, vertices, packs, vertex2pack  # need update
                    for name in packsToDel: 
                        del index[name]
                        vertices.remove(name)
                    index[name] = min(map(lambda x: indexOriginal[x], pack))
                    vertices.add(name)
                    packs[name] = pack
                    for vertex in pack: 
                        vertex2pack[vertex] = name
                    packed = True
                    break
            if not packed: 
                break
        
        self._packedDFG = HyperGraph()
        for vertex in vertices: 
            self._packedDFG.addVertex(vertex, attrs = {"contents": packs[vertex], })
        for vertex in vertices: 
            for elem in packs[vertex]: 
                for net in self._coarseDFG.netsOut(elem): 
                    nodes = [vertex, ]
                    sinks = set()
                    for sink in net.to(): 
                        if not sink in packs[vertex]: 
                            sinks.add(vertex2pack[sink])
                    if len(sinks) > 0:
                        nodes.extend(list(sinks))
                        self._packedDFG.addNet(nodes)
        
        # print(self._packedDFG.info())
        return self._packedDFG 
    
    def packedDFG(self): 
        return self._packedDFG

    def unfold(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self._partition = partition
        self._partitionFinal = []
        vertex2cluster = {}
        for idx, pack in enumerate(self._opsPacked): 
            contents = self._packedDFG.vertex(pack).attr("contents")
            for elem in contents: 
                vertex2cluster[elem] = self._partition[idx]
        for vertex in self._opsDFG: 
            self._partitionFinal.append(vertex2cluster[vertex])
        return self._partitionFinal

    def partitionFinal(self, partition=None): 
        self.unfold(partition)
        return self._partitionFinal

    def getClusters(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        if len(partition) == len(self._opsPacked): 
            self.unfold(partition)
        else: 
            self._partitionFinal = partition
        names = self.names()
        name2cluster = {}
        for idx in range(len(self._partitionFinal)): 
            index = self._partitionFinal[idx]
            name2cluster[names[idx]] = index
        return name2cluster

    def getSubgraphs(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        if len(partition) == len(self._opsPacked): 
            self.unfold(partition)
        else: 
            self._partitionFinal = partition
        name2cluster = self.getClusters(partition)
        self._subgraphs = []
        self._subcompats = []
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        for idx in range(numClusters): 
            self._subgraphs.append(HyperGraph())
        self._subcompats = [{} for _ in range(len(self._subgraphs))]
        for vertex in self._DFG.vertices(): 
            opName = getPrefix(vertex)
            index = name2cluster[opName]
            self._subgraphs[index].addVertex(vertex, self._DFG.vertex(vertex).attrs())
            if not opName in self._subcompats[index]: 
                self._subcompats[index][opName] = self._compat[opName]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cluster = name2cluster[getPrefix(net.fr())]
                okay = True
                for sink in net.to(): 
                    if name2cluster[getPrefix(sink)] != cluster: 
                        okay = False
                        break
                if okay: 
                    self._subgraphs[cluster].addNet(net.nodes())
        return self._subgraphs

    def getExtendedSubgraphs(self, partition=None): 
        name2cluster = self.getClusters(partition)
        self._subgraphs = self.getSubgraphs(partition)
        insertedInputs = [set() for _ in range(len(self._subgraphs))]
        insertedOutputs = [set() for _ in range(len(self._subgraphs))]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cut = False
                cluster = name2cluster[getPrefix(net.fr())]
                for sink in net.to(): 
                    sinkCluster = name2cluster[getPrefix(sink)]
                    if sinkCluster != cluster: 
                        cut = True
                    break
                if cut: 
                    insertedOutputs[cluster].add(net.fr())
                    for sink in net.to(): 
                        sinkCluster = name2cluster[getPrefix(sink)]
                        insertedInputs[sinkCluster].add(net.fr())
        
        for idx, inputs in enumerate(insertedInputs): 
            originalVertices = list(self._subgraphs[idx].vertices().keys())
            for elem in inputs: 
                nameLoad = "load_" + "_".join(elem.split("."))
                self._subgraphs[idx].addVertex(nameLoad + ".in0")
                self._subgraphs[idx].addVertex(nameLoad)
                self._subgraphs[idx].addVertex(nameLoad + ".out0")
                self._subgraphs[idx].addNet([nameLoad + ".in0", nameLoad])
                self._subgraphs[idx].addNet([nameLoad, nameLoad + ".out0"])
                self._subcompats[idx][nameLoad] = ["MEM", ]
                for vertex in originalVertices: 
                    for net in self._DFG.netsIn(vertex): 
                        if net.fr() == elem: 
                            self._subgraphs[idx].addNet([nameLoad + ".out0", vertex])
        
        for idx, outputs in enumerate(insertedOutputs): 
            originalVertices = list(self._subgraphs[idx].vertices().keys())
            for elem in outputs: 
                nameStore = "store_" + "_".join(elem.split("."))
                self._subgraphs[idx].addVertex(nameStore + ".in0")
                self._subgraphs[idx].addVertex(nameStore + ".in1")
                self._subgraphs[idx].addVertex(nameStore)
                self._subgraphs[idx].addVertex(nameStore + ".out0")
                self._subgraphs[idx].addNet([nameStore + ".in0", nameStore])
                self._subgraphs[idx].addNet([nameStore + ".in1", nameStore])
                self._subgraphs[idx].addNet([nameStore, nameStore + ".out0"])
                self._subgraphs[idx].addNet([elem, nameStore + ".in0"])
                self._subcompats[idx][nameStore] = ["MEM", ]
        
        return self._subgraphs

    def cutMatLegacy(self, partition=None): 
        self.unfold(partition)
        self._subgraphs = self.getSubgraphs(partition)
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        name2cluster = self.getClusters(partition)
        cutMat = [[0 for _ in range(numClusters)] for _ in range(numClusters)]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cluster = name2cluster[getPrefix(net.fr())]
                for sink in net.to(): 
                    sinkCluster = name2cluster[getPrefix(sink)]
                    if sinkCluster != cluster: 
                        cutMat[cluster][sinkCluster] += 1
        return cutMat

    def cutMat(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self.unfold(partition)
        self._subgraphs = self.getSubgraphs(partition)
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        name2cluster = self.getClusters(partition)
        cutVertices = [[set() for _ in range(numClusters)] for _ in range(numClusters)]
        cutMat = [[0 for _ in range(numClusters)] for _ in range(numClusters)]
        for vertex in self._DFG.vertices(): 
            for net in self._DFG.netsOut(vertex): 
                cluster = name2cluster[getPrefix(net.fr())]
                for sink in net.to(): 
                    sinkCluster = name2cluster[getPrefix(sink)]
                    if sinkCluster != cluster: 
                        cutVertices[cluster][sinkCluster].add(net.fr())
                        # cutMat[cluster][sinkCluster] += 1
        for idx in range(numClusters): 
            for jdx in range(numClusters): 
                cutMat[idx][jdx] = len(cutVertices[idx][jdx])
        return cutMat

    def cutLegacy(self, partition=None): 
        return np.sum(self.cutMatLegacy(partition))

    def cut(self, partition=None): 
        return np.sum(self.cutMat(partition))

    def invalidCycles(self, partition=None): 
        cutMat = self.cutMat(partition)
        

    def balance(self, partition=None): 
        if partition is None: 
            partition = self._initPartition
        self.unfold(partition)
        self._subgraphs = self.getSubgraphs(partition)
        maxGroupID = 0
        for groupID in partition: 
            if groupID > maxGroupID: 
                maxGroupID = groupID
        numClusters = max(maxGroupID + 1, self._minWays)
        count = [0 for _ in range(numClusters)]
        for elem in self._partitionFinal: 
            count[elem] += 1
        return max(count) - min(count)

    def cutBalance(self, partition=None): 
        cutMat = np.array(self.cutMat(partition))
        if cutMat.shape[0] <= 2: 
            return 0
        return cutMat.max()

    # for 2-way partition
    # def validity(self, partition=None): 
    #     count = 0
    #     mat = self.cutMat(partition)
    #     for idx in range(len(mat)): 
    #         for jdx in range(len(mat[idx])): 
    #             if mat[idx][jdx] > 0 and mat[jdx][idx] > 0: 
    #                 count += mat[idx][jdx] + mat[jdx][idx]
    #     return count

    def validity(self, partition=None): 
        mat = self.cutMat(partition)
        que = []
        cycles = set()
        for idx in range(len(mat)): 
            que.append([idx, ])
        while len(que) > 0: 
            tmp = que[0]
            que = que[1:]
            for jdx, value in enumerate(mat[tmp[-1]]): 
                if value > 0: 
                    if jdx == tmp[0]: 
                        cycles.add(str(tmp + [jdx, ]))
                    elif not jdx in tmp: 
                        que.append(tmp + [jdx, ])
        return len(cycles)

    def cost(self, partition=None): 
        self.unfold(partition)
        self._subgraphs = self.getSubgraphs(self._partition)

def dominate(a, b): 
    assert len(a) == len(b)
    domin = True
    for idx in range(len(a)): 
        if a[idx] > b[idx]: 
            domin = False
            break
    return domin

def newParetoSet(paretoParams, paretoValues, newParams, newValue): 
    assert len(paretoParams) == len(paretoValues)
    dupli = False
    removed = set()
    indices = []
    for idx, elem in enumerate(paretoValues): 
        if str(paretoParams[idx]) == str(newParams): 
            dupli = True
            break
        if dominate(newValue, elem): 
            removed.add(idx)
    if dupli: 
        return paretoParams, paretoValues
    for idx, elem in enumerate(paretoValues): 
        if not idx in removed: 
            indices.append(idx)
    newParetoParams = []
    newParetoValues = []
    for index in indices: 
        newParetoParams.append(paretoParams[index])
        newParetoValues.append(paretoValues[index])
    bedominated = False
    for idx, elem in enumerate(newParetoValues): 
        if dominate(elem, newValue): 
            bedominated = True
    if len(removed) > 0:
        assert not bedominated
    if len(removed) > 0 or len(paretoParams) == 0 or not bedominated: 
        newParetoParams.append(newParams)
        newParetoValues.append(newValue)
    return newParetoParams, newParetoValues

if __name__ == "__main__": 
#===========================================================================
    NumPart = 2

    pathDFG = "./benchmark/partition/matmul/matmul_DFG.txt"
    pathCompat = "./benchmark/partition/matmul/matmul_compat.txt"
    pathRRG = "./arch/ADRES.txt"
    pathFUs = "./arch/ADRES_FUs.txt"

    if len(sys.argv) >= 3: 
        pathDFG = sys.argv[1]
        pathCompat = sys.argv[2]
    if len(sys.argv) >= 4: 
        NumPart = max(2, int(sys.argv[3]))
    postfixDFG = pathDFG.split("/")[-1]
    postfixCompat = pathCompat.split("/")[-1]

    dfg = HyperGraph(pathDFG)
    rrg = HyperGraph(pathRRG)
    compat = readCompat(pathCompat)
    fus = readFUs(pathFUs)
    part = BOPartC(dfg, compat, rrg, fus, minWays = NumPart, maxWays = NumPart, scheme = "spectral")

    costs = []
    paretoParams = []
    paretoValues = []
    used = set()
    def objective(trial:optuna.Trial): 
        global paretoParams, paretoValues, costs
        var = suggestInt(trial, numVars = len(part.namesPacked()), fromVal = 0, toVal = NumPart - 1, prefix = "i")
        valid = part.validity(var)
        cut = part.cut(var)
        bal = part.balance(var)
        cutbal = part.cutBalance(var)
        objs = [1.0 * cut + 100.0 * valid, 1.0 * bal + 100.0 * valid, cutbal + 100.0 * valid]
        paretoParams, paretoValues = newParetoSet(paretoParams, paretoValues, var, objs)
        cost =  1.0 * cut + 0.2 * bal + 0.5 * cutbal + 100.0 * valid
        costs.append(cost)
        return cost

    sampler = optuna.samplers.NSGAIISampler()
    optimizer = optuna.create_study(sampler = sampler, directions = ["minimize", ])
    optimizer.optimize(objective, n_trials=2 ** 11, show_progress_bar=True)
    print(optimizer.best_params)
    print(optimizer.best_value)
    keys = list(optimizer.best_params.keys())
    values = list(optimizer.best_params.values())
    print(keys)
    print(values)
    print("Cut:",     part.cut(values), \
          "Balance:", part.balance(values))
        
    for idx, param in enumerate(paretoParams): 
        print("Pareto Optimal Trial:", param, "; Final:", part.partitionFinal(param), "; Cost:", paretoValues[idx])

    partition = part.partitionFinal(list(optimizer.best_params.values()))
    subgraphs = part.getExtendedSubgraphs(partition)
    subcompats = part.subcompats()
    print("Cut Matrix:", part.cutMat(partition))
    print("Cut:", part.cut(partition), "; Balance:", part.balance(partition))
    for idx, subgraph in enumerate(subgraphs): 
        subgraph.dump("./tmp/" + postfixDFG[:-4] + "_" + str(idx) + "_DFG.txt")
    for idx, subcompat in enumerate(subcompats): 
        dumpCompat(subcompat, "./tmp/" + postfixCompat[:-4] + "_" + str(idx) + "_compat.txt")