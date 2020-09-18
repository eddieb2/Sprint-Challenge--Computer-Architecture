"""CPU functionality."""

import sys

# Instructions
HLT = 0b00000001 # 1
LDI = 0b10000010 # 130
PRN = 0b01000111 # 71
MUL = 0b10100010 # 162
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
#SPRINT
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        # Memory
        self.ram = [0] * 256
        # Registers -> variables in hardware - fixed num and name of these registers
        self.reg = [0] * 8
        # Program Counter -> Address of the currently executing instruction
        self.pc = 0
        # Keeps us running or stopped
        self.running = True
        self.sp = 7
        # self.reg[self.sp] = 0xf4

        # SPRINT MVP flags
        self.equal = 0
        self.less = 0
        self.greater = 0

    # NEW LOAD
    def load(self):
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue

                    # base 2
                    try:
                        value = int(n, 2)
                    except ValueError:
                        print(f'Invalid number {value}')
                        sys.exit(1)

                    self.ram[address] = value
                    address += 1

        except FileNotFoundError:
            print('File not found.')
            sys.exit(2)

    '''
    `MAR`: Memory Address Register
    =>> holds the memory address we're reading or writing
    
    `MDR`: Memory Data Register
    =>> holds the value to write or the value just read
    '''
    ## RAM read ##
    def ram_read(self, MAR):
        return self.ram[MAR]

    ## RAM write ##
    def ram_write(self, MAR, MDR):
        # ram location = value
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]

        #SPRINT MVP
        elif op == 'CMP':
            # if regA is > regB, set the >flag to 1 otherwise 0
            if self.reg[reg_a] < self.reg[reg_b]:
                self.less = 1
            # if regA is less than regB, set the less-than flag to 1 otherwise set it to 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.greater = 1
            # if they are equal, set the equal flag to 1, otherwise set it to 0
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.equal = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running is True:
            # Instruction Register -> copy of currently executing instructions
            # ram @ index 0 to start .. LDI 130
            ir = self.ram[self.pc]

            op_1 = self.ram_read(self.pc + 1)
            op_2 = self.ram_read(self.pc + 2)

            # print(f'{op_1, op_2}')

            if ir == HLT:
                # print(f'HLT: {ir}')
                self.running = False
                self.pc += 1
                # print(self.pc)
            elif ir == LDI:
                # print(f'LDI: {ir}')
                # Store op_2 in a register at index op_1 or 0
                self.reg[op_1] = op_2
                self.pc += 3
                # print(self.pc)
            elif ir == PRN:
                # print(f'PRN: {ir}')
                # Print value stored at reg[0] which is 8
                print(self.reg[op_1])
                # Increment PC to halt
                self.pc += 2
                # print(self.pc)
            elif ir == MUL:
                self.alu('MUL', op_1, op_2)
                self.pc += 3
            elif ir == ADD:
                self.reg[op_1] += self.reg[op_2]
                self.pc += 3
            elif ir == PUSH:
                # decrement sp
                self.sp -= 1
                # get the value from the reg
                val = self.reg[op_1]
                self.ram[self.sp] = val
                self.pc += 2
            elif ir == POP:
                val = self.ram[self.sp]
                self.reg[op_1] = val
                # increment sp
                self.sp += 1
                self.pc += 2
            elif ir == CALL:
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2
                # reg_i = self.ram[self.pc + 1]
                self.pc = self.reg[op_1]
            elif ir == RET:
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
            # ----------------------------------------------------------------
            ### SPRINT ###

            # COMPARE
            # compares two values in two registers
            elif ir == CMP:
                self.alu('CMP', op_1, op_2)
                self.pc += 3

            # JUMP
            # jump to the address stored in the given register
            elif ir == JMP:
                # set the pc to the address sotred in the given register
                self.pc = self.reg[op_1]

            # JUMPEQUAL
            # if eq flag is true,
            # jump to address stored in the given register
            elif ir == JEQ:
                if self.equal == 1:
                    self.pc = self.reg[op_1]
                else:
                    self.pc += 2

            # JUMPNOTEQUAL
            # if eq flag is clear (false,0),
            # jump to the address stored in the given register
            elif ir == JNE:
                if self.equal == 0:
                    self.pc = self.reg[op_1]
                else:
                    self.pc += 2
            # ----------------------------------------------------------------
            else:
                print("Broken")
        # print(self.ram)

