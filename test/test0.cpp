#include "common/Common.h"
#include "common/Logger.h"
#include "common/HyperGraph.h"
#include "common/HierGraph.h"
#include "util/NetworkAnalyzer.h"

using namespace std; 
using namespace FastCGRA; 

bool testHyperGraph(); 
bool testHierGraph(); 
bool testNetworkAnalyzer(); 

int main()
{
    // bool okayHyperGraph = testHyperGraph(); 
    // NOTE << "================================================"; 
    // bool okayHierGraph = testHierGraph(); 
    // NOTE << "================================================"; 
    bool okayAnalyzer = testNetworkAnalyzer(); 
    NOTE << "================================================"; 

    // bool okay = okayHyperGraph; 
    // bool okay = okayHierGraph; 
    bool okay = okayAnalyzer; 

    return okay ? 0 : 1; 
}


bool testHyperGraph()
{
    HyperGraph graph; 
    graph.addAttr("attr0", string("Excited")); 
    graph.addAttr("attr1", vector<string>({"Excited", "Excited", "Excited", })); 
    graph << Vertex("v0", {{"data", Attribute(vector<double>({123, 11234}))}, }); 
    graph << Vertex("v1", {{"data", Attribute(vector<string>({"123", "11234"}))}, }); 
    graph << Vertex("v2"); 
    graph << Vertex("v3"); 
    graph << Net(vector<string>{"v0", "v1", }, {{"data", Attribute(vector<string>({"123", "11234"}))}, }); 
    graph << Net(vector<string>{"v0", "v2", }); 
    graph << Net(vector<string>{"v0", "v3", }); 
    graph.dumpTo("./tmp/tmp.log"); 
    NOTE << graph.toString(); 
    NOTE << ""; 
    
    HyperGraph loaded; 
    loaded.loadFrom("./tmp/tmp.log"); 
    NOTE << loaded.toString(); 
    NOTE << ""; 

    return true; 
}


bool testHierGraph()
{
    HierGraph hier0; 

    HyperGraph g0("G0"); 
    g0.loadFrom("./tmp/tmpg.txt"); 
    NOTE << g0.toString(); 
    HyperGraph g1("G1"); 
    g1.loadFrom("./tmp/tmpg.txt"); 
    NOTE << g1.toString(); 
    HyperGraph g2("G2"); 
    g2.loadFrom("./tmp/tmpg.txt"); 
    NOTE << g2.toString(); 

    hier0.addElement(g0); 
    hier0.addElement(g1); 
    hier0.addElement(g2); 
    hier0.addNet(Net(vector<string>{"G0", "G1"}, {{"Info", Attribute("G0G1")}, })); 
    hier0.addNet(Net(vector<string>{"G0", "G1", "G2"}, {{"Info", Attribute("G0G1G2")}, })); 
    NOTE << hier0.toString(); 

    hier0.dumpTo("./tmp/tmp.log"); 

    HierGraph hier1; 
    hier1.loadFrom("./tmp/tmp.log"); 
    NOTE << hier1.toString(); 

    NOTE << hier1.element("G0").toString(); 
    NOTE << hier1.element("G1").toString(); 
    NOTE << hier1.element("G2").toString(); 

    return true; 

}

bool testNetworkAnalyzer()
{
    Graph graphRRG("top"); 
    graphRRG.loadFrom("./tmp/top.rrg"); 
    clog << "SpectralClustering: RRG loaded. " << "Vertices: " << graphRRG.nVertices() << "; " << "Edges: " << graphRRG.nEdges() << endl; 

    NetworkAnalyzerLegacy analyzer(graphRRG); 
    clog << "SpectralClustering: RRG analyzed. " << "Vertices: " << analyzer.RRG().nVertices() << "; " << "Edges: " << analyzer.RRG().nEdges() << endl; 

    return true; 
}