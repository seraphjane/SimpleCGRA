import os
import sys 
sys.path.append(".")

import numpy as np 
from common.utils import *

import matplotlib.pyplot as plt

def dominate(a, b): 
    assert len(a) == len(b)
    domin = True
    for idx in range(len(a)): 
        if a[idx] > b[idx]: 
            domin = False
            break
    return domin

def newParetoSet(paretoParams, paretoValues, newParams, newValue): 
    assert len(paretoParams) == len(paretoValues)
    dupli = False
    removed = set()
    indices = []
    for idx, elem in enumerate(paretoValues): 
        if str(paretoParams[idx]) == str(newParams): 
            dupli = True
            break
        if dominate(newValue, elem): 
            removed.add(idx)
    if dupli: 
        return paretoParams, paretoValues
    for idx, elem in enumerate(paretoValues): 
        if not idx in removed: 
            indices.append(idx)
    newParetoParams = []
    newParetoValues = []
    for index in indices: 
        newParetoParams.append(paretoParams[index])
        newParetoValues.append(paretoValues[index])
    bedominated = False
    for idx, elem in enumerate(newParetoValues): 
        if dominate(elem, newValue): 
            bedominated = True
    if len(removed) > 0:
        assert not bedominated
    if len(removed) > 0 or len(paretoParams) == 0 or not bedominated: 
        newParetoParams.append(newParams)
        newParetoValues.append(newValue)
    return newParetoParams, newParetoValues

def pareto(params, values): 
    paretoParams = []
    paretoValues = []

    for var, objs in zip(params, values): 
        paretoParams, paretoValues = newParetoSet(paretoParams, paretoValues, var, objs)

if __name__ == "__main__": 
    paretoParams = []
    paretoValues = []
    with open("./tmp/dse.log") as fin: 
        for line in fin.readlines(): 
            if len(line.strip()) == 0: 
                continue
            splited = line.strip().split(": ")[-1].split(", ")
            info    = splited[-3:]
            ratio   = float(info[0])
            ii      = float(info[1])
            area    = float(info[2])
            if ratio == 1.0: 
                splited = line.strip().split("(")[-1].split(")")[0].split(", ")
                params = [splited[0] + ", " + splited[1]] + splited[-10:-3]
                paretoParams, paretoValues = newParetoSet(paretoParams, paretoValues, params, [ii, area])
    print(list2str(list(zip(paretoParams, paretoValues))))
    # print(paretoValues)

    labels = paretoParams
    for label in labels: 
        label = label[0:2]
    xs = []
    ys = []
    for x, y in paretoValues: 
        xs.append(x)
        ys.append(y / 1e6)

    plt.style.use("ggplot")
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 14
    plt.scatter(xs, ys)
    plt.xlabel("Mean II")
    plt.ylabel("Area ($10^6$)")

    for idx in range(len(paretoValues)): 
        x, y = paretoValues[idx][0], paretoValues[idx][1] / 1e6
        if idx % 2 == 1: 
            plt.annotate(str(labels[idx][0] + "," + labels[idx][1][1]), xy=(x, y), xytext=(-20, 10), textcoords='offset points')
        else: 
            plt.annotate(str(labels[idx][0] + "," + labels[idx][1][1]), xy=(x, y), xytext=(-20, -15), textcoords='offset points')

    plt.show()




