import sys
from unittest import result 
sys.path.append(".")

import xmltodict
import json

def _basicFunctions(): 
    return {
        "__INPUT__":  {"input": ["in0", ], "output": ["out0", ], "width": "32"}, 
        "__OUTPUT__": {"input": ["in0", ], "output": ["out0", ], "width": "32"}, 
        "__IO__":  {"input": ["in0", ], "output": ["out0", ], "width": "32"}, 
        "__ADD__": {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__SUB__": {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__MUL__": {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__ACC__": {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__AND__": {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__OR__":  {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__XOR__": {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__NOT__": {"input": ["in0", ],      "output": ["out0", ], "width": "32"}, 
        "__LSHIFT__":  {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__RSHIFT__":  {"input": ["in0", "in1"], "output": ["out0", ], "width": "32"}, 
        "__MAD__":     {"input": ["in0", "in1", "in2"], "output": ["out0", ], "width": "32"}, 
        "__CONST__":   {"input": ["in0", ], "output": ["out0", ], "width": "32"}, 
        # "__REG__":     {"input": ["din", "ctr", ], "output": ["dout", ], "width": "32"}, 
        "__REG__":     {"input": ["in0", "in1", ], "output": ["out0", ], "width": "32"}, 
        # "__MEM__":     {"input": ["addr", "din", "ctr", ], "output": ["dout", ], "width": "32"}, 
        "__MEM__":     {"input": ["in0", "in1", "in2", ], "output": ["out0", ], "width": "32"}, 
        "__EQUAL__":   {"input": ["in0", "in1", ], "output": ["out0", ], "width": "32"}, 
        "__GREATER__": {"input": ["in0", "in1", ], "output": ["out0", ], "width": "32"}, 
        "__LESS__":    {"input": ["in0", "in1", ], "output": ["out0", ], "width": "32"}, 
        "__BRANCH2__": {"input": ["in0", ], "output": ["out0", "out1", ], "width": "32"}, 
        "__BRANCH3__": {"input": ["in0", ], "output": ["out0", "out1", "out2", ], "width": "32"}, 
        "__BRANCH4__": {"input": ["in0", ], "output": ["out0", "out1", "out2", "out3", ], "width": "32"}, 
        "__JOIN2__":   {"input": ["in0", "in1", "select"], "output": ["out0", ], "width": "32"}, 
        "__JOIN3__":   {"input": ["in0", "in1", "in2", "select"], "output": ["out0", ], "width": "32"}, 
        "__JOIN4__":   {"input": ["in0", "in1", "in2", "in3", "select"], "output": ["out0", ], "width": "32"}, 
    } 

def _templateSimple(): 
    arch = {}

    arch["Function"] = _basicFunctions()

    arch["Unit"] = {
        "IO": {"input": ["in0", ], "output": ["out0", ], 
               "function": {"FUNC_IO0": "__IO__", }, 
               "pattern": {"PATN_IO0": {"unit": ["FUNC_IO0", ], 
                                        "port": {"in0": "FUNC_IO0.in0", 
                                                 "out0": "FUNC_IO0.out0"}, 
                                        "connection": [], }, }, 
               "compat": {}, }, 
        "CONST": {"input": ["in0", ], "output": ["out0", ], 
                  "function": {"FUNC_CONST0": "__CONST__", }, 
                  "pattern": {"PATN_CONST0": {"unit": ["FUNC_CONST0", ], 
                                              "port": {"in0": "FUNC_CONST0.in0", 
                                                       "out0": "FUNC_CONST0.out0"}, 
                                              "connection": [], }, }, 
                  "compat": {}, }, 
        "REG": {"input": ["in0", "in1", ], "output": ["out0", ], 
                "function": {"FUNC_REG0": "__REG__", }, 
                "pattern": {"PATN_REG0": {"unit": ["FUNC_REG0", ], 
                                          "port": {"in0": "FUNC_REG0.in0", 
                                                   "in1": "FUNC_REG0.in1", 
                                                   "out0": "FUNC_REG0.out0"}, 
                                          "connection": [], }, }, 
                "compat": {}, }, 
        "MEM": {"input": ["in0", "in1", "in2", ], "output": ["out0", ], 
                "function": {"FUNC_MEM0": "__MEM__", }, 
                "pattern": {"PATN_MEM0": {"unit": ["FUNC_MEM0", ], 
                                          "port": {"in0": "FUNC_MEM0.in0", 
                                                   "in1": "FUNC_MEM0.in1", 
                                                   "in2": "FUNC_MEM0.in2", 
                                                   "out0": "FUNC_MEM0.out0"}, 
                                          "connection": [], }, }, 
                "compat": {}, }, 
        "ALU": {"input": ["in0", "in1", "in2", ], "output": ["out0", ], 
                "function": {"FUNC_ADD0": "__ADD__", 
                             "FUNC_SUB0": "__SUB__", 
                             "FUNC_MUL0": "__MUL__", 
                             "FUNC_AND0": "__AND__", 
                             "FUNC_OR0":  "__OR__", 
                             "FUNC_XOR0":  "__XOR__", 
                             "FUNC_LSHIFT0":  "__LSHIFT__", 
                             "FUNC_RSHIFT0":  "__RSHIFT__", 
                             "FUNC_SELECT0":  "__JOIN2__", }, 
                "pattern": {"PATN_ADD0": {"unit": ["FUNC_ADD0", ], 
                                        "port": {"in0": "FUNC_ADD0.in0", 
                                                    "in1": "FUNC_ADD0.in1", 
                                                    "out0": "FUNC_ADD0.out0"}, 
                                        "connection": [], }, 
                            "PATN_SUB0": {"unit": ["FUNC_SUB0", ], 
                                        "port": {"in0": "FUNC_SUB0.in0", 
                                                    "in1": "FUNC_SUB0.in1", 
                                                    "out0": "FUNC_SUB0.out0"}, 
                                        "connection": [], }, 
                            "PATN_MUL0": {"unit": ["FUNC_MUL0", ], 
                                        "port": {"in0": "FUNC_MUL0.in0", 
                                                    "in1": "FUNC_MUL0.in1", 
                                                    "out0": "FUNC_MUL0.out0"}, 
                                        "connection": [], }, 
                            "PATN_AND0": {"unit": ["FUNC_AND0", ], 
                                        "port": {"in0": "FUNC_AND0.in0", 
                                                    "in1": "FUNC_AND0.in1", 
                                                    "out0": "FUNC_AND0.out0"}, 
                                        "connection": [], }, 
                            "PATN_OR0": {"unit": ["FUNC_OR0", ], 
                                        "port": {"in0": "FUNC_OR0.in0", 
                                                "in1": "FUNC_OR0.in1", 
                                                "out0": "FUNC_OR0.out0"}, 
                                        "connection": [], }, 
                            "PATN_XOR0": {"unit": ["FUNC_XOR0", ], 
                                        "port": {"in0": "FUNC_XOR0.in0", 
                                                    "in1": "FUNC_XOR0.in1", 
                                                    "out0": "FUNC_XOR0.out0"}, 
                                        "connection": [], }, 
                            "PATN_LSHIFT0": {"unit": ["FUNC_LSHIFT0", ], 
                                            "port": {"in0": "FUNC_LSHIFT0.in0", 
                                                    "in1": "FUNC_LSHIFT0.in1", 
                                                    "out0": "FUNC_LSHIFT0.out0"}, 
                                            "connection": [], }, 
                            "PATN_RSHIFT0": {"unit": ["FUNC_RSHIFT0", ], 
                                            "port": {"in0": "FUNC_RSHIFT0.in0", 
                                                    "in1": "FUNC_RSHIFT0.in1", 
                                                    "out0": "FUNC_RSHIFT0.out0"}, 
                                            "connection": [], }, 
                            "PATN_SELECT": {"unit": ["FUNC_SELECT0", ], 
                                            "port": {"in0": "FUNC_SELECT0.in0", 
                                                    "in1": "FUNC_SELECT0.in1", 
                                                    "in2": "FUNC_SELECT0.select", 
                                                    "out0": "FUNC_SELECT0.out0"}, 
                                            "connection": [], }, },
                "compat": {}, },
    }

    arch["Switch"] = {
        "FULLYCONN_2X1": {
            "input":  ["in0", "in1", ], 
            "output": ["out0", ], 
            "required": ["in0->out0", "in1->out0", ], 
            "graph": "", 
        }, 
        "FULLYCONN_6X1": {
            "input":  ["in0", "in1", "in2", "in3", "in4", "in5", ], 
            "output": ["out0", ], 
            "required": ["in0->out0", "in1->out0", "in2->out0", "in3->out0", "in4->out0", "in5->out0",], 
            "graph": "", 
        }, 
        "FULLYCONN_10X1": {
            "input":  ["in0", "in1", "in2", "in3", "in4", "in5", "in6", "in7", "in8", "in9"], 
            "output": ["out0", ], 
            "required": ["in0->out0", "in1->out0", "in2->out0", "in3->out0", "in4->out0", 
                         "in5->out0", "in6->out0", "in7->out0", "in8->out0", "in9->out0", ], 
            "graph": "", 
        }, 
        "FULLYCONN_PE": {
            "input":  [], 
            "output": ["out0", ], 
            "required": [], 
            "graph": "", 
        }, 
        "FULLYCONN_MEM": {
            "input":  [], 
            "output": ["out0", ], 
            "required": [], 
            "graph": "", 
        }, 
        "FULLYCONN_IO": {
            "input":  [], 
            "output": ["out0", ], 
            "required": [], 
            "graph": "", 
        }, 
    }

    arch["Module"] = {
        "PE0": {
            "input": [], 
            "output": [], 
            "module": {}, 
            "element": {
                "ALU0": "ALU", 
                "CONST0": "CONST", 
                # "CONST1": "CONST", 
            }, 
            "switch": {}, 
            "connection": []
        }, 
        "PE1": {
            "input": [], 
            "output": [], 
            "module": {}, 
            "element": {
                "ALU0": "ALU", 
                "CONST0": "CONST", 
                # "CONST1": "CONST", 
            }, 
            "switch": {}, 
            "connection": []
        }, 
        "MEMORY": {
            "input": [], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "MEM0": "MEM", 
            }, 
            "switch": {
                "SW_addr": "FULLYCONN_MEM", 
                "SW_din": "FULLYCONN_MEM", 
                "SW_ctr": "FULLYCONN_MEM", 
            }, 
            "connection": []
        }, 
        "IOPAD": {
            "input": [], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "IO0": "IO", 
            }, 
            "switch": {
                "SW_in0": "FULLYCONN_IO", 
            }, 
            "connection": []
        }, 
    }

    return arch

def _basearch(): 
    arch = _templateSimple()
    
    arch["Function"]["__DUMMY__"] = {"input": ["in0", ], "output": ["out0", ], "width": "32"}
    
    arch["Unit"]["DUMMY"] = {
        "input": ["in0", ], "output": ["out0", ], 
        "function": {"FUNC_DUMMY0": "__DUMMY__", }, 
        "pattern": {"PATN_DUMMY0": {"unit": ["FUNC_DUMMY0", ], 
                                    "port": {"in0": "FUNC_DUMMY0.in0", 
                                             "out0": "FUNC_DUMMY0.out0"}, 
                                    "connection": [], }, }, 
        "compat": {}, 
    }

    arch["Module"]["CGRA"] = {
        "input": [], 
        "output": [], 
        "module": {}, 
        "element": {}, 
        "switch": {}, 
        "connection": []
    }
    return arch

def genarch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO): 

    arch = _basearch()
    
    rows = sizeArray[0]
    cols = sizeArray[1]

    # inputs/outputs of PEs
    inputsPE = ["in0", "in1", "in2", "in3", ]
    outputsPE = ["out0", "out1", "out2", "out3", ]
    if connMesh: 
        inputsPE.extend(["in_mesh0", "in_mesh1", "in_mesh2", "in_mesh3"])
        outputsPE.extend(["out_mesh0", "out_mesh1", "out_mesh2", "out_mesh3"])
    if connDiag: 
        inputsPE.extend(["in_diag0", "in_diag1", "in_diag2", "in_diag3"])
        outputsPE.extend(["out_diag0", "out_diag1", "out_diag2", "out_diag3"])
    if connOnehop: 
        inputsPE.extend(["in_onehop0", "in_onehop1", "in_onehop2", "in_onehop3"])
        outputsPE.extend(["out_onehop0", "out_onehop1", "out_onehop2", "out_onehop3"])
    arch["Module"]["PE0"]["input"].extend(inputsPE)
    arch["Module"]["PE1"]["input"].extend(inputsPE)
    if typeConn == "HyCUBE": 
        pass
    elif typeConn == "ADRES": 
        outputsPE = ["out0", ]
    else: 
        assert 0, "Unsupported interconnect style"
    arch["Module"]["PE0"]["output"].extend(outputsPE)
    arch["Module"]["PE1"]["output"].extend(outputsPE)

    # standard switch
    sizeSwitch = len(inputsPE) + 4
    for idx in range(sizeSwitch): 
        arch["Switch"]["FULLYCONN_PE"]["input"].append("in" + str(idx))
        arch["Switch"]["FULLYCONN_PE"]["required"].append("in" + str(idx) + "->out0")
    
    # Connections in PEs
    arch["Module"]["PE0"]["switch"]["SW_in0"] = "FULLYCONN_PE"
    arch["Module"]["PE0"]["switch"]["SW_in1"] = "FULLYCONN_PE"

    arch["Module"]["PE1"]["switch"]["SW_in0"] = "FULLYCONN_PE"
    arch["Module"]["PE1"]["switch"]["SW_in1"] = "FULLYCONN_PE"
    arch["Module"]["PE1"]["switch"]["SW_in2"] = "FULLYCONN_PE"

    if connBypass:
        for port in outputsPE: 
            arch["Module"]["PE0"]["switch"]["SW_" + port] = "FULLYCONN_PE"
            arch["Module"]["PE1"]["switch"]["SW_" + port] = "FULLYCONN_PE"

    for idx in range(len(inputsPE)):
        arch["Module"]["PE0"]["connection"].append(inputsPE[idx] + "->SW_in0.in" + str(idx))
        arch["Module"]["PE0"]["connection"].append(inputsPE[idx] + "->SW_in1.in" + str(idx))

        arch["Module"]["PE1"]["connection"].append(inputsPE[idx] + "->SW_in0.in" + str(idx))
        arch["Module"]["PE1"]["connection"].append(inputsPE[idx] + "->SW_in1.in" + str(idx))
        arch["Module"]["PE1"]["connection"].append(inputsPE[idx] + "->SW_in2.in" + str(idx))
        if connBypass:
            for port in outputsPE: 
                arch["Module"]["PE0"]["connection"].append(inputsPE[idx] + "->SW_" + port + ".in" + str(idx))
                arch["Module"]["PE1"]["connection"].append(inputsPE[idx] + "->SW_" + port + ".in" + str(idx))

    arch["Module"]["PE0"]["connection"].append("ALU0.out0->SW_in0.in" + str(len(inputsPE)))
    arch["Module"]["PE0"]["connection"].append("CONST0.out0->SW_in0.in" + str(len(inputsPE) + 1))
    # arch["Module"]["PE0"]["connection"].append("CONST1.out0->SW_in0.in" + str(len(inputsPE) + 2))
    arch["Module"]["PE0"]["connection"].append("SW_in0.out0->ALU0.in0")
    arch["Module"]["PE0"]["connection"].append("ALU0.out0->SW_in1.in" + str(len(inputsPE)))
    arch["Module"]["PE0"]["connection"].append("CONST0.out0->SW_in1.in" + str(len(inputsPE) + 1))
    # arch["Module"]["PE0"]["connection"].append("CONST1.out0->SW_in1.in" + str(len(inputsPE) + 2))
    arch["Module"]["PE0"]["connection"].append("SW_in1.out0->ALU0.in1")
    if connBypass:
        for port in outputsPE: 
            arch["Module"]["PE0"]["connection"].append("ALU0.out0->SW_" + port + ".in" + str(len(inputsPE)))
            arch["Module"]["PE0"]["connection"].append("CONST0.out0->SW_" + port + ".in" + str(len(inputsPE) + 1))
            # arch["Module"]["PE0"]["connection"].append("CONST1.out0->SW_" + port + ".in" + str(len(inputsPE) + 2))
            arch["Module"]["PE0"]["connection"].append("SW_" + port + ".out0->" + port)
    else: 
        for port in outputsPE: 
            arch["Module"]["PE0"]["connection"].append("ALU0.out0->" + port)

    arch["Module"]["PE1"]["connection"].append("ALU0.out0->SW_in0.in" + str(len(inputsPE)))
    arch["Module"]["PE1"]["connection"].append("CONST0.out0->SW_in0.in" + str(len(inputsPE) + 1))
    # arch["Module"]["PE1"]["connection"].append("CONST1.out0->SW_in0.in" + str(len(inputsPE) + 2))
    arch["Module"]["PE1"]["connection"].append("SW_in0.out0->ALU0.in0")
    arch["Module"]["PE1"]["connection"].append("ALU0.out0->SW_in1.in" + str(len(inputsPE)))
    arch["Module"]["PE1"]["connection"].append("CONST0.out0->SW_in1.in" + str(len(inputsPE) + 1))
    # arch["Module"]["PE1"]["connection"].append("CONST1.out0->SW_in1.in" + str(len(inputsPE) + 2))
    arch["Module"]["PE1"]["connection"].append("SW_in1.out0->ALU0.in1")
    arch["Module"]["PE1"]["connection"].append("ALU0.out0->SW_in2.in" + str(len(inputsPE)))
    arch["Module"]["PE1"]["connection"].append("CONST0.out0->SW_in2.in" + str(len(inputsPE) + 1))
    # arch["Module"]["PE1"]["connection"].append("CONST1.out0->SW_in2.in" + str(len(inputsPE) + 2))
    arch["Module"]["PE1"]["connection"].append("SW_in2.out0->ALU0.in2")
    if connBypass:
        for port in outputsPE: 
            arch["Module"]["PE1"]["connection"].append("ALU0.out0->SW_" + port + ".in" + str(len(inputsPE)))
            arch["Module"]["PE1"]["connection"].append("CONST0.out0->SW_" + port + ".in" + str(len(inputsPE) + 1))
            # arch["Module"]["PE1"]["connection"].append("CONST1.out0->SW_" + port + ".in" + str(len(inputsPE) + 2))
            arch["Module"]["PE1"]["connection"].append("SW_" + port + ".out0->" + port)
    else: 
        for port in outputsPE: 
            arch["Module"]["PE1"]["connection"].append("ALU0.out0->" + port)
    
    # Memory
    inputsMem = ["in0", ]
    for idx in range(1, cols + 1, interMem): 
        inputsMem.append("in" + str(idx))
    arch["Module"]["MEMORY"]["input"].extend(inputsMem)

    sizeSwitchMem = len(inputsMem)
    for idx in range(sizeSwitchMem): 
        arch["Switch"]["FULLYCONN_MEM"]["input"].append("in" + str(idx))
        arch["Switch"]["FULLYCONN_MEM"]["required"].append("in" + str(idx) + "->out0")
    
    for idx in range(len(inputsMem)): 
        arch["Module"]["MEMORY"]["connection"].append(inputsMem[idx] + "->SW_addr.in" + str(idx))
    arch["Module"]["MEMORY"]["connection"].append("SW_addr.out0->MEM0.in0")
    for idx in range(len(inputsMem)): 
        arch["Module"]["MEMORY"]["connection"].append(inputsMem[idx] + "->SW_din.in" + str(idx))
    arch["Module"]["MEMORY"]["connection"].append("SW_din.out0->MEM0.in1")
    for idx in range(len(inputsMem)): 
        arch["Module"]["MEMORY"]["connection"].append(inputsMem[idx] + "->SW_ctr.in" + str(idx))
    arch["Module"]["MEMORY"]["connection"].append("SW_ctr.out0->MEM0.in2")
    arch["Module"]["MEMORY"]["connection"].append("MEM0.out0->out0")
    
    # IO
    inputsIO = ["in0", ]
    for idx in range(1, rows + 1, interIO): 
        inputsIO.append("in" + str(idx))
    arch["Module"]["IOPAD"]["input"].extend(inputsIO)
    
    sizeSwitchIO = len(inputsIO)
    for idx in range(sizeSwitchIO): 
        arch["Switch"]["FULLYCONN_IO"]["input"].append("in" + str(idx))
        arch["Switch"]["FULLYCONN_IO"]["required"].append("in" + str(idx) + "->out0")

    for idx in range(len(inputsIO)): 
        arch["Module"]["IOPAD"]["connection"].append(inputsIO[idx] + "->SW_in0.in" + str(idx))
    arch["Module"]["IOPAD"]["connection"].append("SW_in0.out0->IO0.in0")
    arch["Module"]["IOPAD"]["connection"].append("IO0.out0->out0")
    
    # Construct the array
    assert len(typePE) == rows * cols or len(typePE) == 1
    if len(typePE) == 1: 
        typePE = typePE * (rows * cols)
    listPEs = []
    for idx in range(rows): 
        for jdx in range(cols): 
            index = idx * cols + jdx
            name = "PE_" + str(idx) + "_" + str(jdx)
            listPEs.append(name)
            arch["Module"]["CGRA"]["module"][name] = typePE[index]
            assert typePE[index] in arch["Module"]
    for idx in range(rows): 
        arch["Module"]["CGRA"]["module"]["mem" + str(idx)] = "MEMORY"
    for idx in range(cols): 
        arch["Module"]["CGRA"]["module"]["io" + str(idx)] = "IOPAD"
    # Dummy units
    dummyUnits = []
    for idx in range(rows): 
        for jdx in range(cols): 
            arch["Module"]["CGRA"]["element"]["__PE_" + str(idx) + "_" + str(jdx)] = "DUMMY"
            arch["Module"]["CGRA"]["connection"].append("__PE_" + str(idx) + "_" + str(jdx) + ".out0->PE_" + str(idx) + "_" + str(jdx) + ".in2")
    for idx in range(rows): 
        arch["Module"]["CGRA"]["element"]["__mem" + str(idx)] = "DUMMY"
        arch["Module"]["CGRA"]["connection"].append("__mem" + str(idx) + ".out0->mem" + str(idx) + ".in0")
    for idx in range(cols): 
        arch["Module"]["CGRA"]["element"]["__io" + str(idx)] = "DUMMY"
        arch["Module"]["CGRA"]["connection"].append("__io" + str(idx) + ".out0->io" + str(idx) + ".in0")

    # -> IO <-> PE
    for jdx in range(cols): 
        for idx in range(0, rows, interIO): 
            index = idx * cols + jdx
            arch["Module"]["CGRA"]["connection"].append(listPEs[index] + ".out0->io" + str(jdx) + ".in" + str(idx + 1))
            arch["Module"]["CGRA"]["connection"].append("io" + str(jdx) + ".out0->" + listPEs[index] + ".in0")
    # -> MEM <-> PE
    for idx in range(rows): 
        for jdx in range(0, cols, interMem): 
            index = idx * cols + jdx
            arch["Module"]["CGRA"]["connection"].append(listPEs[index] + ".out0->mem" + str(idx) + ".in" + str(jdx + 1))
            arch["Module"]["CGRA"]["connection"].append("mem" + str(idx) + ".out0->" + listPEs[index] + ".in1")
    # PE <-> PE
    if connMesh: 
        for idx in range(rows): 
            for jdx in range(cols): 
                name = "PE_" + str(idx) + "_" + str(jdx)
                jdxMesh0 = (jdx + 1) % cols
                jdxMesh1 = (jdx - 1 + cols) % cols
                idxMesh2 = (idx + 1) % rows
                idxMesh3 = (idx - 1 + rows) % rows
                nameMesh0 = "PE_" + str(idx) + "_" + str(jdxMesh0)
                nameMesh1 = "PE_" + str(idx) + "_" + str(jdxMesh1)
                nameMesh2 = "PE_" + str(idxMesh2) + "_" + str(jdx)
                nameMesh3 = "PE_" + str(idxMesh3) + "_" + str(jdx)
                portInMesh0 = "in_mesh0"
                portInMesh1 = "in_mesh1"
                portInMesh2 = "in_mesh2"
                portInMesh3 = "in_mesh3"
                if typeConn == "HyCUBE": 
                    portOutMesh0 = "out_mesh0"
                    portOutMesh1 = "out_mesh1"
                    portOutMesh2 = "out_mesh2"
                    portOutMesh3 = "out_mesh3"
                elif typeConn == "ADRES": 
                    portOutMesh0 = "out0"
                    portOutMesh1 = "out0"
                    portOutMesh2 = "out0"
                    portOutMesh3 = "out0"
                else: 
                    assert 0, "Unsupported interconnect style"
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutMesh0 + "->" + nameMesh0 + "." + portInMesh0)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutMesh1 + "->" + nameMesh1 + "." + portInMesh1)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutMesh2 + "->" + nameMesh2 + "." + portInMesh2)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutMesh3 + "->" + nameMesh3 + "." + portInMesh3)
    if connDiag: 
        for idx in range(rows): 
            for jdx in range(cols): 
                name = "PE_" + str(idx) + "_" + str(jdx)
                jdxDiag0 = (jdx + 1) % cols
                jdxDiag1 = (jdx - 1 + cols) % cols
                idxDiag2 = (idx + 1) % rows
                idxDiag3 = (idx - 1 + rows) % rows
                nameDiag0 = "PE_" + str(idxDiag2) + "_" + str(jdxDiag0)
                nameDiag1 = "PE_" + str(idxDiag2) + "_" + str(jdxDiag1)
                nameDiag2 = "PE_" + str(idxDiag3) + "_" + str(jdxDiag0)
                nameDiag3 = "PE_" + str(idxDiag3) + "_" + str(jdxDiag1)
                portInDiag0 = "in_diag0"
                portInDiag1 = "in_diag1"
                portInDiag2 = "in_diag2"
                portInDiag3 = "in_diag3"
                if typeConn == "HyCUBE": 
                    portOutDiag0 = "out_diag0"
                    portOutDiag1 = "out_diag1"
                    portOutDiag2 = "out_diag2"
                    portOutDiag3 = "out_diag3"
                elif typeConn == "ADRES": 
                    portOutDiag0 = "out0"
                    portOutDiag1 = "out0"
                    portOutDiag2 = "out0"
                    portOutDiag3 = "out0"
                else: 
                    assert 0, "Unsupported interconnect style"
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutDiag0 + "->" + nameDiag0 + "." + portInDiag0)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutDiag1 + "->" + nameDiag1 + "." + portInDiag1)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutDiag2 + "->" + nameDiag2 + "." + portInDiag2)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutDiag3 + "->" + nameDiag3 + "." + portInDiag3)
    if connOnehop: 
        for idx in range(rows): 
            for jdx in range(cols): 
                name = "PE_" + str(idx) + "_" + str(jdx)
                jdxOnehop0 = (jdx + 2) % cols
                jdxOnehop1 = (jdx - 2 + cols) % cols
                idxOnehop2 = (idx + 2) % rows
                idxOnehop3 = (idx - 2 + rows) % rows
                nameOnehop0 = "PE_" + str(idx) + "_" + str(jdxOnehop0)
                nameOnehop1 = "PE_" + str(idx) + "_" + str(jdxOnehop1)
                nameOnehop2 = "PE_" + str(idxOnehop2) + "_" + str(jdx)
                nameOnehop3 = "PE_" + str(idxOnehop3) + "_" + str(jdx)
                portInOnehop0 = "in_onehop0"
                portInOnehop1 = "in_onehop1"
                portInOnehop2 = "in_onehop2"
                portInOnehop3 = "in_onehop3"
                if typeConn == "HyCUBE": 
                    portOutOnehop0 = "out_onehop0"
                    portOutOnehop1 = "out_onehop1"
                    portOutOnehop2 = "out_onehop2"
                    portOutOnehop3 = "out_onehop3"
                elif typeConn == "ADRES": 
                    portOutOnehop0 = "out0"
                    portOutOnehop1 = "out0"
                    portOutOnehop2 = "out0"
                    portOutOnehop3 = "out0"
                else: 
                    assert 0, "Unsupported interconnect style"
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutOnehop0 + "->" + nameOnehop0 + "." + portInOnehop0)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutOnehop1 + "->" + nameOnehop1 + "." + portInOnehop1)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutOnehop2 + "->" + nameOnehop2 + "." + portInOnehop2)
                arch["Module"]["CGRA"]["connection"].append(name + "." + portOutOnehop3 + "->" + nameOnehop3 + "." + portInOnehop3)

    arch["Module"]["TOP"] = {
        "input": [

        ], 
        "output": [
            
        ], 
        "module": {
            "CGRA0": "CGRA", 
        }, 
        "element": {
            
        }, 
        "switch": {
            
        }, 
        "connection": [

        ]
    }
    
    return arch

