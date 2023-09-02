#spemulator.py
# This program emulates a machine that runs on the MIPS ISA using python.
# It takes code in hexadecimal (as assembled from MIPS assembly) and simulates
# the execution of that code on a MIPS machine.
# Currently only accepts one line of code at a time, not an entire program.

import sys

memory = [0]*32             # memory block
register = [0]*32           # register block
pc = 0                      # program counter
exit_program = False        # bool keeping track of exiting program

def strToBin(input_code: str) -> None:
    #convert "binary" string to integer
    integer = 0
    length = len(input_code)-1
    for i in range(0, length):
        curChar = ord(input_code[i]) - 48
        if curChar < 0:                     #Not a valid hex number
            print("Please input a valid MIPS instruction in 8 digit hexadecimal")
            return -1
        if curChar > 9:                     #digit is either A-F or invalid
            curChar = curChar - 7  
            if curChar < 10 or curChar > 15:    #make sure digit is A-F
                print("Please input a valid MIPS instruction in 8 digit hexadecimal")
                return -1
        integer = integer + (16**(length-i-1))*(int(curChar))
    return integer


# Decodes what type of function: i, r or j from hexcode
def decodeFuncType(machine_code: int) -> None:
    first_6_bits = hex(machine_code >> 26)
    if first_6_bits == "0x0":
        return "r"
    if first_6_bits in ["0x23", "0x2b", "0x4"]:
        return "i"
    if first_6_bits in ["0x2"]:
        return "j"
    else:
        raise Exception("Invalid instruction. First 6 bits (2 digits of machine code) are not supported")
        
# decodes the hex code into shamt, rd, rt, and rs and calls appropriate function
def callRType(machine_code: int) -> None:
    funccode = hex(machine_code & 0x0000003F)
    shamt = (machine_code & 0x000007FF)>>6
    rd = (machine_code & 0x0000FFFF)>>11
    rt = (machine_code & 0x001FFFFF)>>16
    rs = (machine_code & 0x01FFFFFF)>>21

    if shamt < 0 or shamt > 31:
        raise Exception("Please enter a valid shamt between 0 and 31 (except 26 and 27)")
    if rd < 0 or rd > 31:
        raise Exception("Please enter a valid rd between 0 and 31 (except 26 and 27)")
    if rt < 0 or rt > 31:
        raise Exception("Please enter a valid rt between 0 and 31 (except 26 and 27)")
    if rs < 0 or rs > 31:
        raise Exception("Please enter a valid rs between 0 and 31 (except 26 and 27)")

    print("shamt: " + str(shamt) + ", rd: " + str(rd) + ", rt: " + str(rt) + ", rs: " + str(rs))
    if funccode == "0x20":
        add(rs, rt, rd)
    if funccode == "0xC":
        syscall()

# decodes the hex code into rt, and rs, immediate and opcode and calls appropriate function
def callIType(machine_code: int) -> None:
    immediate = (machine_code & 0x0000FFFF)
    rt = (machine_code & 0x001FFFFF)>>16
    rs = (machine_code & 0x01FFFFFF)>>21
    if rt < 0 or rt > 31:
        raise Exception("Please enter a valid rt between 0 and 31 (except 26 and 27)")
    if rs < 0 or rs > 31:
        raise Exception("Please enter a valid rs between 0 and 31 (except 26 and 27)")

    opcode = hex(machine_code >> 26)

    if opcode == "0x2b":
        storeWord(rt = rt, rs = rs, immeediate = immediate)
    if opcode == "0x4":
        branchOnEqual(rt = rt, rs = rs, immediate = immediate)

def callJType(machine_code: int) -> None:
    opcode = hex(machine_code >> 26)
    address = (machine_code & 0x01FFFFFF)
    if opcode == "0x2":
        jump(address)


# R type instructions 

# add instruciton
def add(rs: int, rt: int, rd: int) -> None:
    register[rd] = register[rs] + register[rt]

# syscall function
def syscall():
    v0 = register[2]
    a0 = register[4]

    if v0 == 1:
        print(a0)
    
    if v0 == "4":
        printString = memory[a0]
        print(printString)
    if v0 == 5:
        register[2] = sys.stdin.read()
    if v0 == 10:
        exit_program = True


# I type instructions
def storeWord(rt: int, rs: int, immediate: int) -> None:
    if immediate%4 != 0:
        raise Exception("Immediate value must be a multiple of 4")

    register[rt] = memory[register[rs] + (immediate/4)] 


def loadWord(rt: int, rs: int, immediate: int) -> None:
    if immediate%4 != 0:
        raise Exception("Immediate value must be a multiple of 4")

    memory[register[rs] + (immediate/4)] = register[rt]


def branchOnEqual(rt: int, rs: int, immediate: int) -> None:
    if(register[rs] == register[rt]):
        pc = pc + 4 + immediate

# J type instructions
def jump(address: int) -> None:
    pc = address


if __name__ == '__main__':
    print("Welcome to Spemulator: The MIPS emulator!")
    print("Please input a MIPS instruction in hexadecimal:")

    while(not exit_program):
        input_code = sys.stdin.readline()
        assert (len(input_code)-1)%8 == 0         #size of MIPS intructions plus 1 buffer for strings
        machine_code = strToBin(input_code)
        #print('{:032b}'.format(machine_code))
        funcType = decodeFuncType(machine_code)
        print(funcType)
        if funcType == "r":
            callRType(machine_code)
        if funcType == "i":
            callIType(machine_code)
        if funcType == "j":
            callJType(machine_code)
    