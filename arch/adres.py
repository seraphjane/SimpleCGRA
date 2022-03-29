import sys 
sys.path.append(".")

import xmltodict
import json

import arch.arch as ac
import dataflow.dataflow as df
import dataflow.funcmap as fm

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
        "INPUT": {"input": ["in0", ], "output": ["out0", ], 
                  "function": {"FUNC_INPUT0": "__INPUT__", }, 
                  "pattern": {"PATN_INPUT0": {"unit": ["FUNC_INPUT0", ], 
                                              "port": {"in0": "FUNC_INPUT0.in0", 
                                                       "out0": "FUNC_INPUT0.out0"}, 
                                              "connection": [], }, }, 
                  "compat": {}, }, 
        "OUTPUT": {"input": ["in0", ], "output": ["out0", ], 
                  "function": {"FUNC_OUTPUT0": "__OUTPUT__", }, 
                  "pattern": {"PATN_OUTPUT0": {"unit": ["FUNC_OUTPUT0", ], 
                                              "port": {"in0": "FUNC_OUTPUT0.in0", 
                                                       "out0": "FUNC_OUTPUT0.out0"}, 
                                              "connection": [], }, }, 
                  "compat": {}, }, 
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
                             "FUNC_SEL0":  "__JOIN2__", }, 
                "pattern": {"PATN_SEL0": {"unit": ["FUNC_SEL0", ], 
                                          "port": {"in0": "FUNC_SEL0.in0", 
                                                   "in1": "FUNC_SEL0.in1", 
                                                   "in2": "FUNC_SEL0.select", 
                                                   "out0": "FUNC_SEL0.out0"}, 
                                          "connection": [], }, 
                            "PATN_ADD0": {"unit": ["FUNC_ADD0", ], 
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
    }

    arch["Module"] = {
        "PE": {
            "input": [
                "in0", "in1", "in2", "in3", "in4", "in5", "in6", "in7", 
            ], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "ALU0": "ALU", 
                "CONST0": "CONST", 
            }, 
            "switch": {
                "SW10X1_in0": "FULLYCONN_10X1", 
                "SW10X1_in1": "FULLYCONN_10X1", 
                "SW10X1_in2": "FULLYCONN_10X1", 
                "SW10X1_out0": "FULLYCONN_10X1", 
            }, 
            "connection": [
                # CONST -> ALU
                # SW10X1_in0
                "in0->SW10X1_in0.in0",
                "in1->SW10X1_in0.in1",
                "in2->SW10X1_in0.in2",
                "in3->SW10X1_in0.in3",
                "in4->SW10X1_in0.in4",
                "in5->SW10X1_in0.in5",
                "in6->SW10X1_in0.in6",
                "in7->SW10X1_in0.in7",
                "ALU0.out0->SW10X1_in0.in8",
                "CONST0.out0->SW10X1_in0.in9",
                "SW10X1_in0.out0->ALU0.in0",
                # SW10X1_in1
                "in0->SW10X1_in1.in0",
                "in1->SW10X1_in1.in1",
                "in2->SW10X1_in1.in2",
                "in3->SW10X1_in1.in3",
                "in4->SW10X1_in1.in4",
                "in5->SW10X1_in1.in5",
                "in6->SW10X1_in1.in6",
                "in7->SW10X1_in1.in7",
                "ALU0.out0->SW10X1_in1.in8",
                "CONST0.out0->SW10X1_in1.in9",
                "SW10X1_in1.out0->ALU0.in1",
                # SW10X1_in2
                "in0->SW10X1_in2.in0",
                "in1->SW10X1_in2.in1",
                "in2->SW10X1_in2.in2",
                "in3->SW10X1_in2.in3",
                "in4->SW10X1_in2.in4",
                "in5->SW10X1_in2.in5",
                "in6->SW10X1_in2.in6",
                "in7->SW10X1_in2.in7",
                "ALU0.out0->SW10X1_in2.in8",
                "CONST0.out0->SW10X1_in2.in9",
                "SW10X1_in2.out0->ALU0.in2",
                # SW9X1_out0
                "in0->SW10X1_out0.in0",
                "in1->SW10X1_out0.in1",
                "in2->SW10X1_out0.in2",
                "in3->SW10X1_out0.in3",
                "in4->SW10X1_out0.in4",
                "in5->SW10X1_out0.in5",
                "in6->SW10X1_out0.in6",
                "in7->SW10X1_out0.in7",
                "ALU0.out0->SW10X1_out0.in8",
                # "CONST0.out0->SW10X1_out0.in9",
                "SW10X1_out0.out0->out0",
            ]
        }, 
        "MEMORY": {
            "input": [
                "in0", "in1", "in2", "in3", "in4", "in5", 
            ], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "MEM0": "MEM", 
            }, 
            "switch": {
                "SW6X1_addr": "FULLYCONN_6X1", 
                "SW6X1_din": "FULLYCONN_6X1", 
                "SW6X1_ctr": "FULLYCONN_6X1", 
                "SW2X1_out0": "FULLYCONN_2X1", 
            }, 
            "connection": [
                # SW6X1_addr
                "in0->SW6X1_addr.in0",
                "in1->SW6X1_addr.in1",
                "in2->SW6X1_addr.in2",
                "in3->SW6X1_addr.in3",
                "in4->SW6X1_addr.in4",
                "in5->SW6X1_addr.in5",
                "SW6X1_addr.out0->MEM0.in0",
                # SW6X1_din
                "in0->SW6X1_din.in0",
                "in1->SW6X1_din.in1",
                "in2->SW6X1_din.in2",
                "in3->SW6X1_din.in3",
                "in4->SW6X1_din.in4",
                "in5->SW6X1_din.in5",
                "SW6X1_din.out0->MEM0.in1",
                # SW6X1_ctr
                "in0->SW6X1_ctr.in0",
                "in1->SW6X1_ctr.in1",
                "in2->SW6X1_ctr.in2",
                "in3->SW6X1_ctr.in3",
                "in4->SW6X1_ctr.in4",
                "in5->SW6X1_ctr.in5",
                "SW6X1_ctr.out0->MEM0.in2",
                # out0
                "in5->SW2X1_out0.in0", 
                "MEM0.out0->SW2X1_out0.in1", 
                "SW2X1_out0.out0->out0", 
            ]
        }, 
        "INPAD": {
            "input": [
                "in0", "in1", "in2", "in3", "in4", "in5", 
            ], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "INPUT0": "INPUT", 
            }, 
            "switch": {
                "SW6X1_in0": "FULLYCONN_6X1", 
                "SW2X1_out0": "FULLYCONN_2X1", 
            }, 
            "connection": [
                # SW6X1_in0
                "in0->SW6X1_in0.in0",
                "in1->SW6X1_in0.in1",
                "in2->SW6X1_in0.in2",
                "in3->SW6X1_in0.in3",
                "in4->SW6X1_in0.in4",
                "in5->SW6X1_in0.in5",
                "SW6X1_in0.out0->INPUT0.in0", 
                # dout
                "in5->SW2X1_out0.in0", 
                "INPUT0.out0->SW2X1_out0.in1", 
                "SW2X1_out0.out0->out0", 
            ]
        }, 
        "OUTPAD": {
            "input": [
                "in0", "in1", "in2", "in3", "in4", "in5", 
            ], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "OUTPUT0": "OUTPUT", 
            }, 
            "switch": {
                "SW6X1_in0": "FULLYCONN_6X1", 
                "SW2X1_out0": "FULLYCONN_2X1", 
            }, 
            "connection": [
                # SW6X1_in0
                "in0->SW6X1_in0.in0",
                "in1->SW6X1_in0.in1",
                "in2->SW6X1_in0.in2",
                "in3->SW6X1_in0.in3",
                "in4->SW6X1_in0.in4",
                "in5->SW6X1_in0.in4",
                "SW6X1_in0.out0->OUTPUT0.in0", 
                # dout
                "in5->SW2X1_out0.in0", 
                "OUTPUT0.out0->SW2X1_out0.in1", 
                "SW2X1_out0.out0->out0", 
            ]
        }, 
        "IOPAD": {
            "input": [
                "in0", "in1", "in2", "in3", "in4", "in5", 
            ], 
            "output": [
                "out0", 
            ], 
            "module": {}, 
            "element": {
                "IO0": "IO", 
            }, 
            "switch": {
                "SW6X1_in0": "FULLYCONN_6X1", 
                "SW2X1_out0": "FULLYCONN_2X1", 
            }, 
            "connection": [
                # SW6X1_in0
                "in0->SW6X1_in0.in0",
                "in1->SW6X1_in0.in1",
                "in2->SW6X1_in0.in2",
                "in3->SW6X1_in0.in3",
                "in4->SW6X1_in0.in4",
                "in5->SW6X1_in0.in5",
                "SW6X1_in0.out0->IO0.in0", 
                # dout
                "in5->SW2X1_out0.in0", 
                "IO0.out0->SW2X1_out0.in1", 
                "SW2X1_out0.out0->out0", 
            ]
        }, 
    }

    return arch

