import sys 
sys.path.append(".")

from common.utils import *
from common.graph import *
from arch.arch import *
from arch.adres import *
from arch.protocols import *
from arch.genarch import *
from dataflow.dataflow import *
from dataflow.funcmap import *
from dataflow.example import *
import dataflow.dataflow as df

def testGraph(): 
    graph = HyperGraph()
    with open("./tmp/tmp.log", "r") as fin: 
        graph.parse(fin.read())
    print(graph.info())

def testDataflow(): 
    archDesc = archCGRA()
    with open("./tmp/example.json", "w") as fout: 
        fout.write(json.dumps(archDesc, indent=4))
    
    arch = Arch("./tmp/example.json")
    # print(arch.info())
    # print(arch.rrg())
    # print(arch.fus())
    with open("./tmp/exampleRRG.txt", "w") as fout: 
        fout.write(arch.rrg())
    with open("./tmp/exampleFUs.txt", "w") as fout: 
        fout.write(arch.fus())

    LoadFunctions(arch.functions())

    add0 = df.ADD()
    add1 = df.ADD()
    mul0 = df.MUL(add0["out0"], add1["out0"])
    add2 = df.ADD(); add2(mul0["out0"], add2["out0"])

    print(dataflow().info())

    mapper = fm.IsoMatcher(dataflow(), arch.units())
    # mapper = fm.TrivialIsoMatcher(dataflow(), arch.units())
    mapper.match()
    print(mapper.graphInfo())
    print(mapper.compatInfo())
    with open("./tmp/exampleDFG.txt", "w") as fout: 
        fout.write(mapper.graphInfo())
    with open("./tmp/exampleCompat.txt", "w") as fout: 
        fout.write(mapper.compatInfo())

def testArch(): 
    archfile = "./tmp/adres_II2.json"
    info = archADRES(II = 2)
    with open(archfile, "w") as fout: 
        fout.write(json.dumps(info, indent=4))
    adres = Arch(archfile)
    with open("./tmp/adres_II2_RRG.txt", "w") as fout: 
        fout.write(adres.top().dumpGraph())
    with open("./tmp/adres_II2_fus.txt", "w") as fout: 
        fout.write(adres.fus())

def testADRES(): 
    archfile = "./arch/ADRES.json"
    info = ADRES()
    with open(archfile, "w") as fout: 
        fout.write(json.dumps(info, indent=4))
    adres = Arch(archfile)
    with open("./arch/ADRES.txt", "w") as fout: 
        fout.write(adres.top().dumpGraph())
    with open("./arch/ADRES_FUs.txt", "w") as fout: 
        fout.write(adres.fus())


def writeArch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO, \
              jsonfile = "./tmp/arch.json", archfile = "./tmp/arch.txt", coordfile = "./tmp/coord.txt"): 
    arch = genarch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO)
    with open(jsonfile, "w") as fout: 
        fout.write(json.dumps(arch, indent=4))
        
    arch = Arch(jsonfile)
    with open(archfile, "w") as fout: 
        fout.write(arch.top().dumpGraph())

    coord = gencoord(sizeArray, typePE)
    with open(coordfile, "w") as fout: 
        for line in coord: 
            fout.write(line + "\n")
def testHyCUBE(): 
    sizeArray = [4, 4]
    typePE = ["PE1"] * (sizeArray[0] * sizeArray[1])
    typeConn = "HyCUBE"
    connMesh = True
    connDiag = False
    connOnehop = False
    connBypass = True
    interMem = 1
    interIO = 1
    
    writeArch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO)

if __name__ == "__main__": 
    # testGraph()
    # testDataflow()
    # testArch()
    # testADRES()
    testHyCUBE()

    # archfile = "./arch/arch.json"
    # adres = Arch(archfile)