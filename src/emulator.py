import re

class PDUAEmulator:
    def __init__(self):
        self.ProgramCounter = 0
        self.Dptr = '00000000'
        self.Acc = '00000000'
        self.RegisterA = '00000000'

        # Flags
        self.ZeroFlag = True
        self.NegativeFlag = False
        self.OverflowFlag = False
        self.HaltFlag = False

        # Memory
        self.Program = [''] * 256
        self.Memory = [''] * 8
        self.Stack = []
        self.ProgramSize = 0

    def Reset(self):
        self.ProgramCounter = 0
        self.Acc = '00000000'
        self.Dptr = '00000000'
        self.RegisterA = '00000000'

        self.ZeroFlag = True
        self.NegativeFlag = False
        self.OverflowFlag = False
        self.HaltFlag = False

        for i in range(len(self.Memory)):
            self.Program[i] = ''
            self.Memory[i] = ''

        self.Stack = []

    def ResetFlags(self):
        self.ZeroFlag = True
        self.NegativeFlag = False
        self.OverflowFlag = False
        self.HaltFlag = False

    def TransformIntruction(self, instruction):
        if isinstance(instruction, str):
            if re.match('0[xX][0-9a-fA-F]+', instruction) :
                instruction = bin(int(instruction, 16))[2:]
            elif re.match('0[bB][0-1]+', instruction):
                instruction = instruction[2:]
            if len(instruction) < 8:
                instruction = instruction.zfill(8)
            elif len(instruction) > 8:
                raise ValueError("binary too large to fit in memory for variables", instruction)
        return instruction

    def LoadProgram(self, program:list, memory:dict):
        if len(program) > len(self.Program):
            raise MemoryError("El codigo tiene demasiadas instrucciones, limite 256. Recuerde que algunas usan 2 bytes")
        if len(memory) > len(self.Memory):
            raise ValueError("El codigo tiene demasiadas posiciones de memoria, limite 8.")

        self.ProgramSize = len(program)
        for i, v in enumerate(program):
            self.Program[i] = self.TransformIntruction(v)
        for i, (k, v) in enumerate(memory.items()):
            self.Memory[i] = self.TransformIntruction(v)
        
    def check_variables(self):
        if len(self.Memory) < 5:
            raise MemoryError('Se requieren 5 posiciones de memoria asignadas: A, Q, Q-1, M, Count')

    def check_halt(self):
        if '11111111' not in self.Program:
            raise RuntimeError('El programa requiere la instruccion HLT para finalizar adecuadamente.')

    def InvAcc(self):
        resultado = ""
        for caracter in self.Acc:
            if caracter == "0":
                resultado += "1"
            elif caracter == "1":
                resultado += "0"
            else:
                raise ValueError("La cadena debe contener solo valores de 0 y 1.")
        self.Acc = resultado

    def AndAccA(self):
        resultado = ""
        for i in range(len(self.RegisterA)):
            if self.RegisterA[i] == "1" and self.Acc[i] == "1":
                resultado += "1"
            else:
                resultado += "0"
        self.Acc = resultado

    def AddAccA(self):
        resultado = []
        carry = 0
        
        for i in range(len(self.Acc) - 1, -1, -1):
            bit1 = int(self.Acc[i])
            bit2 = int(self.RegisterA[i])
            
            suma_bits = bit1 + bit2 + carry
            resultado.insert(0, str(suma_bits % 2))
            carry = suma_bits // 2
        
        if carry:
            resultado.insert(0, str(carry))
            self.OverflowFlag = True
        else:
            self.OverflowFlag = False
        
        self.Acc = "".join(resultado)
        if len(self.Acc) >8:
            self.Acc = self.Acc[-8:]

    def Step(self):
        instruction = self.Program[self.ProgramCounter]#.lower()
        if instruction == '00000000':
            # NOP | 0x0 | (1 byte)
            self.ProgramCounter += 1
        elif instruction == '00000001':
            # MOV ACC, A | 0x1 | (1 byte)
            self.Acc = self.RegisterA
            self.ProgramCounter += 1
        elif instruction == '00000010':
            # MOV A, ACC | 0x2 | (1 byte)
            self.RegisterA = self.Acc
            self.ProgramCounter += 1
        elif instruction == '00000011':
            # MOV ACC, CTE | 0x3 | (2 bytes)
            self.Acc = self.Program[self.ProgramCounter+1]
            self.ProgramCounter += 2
        elif instruction == '00000100':
            # MOV ACC, [DPTR] | 0x4 | (2 bytes)
            self.Acc = self.Memory[int(self.Dptr,2)]
            self.ProgramCounter += 1
        elif instruction == '00000101':
            # MOV DPTR, ACC | 0x5 | (1 byte)
            self.Dptr = self.Acc
            self.ProgramCounter += 1
        elif instruction == '00000110':
            # MOV [DPTR], ACC | 0x6 | (1 byte)
            self.Memory[int(self.Dptr,2)] = self.Acc
            self.ProgramCounter += 1
        elif instruction == '00000111':
            # INV ACC | 0x7 | (1 byte)
            self.InvAcc()
            self.ProgramCounter += 1
        elif instruction == '00001000':
            # AND ACC, A | 0x8 | (1 byte)
            self.AndAccA()
            self.ProgramCounter += 1
        elif instruction == '00001001':
            # ADD ACC, A | 0x9 | (1 byte)
            self.AddAccA()
            self.ProgramCounter += 1
        elif instruction == '00001010':
            # JMP CTE | 0xA | (2 bytes)
            self.ProgramCounter = int(self.Program[self.ProgramCounter+1], 2)
        elif instruction == '00001011':
            # JZ CTE | 0xB | (2 bytes)
            if self.ZeroFlag:
                self.ProgramCounter = int(self.Program[self.ProgramCounter+1],2)
            else:
                self.ProgramCounter += 2
            self.ResetFlags()
        elif instruction == '00001100':
            # JN CTE | 0xC | (2 bytes)
            if self.NegativeFlag:
                self.ProgramCounter = int(self.Program[self.ProgramCounter+1],2)
            else:
                self.ProgramCounter += 2
            self.ResetFlags()
        elif instruction == '00001101':
            # JC CTE | 0xD | (2 bytes)
            if self.OverflowFlag:
                self.ProgramCounter = int(self.Program[self.ProgramCounter+1],2)
            else:
                self.ProgramCounter += 2
            self.ResetFlags()
        elif instruction == '00001110':
            # CALL CTE | 0xE | (2 bytes)
            address = int(self.Program[self.ProgramCounter+1],2)
            self.Stack.append(self.ProgramCounter+2)
            self.ProgramCounter = address
        elif instruction == '00001111':
            # RET | 0xF | (1 byte)
            if len(self.Stack) == 0:
                raise ValueError("stack underflow")

            self.ProgramCounter = self.Stack[-1]
            self.Stack = self.Stack[:-1]
        elif instruction == '00010000':
            # RSH ACC CTE | 0x10 | (2 byte)
            for i in range(int(self.Program[self.ProgramCounter+1],2)):
                self.Acc = self.Acc[:-1].rjust(8, '0') # Arithmetic shift rigth
            self.ProgramCounter += 2
        elif instruction == '00010001':
            # LSH ACC CTE | 0x11 | (2 byte)
            for i in range(int(self.Program[self.ProgramCounter+1],2)):
                self.Acc = self.Acc[1:].ljust(8, '0') # Arithmetic shift left
            self.ProgramCounter += 2
        elif instruction == '11111111':
            # HLT | 0xff | (1 byte)
            self.HaltFlag = True
        else:
            print(instruction)
            raise ValueError("unknown instruction: ", instruction)

        self.UpdateFlags()

    def UpdateFlags(self):
        self.ZeroFlag = self.Acc == '00000000'
        if len(self.Acc)>0:
            self.NegativeFlag = self.Acc[0] == '1'

