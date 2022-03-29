import os
import sys 
sys.path.append(".")

import optuna
import numpy as np 

from common.utils import *
from common.graph import *
from arch.arch import *
from arch.adres import *
from arch.protocols import *

def rtlMUX(num = 2): 
    info = ""
    info += "module MUX" + str(num) + "(\n"
    info += '''
    input clock,
    input reset,
    '''
    for idx in range(num): 
        info += "    input [31:0] in" + str(idx) + ",\n"
    info += "    input [63:0] config,\n"
    info += "    output [31:0] out0\n);"

    info += '''
reg [63:0] _config; 

always @(posedge clock) begin
    
    if(reset == 1) begin
        _config <= config; 
    end else begin
        _config <= _config >> 8; 
    end
end
    '''

    info += '''

always @(*) begin
    
    case(_config[7:0])
    '''

    for idx in range(num): 
        info += "    " + str(num) + ": out0 = in" + str(idx) + ";\n"
    info += "    default" ": out0 = 0;\n"

    info += "    endcase\n"

    info += "end\n"

    info += "endmodule\n"

    return info

def rtlALU(): 
    return '''
module ALU(
    input clock,
    input reset,
    input [31:0] in0, 
    input [31:0] in1, 
    input [31:0] in2, 
    input [63:0] config, 
    output reg [31:0] out0
); 

reg [63:0] _config; 

always @(posedge clock) begin
    
    if(reset == 1) begin
        out0 <= 0; 
        _config <= config; 
    end else begin
        _config <= _config >> 8; 

        case(_config[7:0])
        0: out0 <= in0 + in1; 
        1: out0 <= in0 - in1; 
        2: out0 <= in0 * in1; 
        4: out0 <= in0 & in1; 
        5: out0 <= in0 | in1; 
        6: out0 <= in0 ^ in1; 
        7: out0 <= in0 << in1; 
        8: out0 <= in0 >> in1; 
        15: out0 <= in2 ? in1 : in0; 
        default: out0 <= 0; 
        endcase
    end
    
end

endmodule    
    '''


def rtlCONST(): 
    return '''
module CONST(
    input clock,
    input reset,
    input [255:0] config, 
    input [31:0] in0, 
    output reg [31:0] out0
); 

reg [255:0] _config; 

always @(posedge clock) begin
    
    if(reset == 1) begin
        out0 <= 0; 
        _config <= config; 
    end else begin
        _config <= _config >> 32; 
        out0 <= _config[31:0]; 
    end
    
end

endmodule    
    '''


def rtlMEM(): 
    return '''
module MEM(
    input clock,
    input reset,
    input [31:0] in0, 
    input [31:0] in1, 
    input [31:0] in2, 
    input [63:0] config, 
    output reg [31:0] out0
); 

endmodule 
    '''


def rtlIO(): 
    return '''
module IO(
    input clock,
    input reset,
    input [63:0] config, 
    input [31:0] in0, 
    output reg [31:0] out0
); 

endmodule    
    '''


def rtlDUMMY(): 
    return '''
module DUMMY(
    input clock,
    input reset,
    input [63:0] config, 
    input [31:0] in0, 
    output reg [31:0] out0
); 

endmodule    
    '''