def _baseADRES(): 
    arch = _templateSimple()
    arch["Module"]["CGRA"] = {
        "input": [
            
        ], 
        "output": [
            
        ], 
        "module": {
            "PE_0_0": "PE", "PE_0_1": "PE", "PE_0_2": "PE", "PE_0_3": "PE", 
            "PE_1_0": "PE", "PE_1_1": "PE", "PE_1_2": "PE", "PE_1_3": "PE", 
            "PE_2_0": "PE", "PE_2_1": "PE", "PE_2_2": "PE", "PE_2_3": "PE", 
            "PE_3_0": "PE", "PE_3_1": "PE", "PE_3_2": "PE", "PE_3_3": "PE", 
            "mem0": "MEMORY", 
            "mem1": "MEMORY", 
            "mem2": "MEMORY", 
            "mem3": "MEMORY", 
            "io0": "IOPAD", 
            "io1": "IOPAD", 
            "io2": "IOPAD", 
            "io3": "IOPAD",  
        }, 
        "element": {
            
        }, 
        "switch": {
            
        }, 
        "connection": [
            # Inputs -> PEs
            "io0.out0->PE_0_0.in4", 
            "io0.out0->PE_1_0.in4", 
            "io0.out0->PE_2_0.in4", 
            "io0.out0->PE_3_0.in4", 
            "io1.out0->PE_0_1.in4", 
            "io1.out0->PE_1_1.in4", 
            "io1.out0->PE_2_1.in4", 
            "io1.out0->PE_3_1.in4", 
            "io2.out0->PE_0_2.in4", 
            "io2.out0->PE_1_2.in4", 
            "io2.out0->PE_2_2.in4", 
            "io2.out0->PE_3_2.in4", 
            "io3.out0->PE_0_3.in4", 
            "io3.out0->PE_1_3.in4", 
            "io3.out0->PE_2_3.in4", 
            "io3.out0->PE_3_3.in4", 
            # PEs -> Outputs
            "PE_0_0.out0->io0.in0", 
            "PE_1_0.out0->io0.in1", 
            "PE_2_0.out0->io0.in2", 
            "PE_3_0.out0->io0.in3", 
            "PE_0_1.out0->io1.in0", 
            "PE_1_1.out0->io1.in1", 
            "PE_2_1.out0->io1.in2", 
            "PE_3_1.out0->io1.in3", 
            "PE_0_2.out0->io2.in0", 
            "PE_1_2.out0->io2.in1", 
            "PE_2_2.out0->io2.in2", 
            "PE_3_2.out0->io2.in3", 
            "PE_0_3.out0->io3.in0", 
            "PE_1_3.out0->io3.in1", 
            "PE_2_3.out0->io3.in2", 
            "PE_3_3.out0->io3.in3", 
            # PEs -> MEMs
            "PE_0_0.out0->mem0.in0", 
            "PE_0_1.out0->mem0.in1", 
            "PE_0_2.out0->mem0.in2", 
            "PE_0_3.out0->mem0.in3", 
            "PE_1_0.out0->mem1.in0", 
            "PE_1_1.out0->mem1.in1", 
            "PE_1_2.out0->mem1.in2", 
            "PE_1_3.out0->mem1.in3", 
            "PE_2_0.out0->mem2.in0", 
            "PE_2_1.out0->mem2.in1", 
            "PE_2_2.out0->mem2.in2", 
            "PE_2_3.out0->mem2.in3", 
            "PE_3_0.out0->mem3.in0", 
            "PE_3_1.out0->mem3.in1", 
            "PE_3_2.out0->mem3.in2", 
            "PE_3_3.out0->mem3.in3", 
            # MEMs -> PEs
            "mem0.out0->PE_0_0.in5", 
            "mem0.out0->PE_0_1.in5", 
            "mem0.out0->PE_0_2.in5", 
            "mem0.out0->PE_0_3.in5", 
            "mem1.out0->PE_1_0.in5", 
            "mem1.out0->PE_1_1.in5", 
            "mem1.out0->PE_1_2.in5", 
            "mem1.out0->PE_1_3.in5", 
            "mem2.out0->PE_2_0.in5", 
            "mem2.out0->PE_2_1.in5", 
            "mem2.out0->PE_2_2.in5", 
            "mem2.out0->PE_2_3.in5", 
            "mem3.out0->PE_3_0.in5", 
            "mem3.out0->PE_3_1.in5", 
            "mem3.out0->PE_3_2.in5", 
            "mem3.out0->PE_3_3.in5", 
            # PEs -> PEs, left -> right
            "PE_0_0.out0->PE_0_1.in0", 
            "PE_0_1.out0->PE_0_2.in0", 
            "PE_0_2.out0->PE_0_3.in0", 
            "PE_0_3.out0->PE_0_0.in0", 
            "PE_1_0.out0->PE_1_1.in0", 
            "PE_1_1.out0->PE_1_2.in0", 
            "PE_1_2.out0->PE_1_3.in0", 
            "PE_1_3.out0->PE_1_0.in0", 
            "PE_2_0.out0->PE_2_1.in0", 
            "PE_2_1.out0->PE_2_2.in0", 
            "PE_2_2.out0->PE_2_3.in0", 
            "PE_2_3.out0->PE_2_0.in0", 
            "PE_3_0.out0->PE_3_1.in0", 
            "PE_3_1.out0->PE_3_2.in0", 
            "PE_3_2.out0->PE_3_3.in0", 
            "PE_3_3.out0->PE_3_0.in0", 
            # PEs -> PEs, right -> left
            "PE_0_1.out0->PE_0_0.in1", 
            "PE_0_2.out0->PE_0_1.in1", 
            "PE_0_3.out0->PE_0_2.in1", 
            "PE_0_0.out0->PE_0_3.in1", 
            "PE_1_1.out0->PE_1_0.in1", 
            "PE_1_2.out0->PE_1_1.in1", 
            "PE_1_3.out0->PE_1_2.in1", 
            "PE_1_0.out0->PE_1_3.in1", 
            "PE_2_1.out0->PE_2_0.in1", 
            "PE_2_2.out0->PE_2_1.in1", 
            "PE_2_3.out0->PE_2_2.in1", 
            "PE_2_0.out0->PE_2_3.in1", 
            "PE_3_1.out0->PE_3_0.in1", 
            "PE_3_2.out0->PE_3_1.in1", 
            "PE_3_3.out0->PE_3_2.in1", 
            "PE_3_0.out0->PE_3_3.in1", 
            # PEs -> PEs, up -> down
            "PE_0_0.out0->PE_1_0.in2", 
            "PE_1_0.out0->PE_2_0.in2", 
            "PE_2_0.out0->PE_3_0.in2", 
            "PE_3_0.out0->PE_0_0.in2", 
            "PE_0_1.out0->PE_1_1.in2", 
            "PE_1_1.out0->PE_2_1.in2", 
            "PE_2_1.out0->PE_3_1.in2", 
            "PE_3_1.out0->PE_0_1.in2", 
            "PE_0_2.out0->PE_1_2.in2", 
            "PE_1_2.out0->PE_2_2.in2", 
            "PE_2_2.out0->PE_3_2.in2", 
            "PE_3_2.out0->PE_0_2.in2", 
            "PE_0_3.out0->PE_1_3.in2", 
            "PE_1_3.out0->PE_2_3.in2", 
            "PE_2_3.out0->PE_3_3.in2", 
            "PE_3_3.out0->PE_0_3.in2", 
            # PEs -> PEs, down -> up
            "PE_1_0.out0->PE_0_0.in3", 
            "PE_2_0.out0->PE_1_0.in3", 
            "PE_3_0.out0->PE_2_0.in3", 
            "PE_0_0.out0->PE_3_0.in3", 
            "PE_1_1.out0->PE_0_1.in3", 
            "PE_2_1.out0->PE_1_1.in3", 
            "PE_3_1.out0->PE_2_1.in3", 
            "PE_0_1.out0->PE_3_1.in3", 
            "PE_1_2.out0->PE_0_2.in3", 
            "PE_2_2.out0->PE_1_2.in3", 
            "PE_3_2.out0->PE_2_2.in3", 
            "PE_0_2.out0->PE_3_2.in3", 
            "PE_1_3.out0->PE_0_3.in3", 
            "PE_2_3.out0->PE_1_3.in3", 
            "PE_3_3.out0->PE_2_3.in3", 
            "PE_0_3.out0->PE_3_3.in3", 
        ]
    }

    return arch