def gencoord(sizeArray, typePE): 
    results = []

    # Size
    rows = sizeArray[0]
    cols = sizeArray[1]

    # Construct the array
    assert len(typePE) == rows * cols or len(typePE) == 1
    if len(typePE) == 1: 
        typePE = typePE * (rows * cols)
    listPEs = []
    for idx in range(rows): 
        for jdx in range(cols): 
            index = idx * cols + jdx
            name = "PE_" + str(idx) + "_" + str(jdx)
            listPEs.append(name)
            results.append("CGRA0." + name + ".ALU0   ALU   " + str(idx) + " " + str(jdx))
            results.append("CGRA0." + name + ".CONST0 CONST " + str(idx) + " " + str(jdx))
            # results.append("CGRA0." + name + ".CONST1 CONST " + str(idx) + " " + str(jdx))
    for idx in range(rows): 
        results.append("CGRA0.mem" + str(idx) + ".MEM0 MEM " + str(idx) + " " + str(-1))
    for idx in range(cols): 
        results.append("CGRA0.io" + str(idx) + ".IO0 IO " + str(-1) + " " + str(idx))
    # Dummy units
    dummyUnits = []
    for idx in range(rows): 
        for jdx in range(cols): 
            name = "__PE_" + str(idx) + "_" + str(jdx)
            listPEs.append(name)
            results.append("CGRA0." + name + " DUMMY " + str(idx) + " " + str(jdx))
    for idx in range(rows): 
        results.append("CGRA0.__mem" + str(idx) + " DUMMY " + str(idx) + " " + str(-1))
    for idx in range(cols): 
        results.append("CGRA0.__io" + str(idx) + " DUMMY " + str(-1) + " " + str(idx))

    return results
    
if __name__ == "__main__": 
    sizeArray = [4, 4]
    typePE = ["PE1"] * (sizeArray[0] * sizeArray[1])
    typeConn = "ADRES"
    connMesh = True
    connDiag = False
    connOnehop = False
    connBypass = True
    interMem = 1
    interIO = 1
    arch = genarch(sizeArray, typePE, typeConn, connMesh, connDiag, connOnehop, connBypass, interMem, interIO)
    with open("./arch/arch.json", "w") as fout: 
        fout.write(json.dumps(arch, indent=4))
        
    coord = gencoord(sizeArray, typePE)
    with open("./arch/coord.txt", "w") as fout: 
        for line in coord: 
            fout.write(line + "\n")