def genrtl(rrgfile, outfile): 
    rrg = HyperGraph(rrgfile)

    info = ""
    info += rtlMEM()
    info += "\n"
    info += rtlIO()
    info += "\n"
    info += rtlDUMMY()
    info += "\n"
    info += rtlCONST()
    info += "\n"
    info += rtlALU()
    info += "\n"

    wires = set()
    swpins = set()
    switches = set()
    mems = set()
    ios = set()
    dummies = set()
    consts = set()
    alus = set()
    for name, vertex in rrg.vertices().items(): 
        if "switch" in vertex.attrs(): 
            switches.add(".".join(name.split(".")[:-1]))
            swpins.add(name)
            wires.add(name)
        elif vertex.attr("type") in ["__ELEMENT_INPUT_PORT__", "__ELEMENT_OUTPUT_PORT__"]: 
            wires.add(name)
        elif vertex.attr("type") in ["__MODULE_INPUT_PORT__", "__MODULE_OUTPUT_PORT__"]: 
            wires.add(name)
        elif vertex.attr("type") in ["MEM", ]: 
            mems.add(name)
        elif vertex.attr("type") in ["IO", ]: 
            ios.add(name)
        elif vertex.attr("type") in ["DUMMY", ]: 
            dummies.add(name)
        elif vertex.attr("type") in ["CONST", ]: 
            consts.add(name)
        elif vertex.attr("type") in ["ALU", ]: 
            alus.add(name)

    definitions = []
    for wire in wires: 
        definitions.append("wire [31:0] " + wire.replace(".", "_") + ";")
    
    assigns = []
    for name, vertex in rrg.vertices().items(): 
        for net in rrg.netsOut(name): 
            if net.fr() in wires and net.to()[0] in wires and \
               not (net.fr() in swpins and net.to()[0] in swpins): 
                assigns.append("assign " + net.to()[0].replace(".", "_") + " = " + net.fr().replace(".", "_") + ";")
    
    
    countConfig = 0
    countOut = 0
    instances = []
    additional = []
    swtypes = set()
    for switch in switches: 
        pins = set()
        for name, vertex in rrg.vertices().items(): 
            prefix = ".".join(name.split(".")[:-1])
            postfix = name.split(".")[-1]
            if prefix == switch: 
                pins.add(postfix)
        length = len(pins) - 1
        if not length in swtypes: 
            info += rtlMUX(length)
            info += "\n" 
            swtypes.add(length)
        tmp = "MUX" + str(length) + " " + switch.replace(".", "_") + "(.clock(clock), .reset(reset), "
        tmp += ".config(config[" + str(countConfig + 63) + ":" + str(countConfig) + "]), "
        countConfig += 64
        for pin in pins: 
            tmp += "." + pin + "(" + switch.replace(".", "_") + "_" + pin + "), "
        tmp = tmp[:-2] + ");"
        instances.append(tmp)
    
    for mem in mems: 
        pins = set()
        for name, vertex in rrg.vertices().items(): 
            prefix = ".".join(name.split(".")[:-1])
            postfix = name.split(".")[-1]
            if prefix == mem: 
                pins.add(postfix)
        tmp = "MEM " + mem.replace(".", "_") + "(.clock(clock), .reset(reset), "
        tmp += ".config(config[" + str(countConfig + 63) + ":" + str(countConfig) + "]), "
        countConfig += 64
        additional.append("assign outs[" + str(countOut + 31) + ":" + str(countOut) + "] = " + mem.replace(".", "_") + "_out0;")
        countOut += 32
        for pin in pins: 
            tmp += "." + pin + "(" + mem.replace(".", "_") + "_" + pin + "), "
        tmp = tmp[:-2] + ");"
        instances.append(tmp)
    
    for io in ios: 
        pins = set()
        for name, vertex in rrg.vertices().items(): 
            prefix = ".".join(name.split(".")[:-1])
            postfix = name.split(".")[-1]
            if prefix == io: 
                pins.add(postfix)
        tmp = "IO " + io.replace(".", "_") + "(.clock(clock), .reset(reset), "
        tmp += ".config(config[" + str(countConfig + 63) + ":" + str(countConfig) + "]), "
        countConfig += 64
        additional.append("assign outs[" + str(countOut + 31) + ":" + str(countOut) + "] = " + io.replace(".", "_") + "_out0;")
        countOut += 32
        for pin in pins: 
            tmp += "." + pin + "(" + io.replace(".", "_") + "_" + pin + "), "
        tmp = tmp[:-2] + ");"
        instances.append(tmp)
    
    for dummy in dummies: 
        pins = set()
        for name, vertex in rrg.vertices().items(): 
            prefix = ".".join(name.split(".")[:-1])
            postfix = name.split(".")[-1]
            if prefix == dummy: 
                pins.add(postfix)
        tmp = "DUMMY " + dummy.replace(".", "_") + "(.clock(clock), .reset(reset), "
        tmp += ".config(config[" + str(countConfig + 63) + ":" + str(countConfig) + "]), "
        countConfig += 64
        additional.append("assign outs[" + str(countOut + 31) + ":" + str(countOut) + "] = " + dummy.replace(".", "_") + "_out0;")
        countOut += 32
        for pin in pins: 
            tmp += "." + pin + "(" + dummy.replace(".", "_") + "_" + pin + "), "
        tmp = tmp[:-2] + ");"
        instances.append(tmp)
    
    for const in consts: 
        pins = set()
        for name, vertex in rrg.vertices().items(): 
            prefix = ".".join(name.split(".")[:-1])
            postfix = name.split(".")[-1]
            if prefix == const: 
                pins.add(postfix)
        tmp = "CONST " + const.replace(".", "_") + "(.clock(clock), .reset(reset), "
        tmp += ".config(config[" + str(countConfig + 255) + ":" + str(countConfig) + "]), "
        countConfig += 256
        additional.append("assign outs[" + str(countOut + 31) + ":" + str(countOut) + "] = " + const.replace(".", "_") + "_out0;")
        countOut += 32
        for pin in pins: 
            tmp += "." + pin + "(" + const.replace(".", "_") + "_" + pin + "), "
        tmp = tmp[:-2] + ");"
        instances.append(tmp)
    
    for alu in alus: 
        pins = set()
        for name, vertex in rrg.vertices().items(): 
            prefix = ".".join(name.split(".")[:-1])
            postfix = name.split(".")[-1]
            if prefix == alu: 
                pins.add(postfix)
        tmp = "ALU " + alu.replace(".", "_") + "(.clock(clock), .reset(reset), "
        tmp += ".config(config[" + str(countConfig + 63) + ":" + str(countConfig) + "]), "
        countConfig += 64
        additional.append("assign outs[" + str(countOut + 31) + ":" + str(countOut) + "] = " + alu.replace(".", "_") + "_out0;")
        countOut += 32
        for pin in pins: 
            tmp += "." + pin + "(" + alu.replace(".", "_") + "_" + pin + "), "
        tmp = tmp[:-2] + ");"
        instances.append(tmp)

    info += '''
module CGRA(
    input clock,
    input reset,
    input [%d:0] config, 
    output [%d:0] outs
); 

''' % (countConfig, countOut)

    for definition in definitions: 
        info += "    " + definition + "\n"
    for assign in assigns: 
        info += "    " + assign + "\n"
    for instance in instances: 
        info += "    " + instance + "\n"
    for line in additional: 
        info += "    " + line + "\n"

    info += "endmodule\n"

    with open(outfile, "w") as fout: 
        fout.write(info)
    
def genyosys(name, vname, ysname): 
    info = ""
    info += "read -sv " + vname + "\n"
    info += "synth -top " + name + "\n"
    info += "dfflibmap -liberty ./test/gscl45nm.lib\n"
    info += "abc -liberty ./test/gscl45nm.lib\n"
    info += "stat -liberty ./test/gscl45nm.lib\n"
    info += "clean\n"
    
    with open(ysname, "w") as fout: 
        fout.write(info)

def getArea(ysname, logname): 
    os.system("yosys " + ysname + " > " + logname + " 2>&1")
    with open(logname, "r") as fout: 
        for line in fout.readlines(): 
            if "Chip area for top module" in line: 
                splited = line.strip().split()
                return float(splited[-1])
    return 1e9

if __name__ == "__main__": 
    genrtl(sys.argv[1], sys.argv[2])
    genyosys("CGRA", sys.argv[2], "./tmp/CGRA.ys")
    area = getArea("./tmp/CGRA.ys", "./tmp/CGRA.log")
    print(area)