def _baseHyCUBE(): 
    arch = _templateSimple()
    arch["Switch"]["CB"] = {
        "input":  ["in0", "in1", "in2", "in3", "in4", ], 
        "output": ["out0", "out1", "out2", "out3", ], 
        "required": ["in0->out0", "in1->out0", "in2->out0", "in3->out0", "in4->out0", 
                     "in0->out1", "in1->out1", "in2->out1", "in3->out1", "in4->out1", 
                     "in0->out2", "in1->out2", "in2->out2", "in3->out2", "in4->out2", 
                     "in0->out3", "in1->out3", "in2->out3", "in3->out3", "in4->out3", ], 
        "graph": "", 
    }
    arch["Module"]["CGRA"] = {
        "input": [
            "in_0_0", "in_0_1", "in_0_2", "in_0_3", 
            "in_1_0", "in_1_1", "in_1_2", "in_1_3", 
            "in_2_0", "in_2_1", "in_2_2", "in_2_3", 
            "in_3_0", "in_3_1", "in_3_2", "in_3_3", 
            "in_mem0", "in_mem1", "in_mem2", "in_mem3", 
        ], 
        "output": [
            "out_0_0", "out_0_1", "out_0_2", "out_0_3", 
            "out_1_0", "out_1_1", "out_1_2", "out_1_3", 
            "out_2_0", "out_2_1", "out_2_2", "out_2_3", 
            "out_3_0", "out_3_1", "out_3_2", "out_3_3", 
            "out_mem0", "out_mem1", "out_mem2", "out_mem3", 
        ], 
        "module": {
            "PE_0_0": "PE", "PE_0_1": "PE", "PE_0_2": "PE", "PE_0_3": "PE", 
            "PE_1_0": "PE", "PE_1_1": "PE", "PE_1_2": "PE", "PE_1_3": "PE", 
            "PE_2_0": "PE", "PE_2_1": "PE", "PE_2_2": "PE", "PE_2_3": "PE", 
            "PE_3_0": "PE", "PE_3_1": "PE", "PE_3_2": "PE", "PE_3_3": "PE", 
            "mem0": "MEMORY", 
            "mem1": "MEMORY", 
            "mem2": "MEMORY", 
            "mem3": "MEMORY", 
            "io0": "IOPAD", 
            "io1": "IOPAD", 
            "io2": "IOPAD", 
            "io3": "IOPAD", 
        }, 
        "element": {

        }, 
        "switch": {
            "CB_0_0": "CB", "CB_0_1": "CB", "CB_0_2": "CB", "CB_0_3": "CB", 
            "CB_1_0": "CB", "CB_1_1": "CB", "CB_1_2": "CB", "CB_1_3": "CB", 
            "CB_2_0": "CB", "CB_2_1": "CB", "CB_2_2": "CB", "CB_2_3": "CB", 
            "CB_3_0": "CB", "CB_3_1": "CB", "CB_3_2": "CB", "CB_3_3": "CB", 
        }, 
        "connection": [
            # Inputs -> PEs
            "io0.out0->PE_0_0.in4", 
            "io0.out0->PE_1_0.in4", 
            "io0.out0->PE_2_0.in4", 
            "io0.out0->PE_3_0.in4", 
            "io1.out0->PE_0_1.in4", 
            "io1.out0->PE_1_1.in4", 
            "io1.out0->PE_2_1.in4", 
            "io1.out0->PE_3_1.in4", 
            "io2.out0->PE_0_2.in4", 
            "io2.out0->PE_1_2.in4", 
            "io2.out0->PE_2_2.in4", 
            "io2.out0->PE_3_2.in4", 
            "io3.out0->PE_0_3.in4", 
            "io3.out0->PE_1_3.in4", 
            "io3.out0->PE_2_3.in4", 
            "io3.out0->PE_3_3.in4", 
            # PEs -> Outputs
            "PE_0_0.out0->io0.in0", 
            "PE_1_0.out0->io0.in1", 
            "PE_2_0.out0->io0.in2", 
            "PE_3_0.out0->io0.in3", 
            "PE_0_1.out0->io1.in0", 
            "PE_1_1.out0->io1.in1", 
            "PE_2_1.out0->io1.in2", 
            "PE_3_1.out0->io1.in3", 
            "PE_0_2.out0->io2.in0", 
            "PE_1_2.out0->io2.in1", 
            "PE_2_2.out0->io2.in2", 
            "PE_3_2.out0->io2.in3", 
            "PE_0_3.out0->io3.in0", 
            "PE_1_3.out0->io3.in1", 
            "PE_2_3.out0->io3.in2", 
            "PE_3_3.out0->io3.in3", 
            # PEs -> MEMs
            "PE_0_0.out0->mem0.in0", 
            "PE_0_1.out0->mem0.in1", 
            "PE_0_2.out0->mem0.in2", 
            "PE_0_3.out0->mem0.in3", 
            "PE_1_0.out0->mem1.in0", 
            "PE_1_1.out0->mem1.in1", 
            "PE_1_2.out0->mem1.in2", 
            "PE_1_3.out0->mem1.in3", 
            "PE_2_0.out0->mem2.in0", 
            "PE_2_1.out0->mem2.in1", 
            "PE_2_2.out0->mem2.in2", 
            "PE_2_3.out0->mem2.in3", 
            "PE_3_0.out0->mem3.in0", 
            "PE_3_1.out0->mem3.in1", 
            "PE_3_2.out0->mem3.in2", 
            "PE_3_3.out0->mem3.in3", 
            # MEMs -> PEs
            "mem0.out0->PE_0_0.in5", 
            "mem0.out0->PE_0_1.in5", 
            "mem0.out0->PE_0_2.in5", 
            "mem0.out0->PE_0_3.in5", 
            "mem1.out0->PE_1_0.in5", 
            "mem1.out0->PE_1_1.in5", 
            "mem1.out0->PE_1_2.in5", 
            "mem1.out0->PE_1_3.in5", 
            "mem2.out0->PE_2_0.in5", 
            "mem2.out0->PE_2_1.in5", 
            "mem2.out0->PE_2_2.in5", 
            "mem2.out0->PE_2_3.in5", 
            "mem3.out0->PE_3_0.in5", 
            "mem3.out0->PE_3_1.in5", 
            "mem3.out0->PE_3_2.in5", 
            "mem3.out0->PE_3_3.in5", 
            # PEs -> CBs
            "PE_0_0.in0->CB_0_0.in0", 
            "PE_0_0.in1->CB_0_0.in1", 
            "PE_0_0.in2->CB_0_0.in2", 
            "PE_0_0.in3->CB_0_0.in3", 
            "PE_0_0.out0->CB_0_0.in4", 
            "PE_0_1.in0->CB_0_1.in0", 
            "PE_0_1.in1->CB_0_1.in1", 
            "PE_0_1.in2->CB_0_1.in2", 
            "PE_0_1.in3->CB_0_1.in3", 
            "PE_0_1.out0->CB_0_1.in4", 
            "PE_0_2.in0->CB_0_2.in0", 
            "PE_0_2.in1->CB_0_2.in1", 
            "PE_0_2.in2->CB_0_2.in2", 
            "PE_0_2.in3->CB_0_2.in3", 
            "PE_0_2.out0->CB_0_2.in4", 
            "PE_0_3.in0->CB_0_3.in0", 
            "PE_0_3.in1->CB_0_3.in1", 
            "PE_0_3.in2->CB_0_3.in2", 
            "PE_0_3.in3->CB_0_3.in3", 
            "PE_0_3.out0->CB_0_3.in4", 
            "PE_1_0.in0->CB_1_0.in0", 
            "PE_1_0.in1->CB_1_0.in1", 
            "PE_1_0.in2->CB_1_0.in2", 
            "PE_1_0.in3->CB_1_0.in3", 
            "PE_1_0.out0->CB_1_0.in4", 
            "PE_1_1.in0->CB_1_1.in0", 
            "PE_1_1.in1->CB_1_1.in1", 
            "PE_1_1.in2->CB_1_1.in2", 
            "PE_1_1.in3->CB_1_1.in3", 
            "PE_1_1.out0->CB_1_1.in4", 
            "PE_1_2.in0->CB_1_2.in0", 
            "PE_1_2.in1->CB_1_2.in1", 
            "PE_1_2.in2->CB_1_2.in2", 
            "PE_1_2.in3->CB_1_2.in3", 
            "PE_1_2.out0->CB_1_2.in4", 
            "PE_1_3.in0->CB_1_3.in0", 
            "PE_1_3.in1->CB_1_3.in1", 
            "PE_1_3.in2->CB_1_3.in2", 
            "PE_1_3.in3->CB_1_3.in3", 
            "PE_1_3.out0->CB_1_3.in4", 
            "PE_2_0.in0->CB_2_0.in0", 
            "PE_2_0.in1->CB_2_0.in1", 
            "PE_2_0.in2->CB_2_0.in2", 
            "PE_2_0.in3->CB_2_0.in3", 
            "PE_2_0.out0->CB_2_0.in4", 
            "PE_2_1.in0->CB_2_1.in0", 
            "PE_2_1.in1->CB_2_1.in1", 
            "PE_2_1.in2->CB_2_1.in2", 
            "PE_2_1.in3->CB_2_1.in3", 
            "PE_2_1.out0->CB_2_1.in4", 
            "PE_2_2.in0->CB_2_2.in0", 
            "PE_2_2.in1->CB_2_2.in1", 
            "PE_2_2.in2->CB_2_2.in2", 
            "PE_2_2.in3->CB_2_2.in3", 
            "PE_2_2.out0->CB_2_2.in4", 
            "PE_2_3.in0->CB_2_3.in0", 
            "PE_2_3.in1->CB_2_3.in1", 
            "PE_2_3.in2->CB_2_3.in2", 
            "PE_2_3.in3->CB_2_3.in3", 
            "PE_2_3.out0->CB_2_3.in4", 
            "PE_3_0.in0->CB_3_0.in0", 
            "PE_3_0.in1->CB_3_0.in1", 
            "PE_3_0.in2->CB_3_0.in2", 
            "PE_3_0.in3->CB_3_0.in3", 
            "PE_3_0.out0->CB_3_0.in4", 
            "PE_3_1.in0->CB_3_1.in0", 
            "PE_3_1.in1->CB_3_1.in1", 
            "PE_3_1.in2->CB_3_1.in2", 
            "PE_3_1.in3->CB_3_1.in3", 
            "PE_3_1.out0->CB_3_1.in4", 
            "PE_3_2.in0->CB_3_2.in0", 
            "PE_3_2.in1->CB_3_2.in1", 
            "PE_3_2.in2->CB_3_2.in2", 
            "PE_3_2.in3->CB_3_2.in3", 
            "PE_3_2.out0->CB_3_2.in4", 
            "PE_3_3.in0->CB_3_3.in0", 
            "PE_3_3.in1->CB_3_3.in1", 
            "PE_3_3.in2->CB_3_3.in2", 
            "PE_3_3.in3->CB_3_3.in3", 
            "PE_3_3.out0->CB_3_3.in4", 
            # CBs -> PEs, left -> right
            "CB_0_0.out0->PE_0_1.in0", 
            "CB_0_1.out0->PE_0_2.in0", 
            "CB_0_2.out0->PE_0_3.in0", 
            "CB_0_3.out0->PE_0_0.in0", 
            "CB_1_0.out0->PE_1_1.in0", 
            "CB_1_1.out0->PE_1_2.in0", 
            "CB_1_2.out0->PE_1_3.in0", 
            "CB_1_3.out0->PE_1_0.in0", 
            "CB_2_0.out0->PE_2_1.in0", 
            "CB_2_1.out0->PE_2_2.in0", 
            "CB_2_2.out0->PE_2_3.in0", 
            "CB_2_3.out0->PE_2_0.in0", 
            "CB_3_0.out0->PE_3_1.in0", 
            "CB_3_1.out0->PE_3_2.in0", 
            "CB_3_2.out0->PE_3_3.in0", 
            "CB_3_3.out0->PE_3_0.in0", 
            # PEs -> PEs, right -> left
            "CB_0_1.out1->PE_0_0.in1", 
            "CB_0_2.out1->PE_0_1.in1", 
            "CB_0_3.out1->PE_0_2.in1", 
            "CB_0_0.out1->PE_0_3.in1", 
            "CB_1_1.out1->PE_1_0.in1", 
            "CB_1_2.out1->PE_1_1.in1", 
            "CB_1_3.out1->PE_1_2.in1", 
            "CB_1_0.out1->PE_1_3.in1", 
            "CB_2_1.out1->PE_2_0.in1", 
            "CB_2_2.out1->PE_2_1.in1", 
            "CB_2_3.out1->PE_2_2.in1", 
            "CB_2_0.out1->PE_2_3.in1", 
            "CB_3_1.out1->PE_3_0.in1", 
            "CB_3_2.out1->PE_3_1.in1", 
            "CB_3_3.out1->PE_3_2.in1", 
            "CB_3_0.out1->PE_3_3.in1", 
            # PEs -> PEs, up -> down
            "CB_0_0.out2->PE_1_0.in2", 
            "CB_1_0.out2->PE_2_0.in2", 
            "CB_2_0.out2->PE_3_0.in2", 
            "CB_3_0.out2->PE_0_0.in2", 
            "CB_0_1.out2->PE_1_1.in2", 
            "CB_1_1.out2->PE_2_1.in2", 
            "CB_2_1.out2->PE_3_1.in2", 
            "CB_3_1.out2->PE_0_1.in2", 
            "CB_0_2.out2->PE_1_2.in2", 
            "CB_1_2.out2->PE_2_2.in2", 
            "CB_2_2.out2->PE_3_2.in2", 
            "CB_3_2.out2->PE_0_2.in2", 
            "CB_0_3.out2->PE_1_3.in2", 
            "CB_1_3.out2->PE_2_3.in2", 
            "CB_2_3.out2->PE_3_3.in2", 
            "CB_3_3.out2->PE_0_3.in2", 
            # PEs -> PEs, down -> up
            "CB_1_0.out3->PE_0_0.in3", 
            "CB_2_0.out3->PE_1_0.in3", 
            "CB_3_0.out3->PE_2_0.in3", 
            "CB_0_0.out3->PE_3_0.in3", 
            "CB_1_1.out3->PE_0_1.in3", 
            "CB_2_1.out3->PE_1_1.in3", 
            "CB_3_1.out3->PE_2_1.in3", 
            "CB_0_1.out3->PE_3_1.in3", 
            "CB_1_2.out3->PE_0_2.in3", 
            "CB_2_2.out3->PE_1_2.in3", 
            "CB_3_2.out3->PE_2_2.in3", 
            "CB_0_2.out3->PE_3_2.in3", 
            "CB_1_3.out3->PE_0_3.in3", 
            "CB_2_3.out3->PE_1_3.in3", 
            "CB_3_3.out3->PE_2_3.in3", 
            "CB_0_3.out3->PE_3_3.in3", 
        ]
    }

    return arch

