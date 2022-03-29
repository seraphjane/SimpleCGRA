import sys 
sys.path.append(".")

import networkx as nx
from networkx.algorithms import isomorphism as iso

import common.utils as utils
from common.utils import Base
from common.graph import HyperGraph
from arch.protocols import *

class IsoPacker(Base): 
    def __init__(self, graph: HyperGraph, patterns: dict, compat: dict, pattCompat: dict): 
        self._original   = graph
        self._patterns   = patterns
        self._compat     = compat
        self._pattCompat = pattCompat
        self._matched    = []
        self._map        = {}
        self._graph      = HyperGraph()
        for name, vertex in self._original.vertices().items(): 
            splited = name.split(".")
            compat = self._compat[splited[0]][0] #TODO
            if len(splited) > 1: 
                compat += "." + splited[1]
            vertex.addAttr("compat", compat)

    def match(self): 
        g1 = self._original.toNX()
        for name, patt in self._patterns.items(): 
            g2 = patt.toNX()
            matcher = iso.DiGraphMatcher(g1, g2, lambda x, y: x["attrs"]["compat"] == y["attrs"]["compat"])
            isomorphisms = matcher.subgraph_isomorphisms_iter()
            for match in isomorphisms: 
                self._matched.append((name, match, ))
        self._matched.sort(key=lambda x: len(x[1]), reverse=True)
        
        used = set()
        relation = {}
        vertex2patt = {}
        for match in self._matched: 
            name = match[0]
            info = match[1]
            duplicated = False
            for v1, v2 in info.items(): 
                if v1 in used: 
                    duplicated = True
                    break
            if duplicated: 
                continue
            for v1, v2 in info.items(): 
                used.add(v1)
                vertex2patt[v1] = name

            vertexName = ""
            for v1, v2 in info.items(): 
                if not "." in v1: 
                    vertexName += v1 + "_"
            vertexName = vertexName[:-1]
            for v1, v2 in info.items(): 
                relation[v1] = vertexName + "." + v2
            self._graph.addVertex(vertexName, {"pattern": name})
            if not vertexName in self._compat: 
                self._compat[vertexName] = []
            assert name in self._pattCompat
            self._compat[vertexName].append(self._pattCompat[name])

        # print(used)
        # print(relation)
        for name, vertex in self._original.vertices().items(): 
            if not name in used: 
                self._graph.addVertex(name, vertex.attrs())
        for name, vertex in self._original.vertices().items(): 
            for net in self._original.netsOut(name): 
                fr = net.fr()
                for to in net.to(): 
                    if fr in vertex2patt and to in vertex2patt and vertex2patt[fr] == vertex2patt[to]: 
                        continue
                    if fr in relation: 
                        fr = relation[fr]
                        if not fr in self._graph.vertices(): 
                            self._graph.addVertex(fr)
                    if to in relation: 
                        to = relation[to]
                        if not to in self._graph.vertices(): 
                            self._graph.addVertex(to)
                    nodes = [fr, to]
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