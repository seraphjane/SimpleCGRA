import sys
sys.path.append(".")

import networkx as nx
from networkx.algorithms import isomorphism as iso
from networkx.algorithms import clique

import common.utils as utils
from common.utils import Base
from common.graph import HyperGraph
from arch.protocols import *

class CliqueRouter(Base): 

    MAXNUM = 16
    MAXLEN = 16

    def __init__(self, RRG): 
        self._RRG = RRG
        self._placement = {}
        self._links = {}
        self._paths = {}

    def routeDFG(self, DFG, placement): 
        self._DFG = DFG
        self._placement = placement

        links = []
        for v1, v2 in self._placement.items(): 
            assert v1 in self._DFG.vertices(), v1 + " cannot be found. "
            assert v2 in self._RRG.vertices(), v2 + " cannot be found. "
        for vertex in self._DFG.vertices().keys(): 
            assert vertex in self._placement
            for net in self._DFG.netsOut(vertex): 
                fr = net.fr()
                for to in net.to(): 
                    if not (fr in to or to in fr): 
                        links.append((self._placement[fr], self._placement[to]))
        
        return self.route(links)

    def route(self, links): 
        
        for idx, link in enumerate(links): 
            self._find(link)
            if len(self._links[link]) == 0: 
                # print(" -> Unable to route", link)
                name = link[0] + "->" + link[1] + "--__NONE__"
                self._links[link] = [name, ]
                self._paths[name] = None
                                
        vertices = []
        edges = []
        sources = {}
        sinks = {}
        for idx in range(len(links)): 
            # print(links[idx], ": ", len(paths[idx]))
            assert(len(self._links[links[idx]]) > 0)
            for jdx in range(len(self._links[links[idx]])): 
                name = self._links[links[idx]][jdx]
                vertices.append(name)
                sources[name] = links[idx][0]
                sinks[name]   = links[idx][1]

        addedNets = set()
        for v1 in vertices: 
            for v2 in vertices: 
                if "__NONE__" in v1 or "__NONE__" in v2: 
                    continue
                if sources[v1] == sources[v2]: 
                    if sinks[v1] != sinks[v2]: 
                        if not v1 + "->" + v2 in addedNets and not v2 + "->" + v1 in addedNets: 
                            edges.append([v1, v2])
                            addedNets.add(v1 + "->" + v2)
                else: 
                    conflict = False
                    for vertex1 in self._paths[v1]: 
                        for vertex2 in self._paths[v2]: 
                            if vertex1 == vertex2: 
                                conflict = True
                            if conflict: 
                                break
                        if conflict: 
                            break
                    if not conflict: 
                        if not v1 + "->" + v2 in addedNets and not v2 + "->" + v1 in addedNets: 
                            edges.append([v1, v2])
                            addedNets.add(v1 + "->" + v2)

        graph = nx.Graph()
        graph.add_nodes_from(vertices)
        graph.add_edges_from(edges)

        maxcliq, size = clique.max_weight_clique(graph, weight=None)
        # print(size, "/", len(links))

        self._results = {}
        if size == len(links): 
            for name in maxcliq: 
                source = sources[name]
                sink   = sinks[name]
                self._results[(source, sink)] = self._paths[name]
        
        return len(links) - size
    
    def results(self): 
        return self._results

    def _find(self, link): 
        links = []
        paths = {}

        if link in self._links: 
            tmps = self._links[link]
            for tmp in tmps: 
                paths[tmp] = self._paths[tmp]
            return paths

        que = [[link[0], ], ]
        while len(que) > 0 and len(paths) < CliqueRouter.MAXNUM: 
            curr = que[0]
            tail = curr[-1]
            if len(que) > 1: 
                que = que[1:]
            else: 
                que = []
            for net in self._RRG.netsOut(tail): 
                for to in net.to(): 
                    if self._RRG.vertex(to).attr("type") == "__MODULE_INPUT_PORT__" or \
                        self._RRG.vertex(to).attr("type") == "__MODULE_OUTPUT_PORT__" or \
                        to == link[1]: 
                        tmp = curr + [to, ]
                        if to == link[1]: 
                            name = link[0] + "->" + link[1] + "--" + str(len(paths))
                            links.append(name)
                            paths[name] = tmp
                        elif len(tmp) < CliqueRouter.MAXLEN: 
                            que.append(tmp)

        self._links[link] = links
        for key, value in paths.items(): 
            self._paths[key] = value
        return paths

        
        

