import sys 
sys.path.append(".")

import json

from mapping.schedule import *
from mapping.pack import *
from mapping.place import *
from mapping.route import *

def test0(): 
    dfg        = HyperGraph("./benchmark/cgrame/conv3_DFG.txt")
    compat     = utils.readCompat("./benchmark/cgrame/conv3_compat.txt")
    patt1      = HyperGraph("./dataflow/patterns/pattALU1.txt")
    patt2      = HyperGraph("./dataflow/patterns/pattALU2.txt")
    patt3      = HyperGraph("./dataflow/patterns/pattALU3.txt")
    patt4      = HyperGraph("./dataflow/patterns/pattALU4.txt")
    patterns   = {"pattALU1": patt1, "pattALU2": patt2, "pattALU3": patt3, "pattALU4": patt4, }
    pattCompat = {"pattALU1": "func", "pattALU2": "func", "pattALU3": "func", "pattALU4": "func", }
    
    packer = IsoPacker(dfg, patterns, compat, pattCompat)

    packer.match()
    
    utils.writefile("./tmp/conv3_DFG.txt", packer.graph().info())
    utils.writeCompat("./tmp/conv3_compat.txt", packer.compat())


def test1(): 
    dfg    = HyperGraph("./tmp/conv3_DFG.txt")
    rrg    = HyperGraph("./tmp/adres_RRG.txt")
    compat = utils.readCompat("./tmp/conv3_compat.txt")
    placer = AnalyticPlacer(rrg, "./tmp/adres_coords.txt")
    placer.place(dfg, compat)


def test2(): 
    dfg    = HyperGraph("./tmp/conv2_DFG.txt")
    rrg    = HyperGraph("./tmp/adres_RRG.txt")
    compat = utils.readCompat("./tmp/conv2_compat.txt")
    placer = AnalyticPlacer(rrg, "./tmp/adres_coords.txt")
    result = placer.place(dfg, compat)

    # router = MazeRouter(rrg, 1024)
    router = CliqueRouter(rrg)
    result = router.routeDFG(dfg, result)
    print(result)


def test3(): 
    dfg    = HyperGraph("./tmp/conv3_DFG.txt")
    compat = utils.readCompat("./tmp/conv3_compat.txt")
    rrg    = HyperGraph("./tmp/adres_RRG.txt")
    placer = AnnealingPlacer(rrg)
    placement, routing = placer.place(dfg, compat)


def test4(): 
    # dfg    = HyperGraph("./benchmark/express/arf_DFG.txt")
    # compat = utils.readCompat("./benchmark/express/arf_compat.txt")
    dfg    = HyperGraph("./benchmark/express/motion_vectors_dfg__7_DFG.txt")
    compat = utils.readCompat("./benchmark/express/motion_vectors_dfg__7_compat.txt")
    # dfg    = HyperGraph("./benchmark/express/horner_bezier_surf_dfg__12_DFG.txt")
    # compat = utils.readCompat("./benchmark/express/horner_bezier_surf_dfg__12_compat.txt")
    rrg    = HyperGraph("./arch/ADRES.txt")
    scheduler = Scheduler(rrg, dfg, compat, "./arch/ADRES_coords.txt")
    scheduler.schedule()


def test5(): 
    dfg    = HyperGraph("./tmp/tmpg0.txt")
    compat = utils.readCompat("./benchmark/express/arf_compat.txt")
    rrg    = HyperGraph("./tmp/adres_RRG.txt")
    placer = AnnealingPlacer(rrg)
    placement, routing = placer.place(dfg, compat)


def test6(): 
    # dfg    = HyperGraph("./tmp/tmpg0.txt")
    # compat = utils.readCompat("./benchmark/express/arf_compat.txt")
    dfg    = HyperGraph("./tmp/conv3_DFG.txt")
    compat = utils.readCompat("./tmp/conv3_compat.txt")
    rrg    = HyperGraph("./tmp/ADRES_RRG.txt")

    placer = AnalyticPlacer(rrg, "./tmp/ADRES_coords.txt", silent=False)
    placement, routing = placer.place(dfg, compat)

    placer = AnnealingPlacer(rrg, "./tmp/ADRES_coords.txt", patience=256, temper=0.20, silent=False)
    placement, routing = placer.place(dfg, compat, placement)



if __name__ == "__main__": 
    # test0()
    # test1()
    # test2()
    # test3()
    test4()
    # test5()
    # test6()
