import sys 
sys.path.append(".")

import xmltodict
import json
import networkx as nx
from networkx.algorithms import isomorphism as iso

import common.utils as utils
from common.utils import Base
from common.graph import HyperGraph
from arch.protocols import *

class IsoMatcher(Base): 
    def __init__(self, graph, units): 
        self._original = graph
        self._units    = units
        self._patterns = {}
        self._matched  = []
        self._map      = {}
        self._graph    = HyperGraph()
        self._compat   = {}

    def match(self): 
        for uname, unit in self._units.items(): 
            self._patterns[uname] = {}
            for pname, patt in unit.patterns().items(): 
                self._patterns[uname][pname] = patt.graph()
                # print("Pattern: " + uname + "." + pname)
                # print(self._patterns[uname][pname].info())
                # print("Matching: " + uname + "." + pname)
                g1 = self._original.toNX()
                g2 = self._patterns[uname][pname].toNX()
                matcher = iso.DiGraphMatcher(g1, g2, lambda x, y: x["attrs"]["function"] == y["attrs"]["function"])
                # print(matcher.subgraph_is_isomorphic())
                isomorphisms = matcher.subgraph_isomorphisms_iter()
                for match in isomorphisms: 
                    self._matched.append((uname, pname, match, ))
                    # print(match)
        self._matched.sort(key=lambda x: (len(x[2]), -len(self._units[x[0]].patterns())), reverse=True)
        # print(self._original.info())
        # print(utils.list2str(self._matched))

        def calcValue(pack): 
            used = set()
            for match in pack: 
                for elem in match[2]: 
                    used.add(elem)
            return len(used)

        # print("Matched: ", len(self._matched))
        # print("Destination: ", len(self._original.vertices()))
        states = [[] for _ in range(len(self._matched))]
        for idx in range(len(self._matched)): 
            for jdx in range(len(states) - 1, 0, -1): 
                valueCurrent  = calcValue(states[jdx])
                stateNew      = states[jdx - 1] + [self._matched[idx], ]
                valueNew      = calcValue(stateNew)
                if valueCurrent < valueNew and len(stateNew) == jdx: 
                    # print("Substitute:", valueCurrent, "vs.", valueNew)
                    states[jdx] = stateNew
            # print(utils.list2str(states))
            # print("====================================================")
        states = sorted(states, key = lambda x: (calcValue(x), -len(x)), reverse = True)
        # values = list(map(lambda x: calcValue(x), states))
        # print(utils.list2str(values))
        # print(utils.list2str(states))
        result = states[0]
        if calcValue(result) < len(self._original.vertices()): 
            print("IsoMatcher: FAILED. Cannot match all vertices. ")
            return

        used = set()
        for match in result: 
            uname = match[0]
            pname = match[1]
            info  = match[2]
            duplicated = False
            for v1, v2 in info.items(): 
                if v1 in used: 
                    duplicated = True
                    break
            assert not duplicated, "IsoMatcher: FAILED. Duplicated match. "
            for v1, v2 in info.items(): 
                used.add(v1)

            vertexName = ""
            for v1, v2 in info.items(): 
                if not "." in v1: 
                    vertexName += v1 + "_"
            vertexName = vertexName[:-1]
            self._graph.addVertex(vertexName, {"unit": uname, "pattern": pname})
            if not vertexName in self._compat: 
                self._compat[vertexName] = set()
            self._compat[vertexName].add(uname)
            for v1, v2 in info.items(): 
                portName = ""
                portType = ""
                for key, value in self._units[uname].pattern(pname).portMap().items(): 
                    if value == v2: 
                        portName = key
                        if portName in self._units[uname].inputs(): 
                            portType = "input"
                        elif portName in self._units[uname].outputs(): 
                            portType = "output"
                        else: 
                            assert portName in self._units[uname].inputs() or portName in self._units[uname].outputs(), "IsoMatcher: Invalid port: " + portName + " of " + uname
                if portName != "": 
                    temp = portName
                    portName = vertexName + "." + portName
                    self._graph.addVertex(portName, {"unit": uname + "." + temp})
                    self._map[v1] = portName
                    if portType == "input": 
                        self._graph.addNet([portName, vertexName], {})
                    elif portType == "output": 
                        self._graph.addNet([vertexName, portName], {})
        # print(utils.dict2str(self._map))

        if len(used) < len(self._original.vertices()): 
            print("IsoMatcher: FAILED. ")
            return

        for vname, vertex in self._original.vertices().items(): 
            if vname in self._map: 
                for edge in self._original.netsOut()[vname]: 
                    nodes = [self._map[edge.fr()], ]
                    for node in edge.to(): 
                        if node in self._map: 
                            nodes.append(self._map[node])
                    if len(nodes) > 1: 
                        self._graph.addNet(nodes, {})


    def graph(self): 
        return self._graph

    def graphInfo(self): 
        return self._graph.info()

    def compat(self): 
        return self._compat

    def compatInfo(self): 
        info = ""
        for vertex, compats in self._compat.items(): 
            info += vertex
            for compat in compats: 
                info += " " + compat
            info += "\n"
        return info