def _extendII(arch, II = 2): 
    if II <= 1: 
        return arch 
    arch["Module"]["TOP"]["module"] = {}
    arch["Module"]["TOP"]["connection"] = []
    for idx in range(II): 
        name = "CGRA" + str(idx)
        arch["Module"]["TOP"]["module"][name] = "CGRA"
        if idx == 0: 
            continue
        nameLast = "CGRA" + str(idx - 1)
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_0_0" + "->" + name + ".in_0_0")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_0_1" + "->" + name + ".in_0_1")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_0_2" + "->" + name + ".in_0_2")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_0_3" + "->" + name + ".in_0_3")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_1_0" + "->" + name + ".in_1_0")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_1_1" + "->" + name + ".in_1_1")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_1_2" + "->" + name + ".in_1_2")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_1_3" + "->" + name + ".in_1_3")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_2_0" + "->" + name + ".in_2_0")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_2_1" + "->" + name + ".in_2_1")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_2_2" + "->" + name + ".in_2_2")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_2_3" + "->" + name + ".in_2_3")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_3_0" + "->" + name + ".in_3_0")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_3_1" + "->" + name + ".in_3_1")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_3_2" + "->" + name + ".in_3_2")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_3_3" + "->" + name + ".in_3_3")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_mem0" + "->" + name + ".in_mem0")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_mem1" + "->" + name + ".in_mem1")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_mem2" + "->" + name + ".in_mem2")
        arch["Module"]["TOP"]["connection"].append(nameLast + ".out_mem3" + "->" + name + ".in_mem3")
        if idx == II - 1: 
            arch["Module"]["TOP"]["connection"].append(name + ".out_0_0" + "->" + "CGRA0" + ".in_0_0")
            arch["Module"]["TOP"]["connection"].append(name + ".out_0_1" + "->" + "CGRA0" + ".in_0_1")
            arch["Module"]["TOP"]["connection"].append(name + ".out_0_2" + "->" + "CGRA0" + ".in_0_2")
            arch["Module"]["TOP"]["connection"].append(name + ".out_0_3" + "->" + "CGRA0" + ".in_0_3")
            arch["Module"]["TOP"]["connection"].append(name + ".out_1_0" + "->" + "CGRA0" + ".in_1_0")
            arch["Module"]["TOP"]["connection"].append(name + ".out_1_1" + "->" + "CGRA0" + ".in_1_1")
            arch["Module"]["TOP"]["connection"].append(name + ".out_1_2" + "->" + "CGRA0" + ".in_1_2")
            arch["Module"]["TOP"]["connection"].append(name + ".out_1_3" + "->" + "CGRA0" + ".in_1_3")
            arch["Module"]["TOP"]["connection"].append(name + ".out_2_0" + "->" + "CGRA0" + ".in_2_0")
            arch["Module"]["TOP"]["connection"].append(name + ".out_2_1" + "->" + "CGRA0" + ".in_2_1")
            arch["Module"]["TOP"]["connection"].append(name + ".out_2_2" + "->" + "CGRA0" + ".in_2_2")
            arch["Module"]["TOP"]["connection"].append(name + ".out_2_3" + "->" + "CGRA0" + ".in_2_3")
            arch["Module"]["TOP"]["connection"].append(name + ".out_3_0" + "->" + "CGRA0" + ".in_3_0")
            arch["Module"]["TOP"]["connection"].append(name + ".out_3_1" + "->" + "CGRA0" + ".in_3_1")
            arch["Module"]["TOP"]["connection"].append(name + ".out_3_2" + "->" + "CGRA0" + ".in_3_2")
            arch["Module"]["TOP"]["connection"].append(name + ".out_3_3" + "->" + "CGRA0" + ".in_3_3")
            arch["Module"]["TOP"]["connection"].append(name + ".out_mem0" + "->" + "CGRA0" + ".in_mem0")
            arch["Module"]["TOP"]["connection"].append(name + ".out_mem1" + "->" + "CGRA0" + ".in_mem1")
            arch["Module"]["TOP"]["connection"].append(name + ".out_mem2" + "->" + "CGRA0" + ".in_mem2")
            arch["Module"]["TOP"]["connection"].append(name + ".out_mem3" + "->" + "CGRA0" + ".in_mem3")
    return arch

