import sys 
sys.path.append(".")

from mapping.schedule import *
from mapping.pack import *
from mapping.place import *
from mapping.route import *

if __name__ == "__main__": 
    dfgfile = sys.argv[1]
    compatfile = sys.argv[2]
    if len(sys.argv) < 5: 
        rrgfile = "./arch/ADRES.txt"
        coordfile = "./arch/ADRES_coords.txt"
    else: 
        rrgfile = sys.argv[3]
        coordfile = sys.argv[4]
    verbose = False
    if len(sys.argv) > 5: 
        verbose = True

    dfg    = HyperGraph(dfgfile)
    compat = utils.readCompat(compatfile)
    rrg    = HyperGraph(rrgfile)

    patt1      = HyperGraph("./dataflow/patterns/pattALU1.txt")
    patt2      = HyperGraph("./dataflow/patterns/pattALU2.txt")
    patt3      = HyperGraph("./dataflow/patterns/pattALU3.txt")
    patt4      = HyperGraph("./dataflow/patterns/pattALU4.txt")
    patterns   = {"pattALU1": patt1, "pattALU2": patt2, "pattALU3": patt3, "pattALU4": patt4, }
    pattCompat = {"pattALU1": "ALU", "pattALU2": "ALU", "pattALU3": "ALU", "pattALU4": "ALU", }

    packer = IsoPacker(dfg, patterns, compat, pattCompat)
    packer.match()

    dfg = packer.graph()
    compat = packer.compat()

    AnalyticPlacer.MAXITER = 1024 * 2
    AnalyticPlacer.PATIENCE = 256
    placer = AnalyticPlacer(rrg, coordfile, silent=verbose, temper=0.25)
    placement, routing, cost = placer.place(dfg, compat)
    placer = AnnealingPlacer(rrg, coordfile, patience=1024, temper=0.20, silent=verbose, maxDist=2)
    placement, routing, cost = placer.place(dfg, compat, placement)

    # placer = AnnealingPlacer(rrg, "./arch/ADRES_coords.txt", silent=verbose)
    # placement, routing, cost = placer.place(dfg, compat)

    if len(placement) > 0: 
        print("Succeed")
        exit(0)
    else: 
        print("Failed")
        exit(1)
