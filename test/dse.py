import os
import sys 
sys.path.append(".")

import optuna
import numpy as np 

from genrtl import * 
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

MINSIZE = 2
MAXSIZE = 8
VARSIZE = 2 + 6 + 1
def var2param(var): # 0.0-1.0
    sizeArray = var[0:2]
    sizeArray[0] = MINSIZE + round(sizeArray[0] * (MAXSIZE - MINSIZE))
    sizeArray[1] = MINSIZE + round(sizeArray[1] * (MAXSIZE - MINSIZE))

    typePE = ["PE1" for _ in range(sizeArray[0]*sizeArray[1])]
    
    typeConn = var[2]
    if typeConn > 0.5: 
        typeConn = "HyCUBE"
    else: 
        typeConn = "ADRES"

    connMesh   = var[2 + 1]
    connDiag   = var[2 + 2]
    connOnehop = var[2 + 3]
    connBypass = var[2 + 4]
    if connMesh > 0.5: 
        connMesh = True
    else: 
        connMesh = False
    if connDiag > 0.5: 
        connDiag = True
    else: 
        connDiag = False
    if connOnehop > 0.5: 
        connOnehop = True
    else: 
        connOnehop = False
    if connBypass > 0.5: 
        connBypass = True
    else: 
        connBypass = False
    # connBypass = True

    MININTER = 1
    MAXINTER = 8
    interMem = var[2 + 5]
    interMem = MININTER + round(interMem * (MAXINTER - MININTER))
    interIO  = var[2 + 6]
    interIO  = MININTER + round(interIO * (MAXINTER - MININTER))

    return sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO

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

def evaluate(archfile = "./tmp/arch.txt", coordfile = "./tmp/coord.txt", timelimit = 180): 
    benchset = "cgrame"
    benchmarks = ["simple", "accumulate", "cap", "conv3", "mac2", "matrixmultiply", "mults1", "mults2", ]
    # benchmarks = ["accumulate", "cap", "conv2", "conv3", "mac", "mac2", "matrixmultiply", "mults1", "mults2", "nomem1", "simple", "simple2", "sum", ]

    count = 0
    countII = 0
    statuses = []
    for benchmark in benchmarks: 
        print("Running Benchmark: %s/%s" % (benchset, benchmark))
        command = "timeout %ds python3 ./test/pnr.py ./benchmark/%s/%s/%s_DFG.txt ./benchmark/%s/%s/%s_compat.txt  ./benchmark/%s/%s/%s_param.txt %s %s > /dev/null 2>&1" % (timelimit, benchset, benchmark, benchmark, benchset, benchmark, benchmark, benchset, benchmark, benchmark, archfile, coordfile)
        # print(" -> ", command)
        result = os.system(command)
        result /= 256
        print(" -> %s/%s:" % (benchset, benchmark), result)
        statuses.append(result)
        if result < 100: 
            count += 1
            countII += result
        else: 
            if benchmark == benchmarks[0]: 
                return 0, 16, 1e9
    
    print("Evaluating area with yosys. ")
    genrtl(archfile, "./tmp/CGRA.v")
    genyosys("CGRA","./tmp/CGRA.v", "./tmp/CGRA.ys")

    ratio = count / len(benchmarks)
    meanII = countII / count if count > 0 else 16
    area = getArea("./tmp/CGRA.ys", "./tmp/CGRA.log")

    print(list(zip(benchmarks, statuses)))
    print("Success rate: %f/%f = %f" % (count, len(benchmarks), ratio))
    print("Mean II: %f/%f = %f" % (countII, count, meanII))
    print("Area:", area)

    return ratio, meanII, area

def test0(): 
    sizeArray = [4, 4]
    typePE = ["PE1"] * (sizeArray[0] * sizeArray[1])
    typeConn = "ADRES"
    connMesh = True
    connDiag = False
    connOnehop = False
    connBypass = True
    interMem = 1
    interIO = 1
    
    writeArch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO)
    evaluate()


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

if __name__ == "__main__": 

    iter = 0
    def objective(trial: optuna.Trial): 
        global iter
        jsonfile  = "./arch/tmp/arch%d.json" % iter
        archfile  = "./arch/tmp/arch%d.txt"  % iter
        coordfile = "./arch/tmp/coord%d.txt" % iter
        var = suggestFloat(trial, numVars = VARSIZE, fromVal = 0, toVal = 1.0, prefix = "f")
        sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO = var2param(var)
        writeArch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO, \
                  jsonfile, archfile, coordfile)
        print(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO, \
              jsonfile, archfile, coordfile)
        if (not connMesh and not connDiag and not connOnehop) or \
           (not connMesh and not connDiag and not connBypass) or \
           (not connMesh and not connOnehop and not connBypass) or \
           (not connDiag and not connOnehop and not connBypass): 
            ratio, meanII, area = 0, 16, 1e9
        else: 
            ratio, meanII, area = evaluate(archfile, coordfile)
        with open("./tmp/dse.log", "a") as fout: 
            fout.write("Arch: " + archfile + "; " +  str((sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO, \
              jsonfile, archfile, coordfile)) +  "; Ratio, MeanII, Area: " + str(ratio) + ", " + str(meanII) + ", " + str(area) + "\n")
        iter += 1
        return ratio, meanII, area

    # sampler = optuna.samplers.NSGAIISampler()
    sampler = optuna.samplers.TPESampler(multivariate = True)
    optimizer = optuna.create_study(sampler = sampler, directions = ["maximize", "minimize", "minimize", ])

    optimizer.enqueue_trial({"f0": 0.33, "f1": 0.33, "f2": 0.0, "f3": 1.0, "f4": 0.0, \
                             "f5": 0.0, "f6": 1.0, "f7": 0.0, "f8": 0.0, })

    optimizer.enqueue_trial({"f0": 0.33, "f1": 0.33, "f2": 1.0, "f3": 1.0, "f4": 0.0, \
                             "f5": 0.0, "f6": 1.0, "f7": 0.0, "f8": 0.0, })

    optimizer.optimize(objective, n_trials=2 ** 12, show_progress_bar=True)

    