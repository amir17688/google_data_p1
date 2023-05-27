### BEGIN LICENSE ###
### Use of the triage tools and related source code is subject to the terms 
### of the license below. 
### 
### ------------------------------------------------------------------------
### Copyright (C) 2011 Carnegie Mellon University. All Rights Reserved.
### ------------------------------------------------------------------------
### Redistribution and use in source and binary forms, with or without
### modification, are permitted provided that the following conditions are 
### met:
### 
### 1. Redistributions of source code must retain the above copyright 
###    notice, this list of conditions and the following acknowledgments 
###    and disclaimers.
### 
### 2. Redistributions in binary form must reproduce the above copyright 
###    notice, this list of conditions and the following disclaimer in the 
###    documentation and/or other materials provided with the distribution.
### 
### 3. All advertising materials for third-party software mentioning 
###    features or use of this software must display the following 
###    disclaimer:
### 
###    "Neither Carnegie Mellon University nor its Software Engineering 
###     Institute have reviewed or endorsed this software"
### 
### 4. The names "Department of Homeland Security," "Carnegie Mellon 
###    University," "CERT" and/or "Software Engineering Institute" shall 
###    not be used to endorse or promote products derived from this software 
###    without prior written permission. For written permission, please 
###    contact permission@sei.cmu.edu.
### 
### 5. Products derived from this software may not be called "CERT" nor 
###    may "CERT" appear in their names without prior written permission of
###    permission@sei.cmu.edu.
### 
### 6. Redistributions of any form whatsoever must retain the following
###    acknowledgment:
### 
###    "This product includes software developed by CERT with funding 
###     and support from the Department of Homeland Security under 
###     Contract No. FA 8721-05-C-0003."
### 
### THIS SOFTWARE IS PROVIDED BY CARNEGIE MELLON UNIVERSITY ``AS IS'' AND
### CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER 
### EXPRESS OR IMPLIED, AS TO ANY MATTER, AND ALL SUCH WARRANTIES, INCLUDING 
### WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE 
### EXPRESSLY DISCLAIMED. WITHOUT LIMITING THE GENERALITY OF THE FOREGOING, 
### CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND 
### RELATING TO EXCLUSIVITY, INFORMATIONAL CONTENT, ERROR-FREE OPERATION, 
### RESULTS TO BE OBTAINED FROM USE, FREEDOM FROM PATENT, TRADEMARK AND 
### COPYRIGHT INFRINGEMENT AND/OR FREEDOM FROM THEFT OF TRADE SECRETS. 
### END LICENSE ###
'''
Some unit tests for select objects in lib. 

Because these objects expect to be instantiated in GDB's Python interpreter,
the Python-supplied unittest module is not used (it assumes access to
argv). This script is meant to be invoked like this:

exploitable$ gdb -ex "source lib/tests/unit_tests.py" -ex "quit"
'''
import sys, os
sys.path.append(os.getcwd())
import lib.gdb_wrapper as gdb_wrapper

def assertEqual(val1, val2, fmt="\"%s\""):
    assert type(val1) == type(val2), "%s != %s" % (type(val1), type(val2))
    assert val1 == val2, ("%s != %s" % (fmt, fmt)) % (val1, val2)
    
def testInstruction():
    '''
    Tests that the gdb_wrapper.Instruction string parsing works as expected. 
    '''
    # single arg test
    gdbstr = "=> 0xb97126 <gtk_main+6>:call   0xab9247"
    i = gdb_wrapper.Instruction(gdbstr)
    assertEqual(i.addr, 0xb97126, "0x%x")
    assertEqual(str(i.operands[0]), "0xab9247")
    assertEqual(i.mnemonic, "call")
    
    # trailing symbol test
    gdbstr = "=> 0xb97126 <gtk_main+6>:call   0xab9247 <g_list_remove_link@plt>"
    i = gdb_wrapper.Instruction(gdbstr)
    assertEqual(i.addr, 0xb97126, "0x%x")
    assertEqual(str(i.operands[0]), "0xab9247 <g_list_remove_link@plt>")
    assertEqual(i.mnemonic, "call")
    
    # no args
    gdbstr = "   0x005ab337 <+535>:    ret"
    i = gdb_wrapper.Instruction(gdbstr)
    assertEqual(i.addr, 0x005ab337, "0x%x")
    assertEqual(len(i.operands), 0)
    assertEqual(i.mnemonic, "ret")

    # prefix, multiple args
    gdbstr = "   0x0011098c:    repz xor 0xDEADBEEF,0x23"
    i = gdb_wrapper.Instruction(gdbstr)
    assertEqual(i.addr, 0x0011098c, "0x%x")
    assertEqual(str(i.operands[0]), "0xDEADBEEF")
    assertEqual(str(i.operands[1]), "0x23")
    assertEqual(i.mnemonic, "repz xor")

def testOperand():
    '''
    Tests that the gdb_wrapper.Operand string parsing works as expected.
    Does not test expression evaluation -- would need active registers to
    do that.
    '''
    # eiz, pointer test
    # 0x005ab184 <+100>:    lea    esi,[esi+eiz*1+0x0]
    gdbstr = "[esi+eiz*1+0x0]"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, True)
    assertEqual(o.expr, "$esi+0*1+0x0")
    
    # complex, other-pointer-style test
    #   0x00110057:    add    BYTE PTR [edx+edx*8-0x1d43fffe],bh
    gdbstr = "BYTE PTR [edx+edx*8-0x1d43fffe]"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, True)
    assertEqual(o.expr, "$edx+$edx*8-0x1d43fffe")
    
    # less-common register test
    #   0x00110057:    add    BYTE PTR [edx+edx*8-0x1d43fffe],bh
    gdbstr = "bh"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, False)
    assertEqual(o.expr, "$bh")
    
    # yet-another-pointer-style test
    #   0x001102ab:    add    BYTE PTR ds:0x2880000,ch
    gdbstr = "BYTE PTR ds:0x2880000"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, True)
    assertEqual(o.expr, "0x2880000")
    
    # floating point stack test
    #   0xb68dc5:    fucomi st,st(1)
    gdbstr = "st(1)"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, False)
    assertEqual(o.expr, "st(1)")
    
    # spacing test
    gdbstr = "edi    *    xmm5  +1"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, False)
    assertEqual(o.expr.replace(" ",""), "$edi*$xmm5+1")
    
    # 64-bit registers
    gdbstr = "r16 + r8 + r8b"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, False)
    assertEqual(o.expr.replace(" ",""), "$r16+$r8+$r8b")
    
    # more 64-bit registers
    gdbstr = "[r12w + 0x50]"
    o = gdb_wrapper.Operand(gdbstr)
    assertEqual(o.is_pointer, True)
    assertEqual(o.expr.replace(" ",""), "$r12w+0x50")
    
if __name__ == "__main__":
    testInstruction()
    testOperand()
    print "passed all tests"