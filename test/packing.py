import sys 
sys.path.append(".")

import json

from mapping.schedule import *
from mapping.pack import *
from mapping.place import *
from mapping.route import *

if __name__ == "__main__": 
    dfgfile = sys.argv[1]
    compatfile = sys.argv[2]

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
    
    utils.writefile(dfgfile[0:-3] + "packed.txt", packer.graph().info())
    utils.writeCompat(compatfile[0:-3] + "packed.txt", packer.compat())
