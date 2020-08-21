"""CPU functionality."""

import sys

HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

stack_pointer = 7


class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.running = True
        self.pc = 0
        self.fl = 0  # CMP flag
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.reg[stack_pointer] = 0xf4
        # self.reg[sp] = 244

    # Memory Address Register
    def ram_read(self, MAR):
        return self.ram[MAR]

    # Memory Address Register, Memory Data Register
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def handle_HLT(self, _a, _b):
        self.running = False

    # print a register's value
    def handle_PRN(self, a, _):
        print(self.reg[a])
        self.pc += 2

    # we set a register to a value
    def handle_LDI(self, a, b):
        self.reg[a] = b
        self.pc += 3

    def handle_MUL(self, a, b):
        self.alu("MUL", a, b)
        # self.reg[a] *= self.reg[b]
        self.pc += 3

    def handle_ADD(self, a, b):
        self.alu("ADD", a, b)
        # self.reg[a] *= self.reg[b]
        self.pc += 3

    def handle_PUSH(self, a, _):
        # with push we decrement sp
        self.reg[stack_pointer] -= 1
        # set the value to that slot
        reg_value = self.reg[a]
        self.ram_write(self.reg[stack_pointer], reg_value)
        self.pc += 2

    def handle_POP(self, a, _):

        # the value where the sp is pointing
        sp_value = self.ram_read(self.reg[stack_pointer])
        # set the value to the register at the index we pass in
        self.reg[a] = sp_value
        self.pc += 2

        # after pop we increment sp
        self.reg[stack_pointer] += 1

    def handle_CALL(self, a, _b):
        # push return address on to the stack
        # setting return address to next instruction
        return_address = self.pc + 2
        # decrement stack pointer
        # to set us up to add next thing to stack
        self.reg[stack_pointer] -= 1
        # store the return address in the stack
        self.ram_write(self.reg[stack_pointer], return_address)
        # move to the subroutine call
        self.pc = self.reg[a]

    def handle_RET(self, a, b):
        return_address = self.ram[self.reg[stack_pointer]]
        self.pc = return_address
        self.reg[stack_pointer] += 1

    def load(self, filename):
        """Load a program into memory."""

        try:
            address = 0

            with open(filename) as f:
                for line in f:
                    comment_split = line.split('#')
                    byte = comment_split[0].strip()

                    if byte == '':
                        continue

                    dec = int(byte, 2)

                    self.ram_write(address, dec)

                    # incr so we will not overwrite next time
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} not found")
            sys.exit(2)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            # L
            # reg a less than reg b
            if self.reg[reg_a] < self.reg[reg_b]:

            # G
            # reg a greater than reg b
            elif self.reg[reg_a] > self.reg[reg_b]:

            # E
            # equal
            else:

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |" % (
                self.pc,
                #self.fl,
                #self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2)),
            end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            # IR is the instruction register
            # read the op code for this instruction into the IR
            IR = self.ram_read(self.pc)
            # we read the memory in these pc slots given, in case they are used later
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR in self.branchtable:
                cmnd = self.branchtable[IR]
                cmnd(operand_a, operand_b)

            else:
                print(f"{IR} is not a valid command")
                print('memory address', self.pc)
                self.running = False

            # # exits the action
            # if IR == HLT:
            #     self.running = False

            # # print a register's value
            # elif IR == PRN:
            #     print(self.reg[operand_a])
            #     self.pc += 2

            # # we set a register to a value
            # elif IR == LDI:
            #     self.reg[operand_a] = operand_b
            #     self.pc += 3

            # elif IR == MUL:
            #     self.alu("MUL", operand_a, operand_b)
            #     self.pc += 3

            # else:
            #     print("That is not a valid command")
            #     self.running = False