class MazeRouter(Base): 

    MAXNUM = 16
    MAXLEN = 16

    def __init__(self, RRG, patience=256): 
        self._RRG = RRG
        self._patience = patience
        self._links = {}
        self._paths = {}
        self._results = {}

    def routeDFG(self, DFG, placement): 
        toRoute = []
        for fr in DFG.vertices().keys(): 
            for net in DFG.netsOut(fr): 
                for to in net.to(): 
                    frSplited = fr.split(".")
                    toSplited = to.split(".")
                    frFU = placement[frSplited[0]]
                    toFU = placement[toSplited[0]]
                    frRRG = frFU + "." + frSplited[1] if len(frSplited) > 1 else frFU
                    toRRG = toFU + "." + toSplited[1] if len(toSplited) > 1 else toFU
                    if not (frSplited[0] == to or toSplited[0] == fr): 
                        toRoute.append((frRRG, toRRG))
                    else: 
                        assert len(frSplited) == 1 or len(toSplited) == 1
        return self.route(toRoute)

    def route(self, links): 
        candidates = {}
        for link in links: 
            paths = self._find(link)
            candidates[link] = sorted(list(paths.keys()), key=lambda x: len(x))

        # Figure out the compatibility of the links
        conflicts = set()
        allLinks = []
        sources = {}
        sinks = {}
        for link in links: 
            if len(self._links[link]) == 0: 
                # print(" -> Unable to route", link)
                name = link[0] + "->" + link[1] + "--__NONE__"
                self._links[link] = [name, ]
                self._paths[name] = None
                allLinks.append(name)
                sources[name] = link[0]
                sinks[name] = link[1]
            for name in self._links[link]: 
                allLinks.append(name)
                sources[name] = link[0]
                sinks[name] = link[1]
        for v1 in allLinks: 
            for v2 in allLinks: 
                if "__NONE__" in v1 or "__NONE__" in v2: 
                    conflicts.add((v1, v2))
                    conflicts.add((v2, v1))
                elif sources[v1] == sources[v2]: 
                    if sinks[v1] == sinks[v2]: 
                        conflicts.add((v1, v2))
                        conflicts.add((v2, v1))
                else: 
                    conflict = False
                    for vertex1 in self._paths[v1]: 
                        for vertex2 in self._paths[v2]: 
                            if vertex1 == vertex2: 
                                conflict = True
                            if conflict: 
                                break
                        if conflict: 
                            break
                    if conflict: 
                        conflicts.add((v1, v2))
                        conflicts.add((v2, v1))

        # Initialization, all links use the first candidates
        status = {}
        for link in links: 
            status[link] = 0

        # Iterations
        self._counts = {}
        def countConflicts(): 
            results = 0
            self._counts = {}
            for key1, value1 in status.items(): 
                assert key1 in self._links, key1 + " not found"
                name1 = self._links[key1][value1]
                self._counts[key1] = 0
                for key2, value2 in status.items(): 
                    assert key2 in self._links, key2 + " not found"
                    name2 = self._links[key2][value2]
                    if name1 != name2 and (name1, name2) in conflicts: 
                        results += 1
                        self._counts[key1] += 1
            return results / 2
        
        failures = 0
        numConflicts = []
        numConflicts.append(countConflicts())
        while numConflicts[-1] > 0 and failures < self._patience: 
            # print(" -> Iteration", failures, "Conflicts", countConflicts())
            failures += 1
            
            seq = sorted(list(status.keys()), key=lambda x: self._counts[x], reverse=True)
            tried = False
            okay1 = False
            for idx, link in enumerate(seq): 
                if status[link] + 1 < len(self._links[link]): 
                    for jdx in range(status[link] + 1, len(self._links[link])): 
                        tmp = 0
                        for link2, kdx in status.items(): 
                            name1 = self._links[link][jdx]
                            name2 = self._links[link2][kdx]
                            if not (name1, name2) in conflicts: 
                                okay1 = True
                                tried = True
                                status[link] = jdx
                                break
                        if okay1: 
                            break
                    if okay1: 
                        break
            if not tried: 
                for idx, link in enumerate(seq): 
                    if status[link] + 1 < len(self._links[link]): 
                        if status[link] + 1 < len(self._links[link]): 
                            tried = True
                            status[link] += 1
                            break
            if not tried: 
                break
            else: 
                numConflicts.append(countConflicts())

        self._results = {}
        if numConflicts[-1] == 0: 
            for link, index in status.items(): 
                self._results[link] = self._paths[self._links[link][index]]
            return 0
        else: 
            return min(numConflicts)
    
    def results(self): 
        return self._results

    def _find(self, link): 
        links = []
        paths = {}

        if link in self._links: 
            tmps = self._links[link]
            for tmp in tmps: 
                paths[tmp] = self._paths[tmp]
            return paths

        que = [[link[0], ], ]
        while len(que) > 0 and len(paths) < CliqueRouter.MAXNUM: 
            curr = que[0]
            tail = curr[-1]
            if len(que) > 1: 
                que = que[1:]
            else: 
                que = []
            for net in self._RRG.netsOut(tail): 
                for to in net.to(): 
                    if self._RRG.vertex(to).attr("type") == "__MODULE_INPUT_PORT__" or \
                        self._RRG.vertex(to).attr("type") == "__MODULE_OUTPUT_PORT__" or \
                        to == link[1]: 
                        tmp = curr + [to, ]
                        if to == link[1]: 
                            name = link[0] + "->" + link[1] + "--" + str(len(paths))
                            links.append(name)
                            paths[name] = tmp
                        elif len(tmp) < CliqueRouter.MAXLEN: 
                            que.append(tmp)

        self._links[link] = links
        for key, value in paths.items(): 
            self._paths[key] = value
        return paths

        


        