class TrivialIsoMatcher(Base): 
    def __init__(self, graph, units): 
        self._original = graph
        self._units    = units
        self._patterns = {}
        self._matched  = []
        self._map      = {}
        self._graph    = HyperGraph()
        self._compat   = {}

    def match(self): 
        for uname, unit in self._units.items(): 
            self._patterns[uname] = {}
            for pname, patt in unit.patterns().items(): 
                self._patterns[uname][pname] = patt.graph()
                # print("Pattern: " + uname + "." + pname)
                # print(self._patterns[uname][pname].info())
                # print("Matching: " + uname + "." + pname)
                g1 = self._original.toNX()
                g2 = self._patterns[uname][pname].toNX()
                matcher = iso.DiGraphMatcher(g1, g2, lambda x, y: x["attrs"]["function"] == y["attrs"]["function"])
                # print(matcher.subgraph_is_isomorphic())
                isomorphisms = matcher.subgraph_isomorphisms_iter()
                for match in isomorphisms: 
                    self._matched.append((uname, pname, match, ))
                    # print(match)
        self._matched.sort(key=lambda x: (len(x[2]), -len(self._units[x[0]].patterns())), reverse=True)
        # print(self._original.info())
        # print(utils.list2str(self._matched))
        
        used = set()
        for match in self._matched: 
            uname = match[0]
            pname = match[1]
            info  = match[2]
            duplicated = False
            for v1, v2 in info.items(): 
                if v1 in used: 
                    duplicated = True
                    break
            if duplicated: 
                continue
            for v1, v2 in info.items(): 
                used.add(v1)

            vertexName = ""
            for v1, v2 in info.items(): 
                if not "." in v1: 
                    vertexName += v1 + "_"
            vertexName = vertexName[:-1]
            self._graph.addVertex(vertexName, {"unit": uname, "pattern": pname})
            if not vertexName in self._compat: 
                self._compat[vertexName] = set()
            self._compat[vertexName].add(uname)
            for v1, v2 in info.items(): 
                portName = ""
                portType = ""
                for key, value in self._units[uname].pattern(pname).portMap().items(): 
                    if value == v2: 
                        portName = key
                        if portName in self._units[uname].inputs(): 
                            portType = "input"
                        elif portName in self._units[uname].outputs(): 
                            portType = "output"
                        else: 
                            assert portName in self._units[uname].inputs() or portName in self._units[uname].outputs(), "IsoMatcher: Invalid port: " + portName + " of " + uname
                if portName != "": 
                    temp = portName
                    portName = vertexName + "." + portName
                    self._graph.addVertex(portName, {"unit": uname + "." + temp})
                    self._map[v1] = portName
                    if portType == "input": 
                        self._graph.addNet([portName, vertexName], {})
                    elif portType == "output": 
                        self._graph.addNet([vertexName, portName], {})
        # print(utils.dict2str(self._map))

        if len(used) < len(self._original.vertices()): 
            print("IsoMatcher: FAILED. ")
            exit(1) 

        for vname, vertex in self._original.vertices().items(): 
            if vname in self._map: 
                for edge in self._original.netsOut()[vname]: 
                    nodes = [self._map[edge.fr()], ]
                    for node in edge.to(): 
                        if node in self._map: 
                            nodes.append(self._map[node])
                    if len(nodes) > 1: 
                        self._graph.addNet(nodes, {})

    def graph(self): 
        return self._graph

    def graphInfo(self): 
        return self._graph.info()

    def compat(self): 
        return self._compat

    def compatInfo(self): 
        info = ""
        for vertex, compats in self._compat.items(): 
            info += vertex
            for compat in compats: 
                info += " " + compat
            info += "\n"
        return info



