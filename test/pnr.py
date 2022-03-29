import sys 
sys.path.append(".")

import time
import json
import argparse

from mapping.schedule import *
from mapping.pack import *
from mapping.place import *
from mapping.route import *

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="FastCGRA: Placement and Routing")
    parser.add_argument("dfg", type=str, \
                        help="The path of the DFG file. ")
    parser.add_argument("compat", type=str, \
                        help="The path of the compatibility file. ")
    parser.add_argument("--rrg", "-r", type=str, default="./arch/ADRES.txt", \
                        help="The path of the RRG file. ")
    parser.add_argument("--coord", "-c", type=str, default="./arch/ADRES_coords.txt", \
                        help="The path of the coordinate file. ")
    parser.add_argument("--param", "-p", type=str, default="", \
                        help="The path of the mapping parameter file. ")
    parser.add_argument("--maxnum", "-n", type=int, default=4, \
                        help="Maximum number of seeds. ")
    parser.add_argument("--maxstatuses", "-s", type=int, default=16, \
                        help="Maximum number of scheduling statuses. ")
    parser.add_argument("--njobs", "-j", type=int, default=8, \
                        help="Maximum number of jobs. ")
    parser.add_argument("--maxops", "-v", type=float, default=0.9, \
                        help="Full-threshold of operations. ")
    parser.add_argument("--maxedges", "-e", type=float, default=0.6, \
                        help="Full-threshold of edges. ")
    parser.add_argument("--fullnum", "-f", type=int, default=1, \
                        help="Maximum number of full oprations/edges. ")
    parser.add_argument("--mapper", "-m", type=int, default=0, \
                        help="Mapper: 0: HybridMap; 1: Simulated Annealing. ")
    args = parser.parse_args()

    dfgfile    = args.dfg
    compatfile = args.compat
    paramfile  = args.param
    rrgfile    = args.rrg
    coordfile  = args.coord

    dfg    = HyperGraph(dfgfile)
    compat = utils.readCompat(compatfile)

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

    Scheduler.MAXNUM      = args.maxnum
    Scheduler.NUMSTATUSES = args.maxstatuses
    Scheduler.NJOBS       = args.njobs
    Scheduler.MAXOPS      = args.maxops
    Scheduler.MAXEDGES    = args.maxedges
    Scheduler.FULLNUM     = args.fullnum
    Scheduler.PLACER      = args.mapper

    if len(paramfile) > 0: 
        with open(paramfile, "r") as fin: 
            info = json.loads(fin.read())
        Scheduler.MAXNUM      = info["MAXNUM"]   if "MAXNUM"   in info else 4
        Scheduler.NUMSTATUSES = info["NUMSTATUSES"] if "NUMSTATUSES" in info else 16
        Scheduler.NJOBS       = info["NJOBS"]  if "NJOBS"  in info else 8
        Scheduler.MAXOPS      = info["MAXOPS"]   if "MAXOPS"   in info else 0.9
        Scheduler.MAXEDGES    = info["MAXEDGES"] if "MAXEDGES" in info else 0.6
        Scheduler.FULLNUM     = info["FULLNUM"]  if "FULLNUM"  in info else 1
        Scheduler.PLACER      = info["PLACER"]   if "PLACER"  in info else 0

    start  = time.perf_counter()
    rrg = HyperGraph(rrgfile)
    scheduler = Scheduler(rrg, dfg, compat, coordfile)
    ii = scheduler.schedule()
    end  = time.perf_counter()
    print("Time: %.3fs" % (end-start))

    exit(ii)