def archADRES(II = 1): 
    arch = _baseADRES()

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

    if II > 1: 
        arch = _extendII(arch, II)

    return arch

def archHyCUBE(II = 1): 
    arch = _baseHyCUBE()

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

    if II > 1: 
        arch = _extendII(arch, II)

    return arch

def _addDummy(arch): 
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

    arch["Module"]["CGRA"]["element"]["__io0"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__io1"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__io2"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__io3"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__mem0"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__mem1"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__mem2"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__mem3"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_0_0"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_0_1"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_0_2"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_0_3"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_1_0"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_1_1"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_1_2"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_1_3"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_2_0"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_2_1"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_2_2"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_2_3"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_3_0"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_3_1"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_3_2"] = "DUMMY"
    arch["Module"]["CGRA"]["element"]["__PE_3_3"] = "DUMMY"
    arch["Module"]["CGRA"]["connection"].append("__io0.out0->io0.in5")
    arch["Module"]["CGRA"]["connection"].append("__io1.out0->io1.in5")
    arch["Module"]["CGRA"]["connection"].append("__io2.out0->io2.in5")
    arch["Module"]["CGRA"]["connection"].append("__io3.out0->io3.in5")
    arch["Module"]["CGRA"]["connection"].append("__mem0.out0->mem0.in5")
    arch["Module"]["CGRA"]["connection"].append("__mem1.out0->mem1.in5")
    arch["Module"]["CGRA"]["connection"].append("__mem2.out0->mem2.in5")
    arch["Module"]["CGRA"]["connection"].append("__mem3.out0->mem3.in5")
    arch["Module"]["CGRA"]["connection"].append("__PE_0_0.out0->PE_0_0.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_0_1.out0->PE_0_1.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_0_2.out0->PE_0_2.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_0_3.out0->PE_0_3.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_1_0.out0->PE_1_0.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_1_1.out0->PE_1_1.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_1_2.out0->PE_1_2.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_1_3.out0->PE_1_3.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_2_0.out0->PE_2_0.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_2_1.out0->PE_2_1.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_2_2.out0->PE_2_2.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_2_3.out0->PE_2_3.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_3_0.out0->PE_3_0.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_3_1.out0->PE_3_1.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_3_2.out0->PE_3_2.in6")
    arch["Module"]["CGRA"]["connection"].append("__PE_3_3.out0->PE_3_3.in6")

    return arch

def ADRES(II = 1): 
    arch = _baseADRES()

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
    arch = _addDummy(arch)

    return arch