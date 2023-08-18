import os
import argparse
import yaml
import re
from src.emulator import PDUAEmulator
from typing import Union, List, Dict

#import streamlit as st
def load_program():
    '''
    Load .asm file from args
    '''
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("-f", "--asemmbly", help = "file .asm with PDUA instructions")
    # Read arguments from command line
    return vars(parser.parse_args())

def get_file(asm_file: str) -> list:
    '''
    Load file from disk, return as list of instructions
    '''
    assert os.path.isfile(asm_file), 'No se encontro archivo '+asm_file
    assert asm_file.endswith('.asm'), 'Extension no valida, '+asm_file
    with open(asm_file, 'r') as f:
        raw_asm = f.readlines()
    return raw_asm

def clean_line(line: str)->str:
    '''
    Remove spaces and special characters, return in upper.
    '''
    if ';' in line and ':' in line:
        return line.replace('\n','').replace('\t','').split(';')[0].strip().upper()
    return line.replace('\n','').replace('\t','').strip().upper()

def remove_comments(raw_asm: str) -> list:
    '''
    Delete comment lines
    '''
    #code_asm = [clean_line(line).split(';')[0].strip() for line in raw_asm if (not clean_line(line).endswith(':')) and (not clean_line(line).startswith(';'))]
    code_asm = [clean_line(line).split(';')[0].strip() for line in raw_asm if (not clean_line(line).startswith(';'))]
    return list(filter(None, code_asm))

def split_instructions(code_asm: list) -> Union[List, Dict, Dict]:
    '''
    From instructions in Assembly split clan instructions from jump reference values and variables

    Input:
        List of strings, with assembly code
    Output:
        instructions: list of filtered instructions
        jump_reference: Dict where the key represent the name of the jump reference and the value the number of the instruction to go
        variables: Dict where the key represent the name of the variable and the value the value of it
    '''
    instructions = []
    inst_count = 0
    jump_reference = {}
    variables = {}
    isa = read_yaml()
    for line in code_asm:
        if ':' in line:
            splited_line = line.split(':')
            # is a jump reference
            if splited_line[1] == '':
                jump_reference[splited_line[0]] = inst_count
            # is a variable
            else:
                variables[splited_line[0]] = splited_line[1].strip()
        else:
            try:
                isa['ISA'][line]
            except:
                inst_count += 1
            instructions.append(line)
            inst_count += 1
    return instructions, jump_reference, variables

def read_yaml(yaml_file: str ='/work/src/Instructions_set.yaml'):
    '''
    Read ISA yaml file
    '''
    with open(yaml_file, "r") as stream:
        try:
            return  yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def decode_instructions(instructions: list, jump_reference: dict, variables: dict) -> Union[List, List]:
    '''
    Use instructions, jump_reference and variables to decode instructions into the binary representation, setting in possition the constants as a values.
    Inputs:
        instructions: list of filtered instructions
        jump_reference: Dict where the key represent the name of the jump reference and the value the number of the instruction to go
        variables: Dict where the key represent the name of the variable and the value the value of it
    Output:
        bin_instructions: binary representation of instructions
        readable_inst: ISA representation of binary instruction or value be used.

    '''
    bin_instructions=[]
    readable_inst = []
    isa = read_yaml()
    #memory = {}
    for inst in instructions:
        var =0
        try:
            bin_instructions.append(isa['ISA'][inst])
            readable_inst.append(inst)
        except:
            _inst, var, asm_inst, is_variable = replace_variables(inst, jump_reference, variables, isa)
            
            bin_instructions.append(_inst)
            readable_inst.append(asm_inst)
            if is_variable:
                #memory.setdefault(inst.split()[-1], var)
                bin_instructions.append(list(variables).index(inst.split()[-1]))
                readable_inst.append(inst.split()[-1])
            else:
                bin_instructions.append(var)
                readable_inst.append(var)

                
    return bin_instructions, readable_inst

def replace_variables(inst: str, jump_reference: dict, variables: dict, isa: dict) -> Union[str,int,str,bool]:
    '''
    From instructions replace variables from jump reference and variables
    Input:
        inst: a specific instruction
        jump_reference: Dict where the key represent the name of the jump reference and the value the number of the instruction to go
        variables: Dict where the key represent the name of the variable and the value the value of it
        isa: Dict where the key represent the Assembley representation and value the binary code
    Output:
        - str of binary code
        - int variable value
        - str of assembly instruction
        - flag for variable value
    '''
    is_variable = False
    try:
        v_inst = inst.split()
        ## if value is CTE expressed in HEX or bin
        if re.match('0[xX][0-9a-fA-F]+', v_inst[-1]) or re.match('0[bB][0-1]+', v_inst[-1]):
            var = v_inst[-1]
            
        ## if CTE is referenced by variable
        else:
            var = jump_reference[v_inst[-1]]
    except KeyError as e:
        try:
            var = variables[v_inst[-1]]
            is_variable = True
        except KeyError as e:
            raise NameError('INSTRUCCION NO EXISTENTE', inst)
    var = get_int(str(var))
    ## return binary code, variable value and assembly instruction
    if v_inst[0] == 'MOV':
        return isa['ISA']['MOV ACC, CTE'], var, 'MOV ACC, CTE', is_variable
    if v_inst[0] == 'JMP':
        return isa['ISA']['JMP CTE'], var, 'JMP CTE', is_variable
    if v_inst[0] == 'JZ':
        return isa['ISA']['JZ CTE'], var, 'JZ CTE', is_variable
    if v_inst[0] == 'JN':
        return isa['ISA']['JZ CTE'], var, 'JZ CTE', is_variable
    if v_inst[0] == 'JC':
        return isa['ISA']['JC CTE'], var, 'JC CTE', is_variable
    if v_inst[0] == 'RSH':
        return isa['ISA']['RSH ACC CTE'], var, 'RSH ACC CTE', is_variable
    if v_inst[0] == 'LSH':
        return isa['ISA']['LSH ACC CTE'], var, 'LSH ACC CTE', is_variable
    
def get_int(line: str):
    if isinstance(line, str):
        if line.startswith('0X') or line.startswith('0x'):
            return int(line[2:], 16)
        elif line.startswith('0B') or line.startswith('0b'):
            return int(line[2:], 2)
        else:
            return int(line)
    elif isinstance(line, int):
        return line
    else:
        raise TypeError('line must be str or int')       

def get_hex(line: str):
    return hex(get_int(line))

def c1(number):
    resultado = ""
    for caracter in number:
        if caracter == "0":
            resultado += "1"
        elif caracter == "1":
            resultado += "0"
    return resultado

def c2(number1,final=False):
    resultado = []
    carry = 0
    if final:
        number2 ='0000000000000001'
    else:
        number2 ='00000001'
    for i in range(len(number1) - 1, -1, -1):
        bit1 = int(number1[i])
        bit2 = int(number2[i])
        
        suma_bits = bit1 + bit2 + carry
        resultado.insert(0, str(suma_bits % 2))
        carry = suma_bits // 2
    
    if carry:
        resultado.insert(0, str(carry))
    
    number1 = "".join(resultado)
    if final:
        print(number1)
        if len(number1) >16:
            number1 = number1[-16:]
    else:
        if len(number1) >8:
            number1 = number1[-8:]
    return number1


if __name__ == '__main__':
    args = load_program()
    raw_asm = get_file(args['asemmbly'])
    
    code_asm = remove_comments(raw_asm)
    instructions, jump_reference, variables = split_instructions(code_asm)

    hex_instructions, readable_inst = decode_instructions(instructions, jump_reference, variables)
    hex_instructions = [get_hex(x) for x in hex_instructions]
    pdua = PDUAEmulator()
    from pprint import pprint
    # pprint(instructions)
    print(jump_reference)
    print(variables)

    pdua.Reset()
    print('[Creando PDUA]')
    
    pdua.LoadProgram(hex_instructions, variables)
    Multiplicando_inicial = pdua.Memory[3]
    Multiplicador_inicial = pdua.Memory[1]
    print('[Cargando Programa]')
    print('Tamaño del código:', pdua.ProgramSize)
    print('------------------------------------------')
    print('Valores de Memoria:', pdua.Memory)

    from pprint import pprint
    #print('------------------------------------------')
    #print('Listado')
    #pprint(list(zip(hex_instructions, readable_inst)))
    
    print('------------------------------------------')
    print('------------------------------------------')
    print('------------------------------------------')
    print( '|PC {: <3}'.format(pdua.ProgramCounter),
            '|{: <3} {: <15}'.format(pdua.Program[pdua.ProgramCounter], readable_inst[pdua.ProgramCounter]),
            '|Acc {: <2}'.format(pdua.Acc),
            '|rA {: <3}'.format(pdua.RegisterA),
            '|DPTR {: <2}'.format(pdua.Dptr),
            '|[DPTR]',pdua.Stack,
            '|A {: <3}'.format(pdua.Memory[0]),
            '|Q {: <3}'.format(pdua.Memory[1]),
            '|Q0 {: <3}'.format(pdua.Memory[2]),
            '|M {: <3}'.format(pdua.Memory[3]),
            '|I {: <3}'.format(pdua.Memory[4]),
            '|C {: <3}'.format(pdua.Memory[5]))
    input()
    while(not pdua.HaltFlag):

        try:
            pdua.Step() # revisar logica del shift
            #if pdua.ProgramCounter == 117 or pdua.ProgramCounter == 0:

            print( '|PC {: <3}'.format(pdua.ProgramCounter),
                    '|{: <3} {: <15}'.format(pdua.Program[pdua.ProgramCounter], readable_inst[pdua.ProgramCounter]),
                    '|Acc {: <2}'.format(pdua.Acc),
                    '|A {: <3}'.format(pdua.RegisterA),
                    '|DPTR {: <2}'.format(pdua.Dptr),
                    ' | | A {: <3}'.format(pdua.Memory[0]),
                    '|Q {: <3}'.format(pdua.Memory[1]),
                    '|Q0 {: <3}'.format(pdua.Memory[2]),
                    '|M {: <3}'.format(pdua.Memory[3]),
                    '|C {: <3}'.format(pdua.Memory[5]))#,
                    # '|Z {: <3}'.format(pdua.ZeroFlag),
                    # '|N {: <3}'.format(pdua.NegativeFlag),
                    # '|C {: <3}'.format(pdua.OverflowFlag))

            # if pdua.ProgramCounter == 117:
            #     print(pdua.Memory)
            #     break

        except Exception as e:
            print('Accumulator', type(pdua.Acc),' Registro A ', type(pdua.RegisterA), '.Pointer ', type(pdua.Dptr))
            print('------------------------')
            print('ProgramCounter', pdua.ProgramCounter)
            print('INST', pdua.Program[pdua.ProgramCounter], readable_inst[pdua.ProgramCounter])
            
            #print(pdua.Memory)
            raise e
    if Multiplicando_inicial[0] == '0':
        print('Multiplicando_inicial: ',Multiplicando_inicial, int(Multiplicando_inicial,2))
    else:
        resultado = c1(Multiplicando_inicial)
        resultado = c2(resultado)
        print('Multiplicando_inicial: ', '({})_c2'.format(resultado), '({})_c2'.format(-int(resultado,2)))
        #print('Multiplicando_inicial: ',Multiplicando_inicial, int(Multiplicando_inicial,2), '({})_c2'.format(resultado), '({})_c2'.format(-int(resultado,2)))

    if Multiplicador_inicial[0] == '0':
        print('Multiplicador_inicial: ',Multiplicador_inicial, int(Multiplicador_inicial,2))
    else:
        resultado = c1(Multiplicador_inicial)
        resultado = c2(resultado)
        print('Multiplicador_inicial: ','({})_c2'.format(resultado), '({})_c2'.format(-int(resultado,2)))
        #print('Multiplicador_inicial: ',Multiplicador_inicial, int(Multiplicador_inicial,2), '({})_c2'.format(resultado), '({})_c2'.format(-int(resultado,2)))
    
    if pdua.Memory[0][0] == '0':
        print('Resultado: ',pdua.Memory[0]+pdua.Memory[1], int(pdua.Memory[0]+pdua.Memory[1],2))
    else:
        resultado = c1(pdua.Memory[0]+pdua.Memory[1])
        resultado = c2(resultado, final=True)
        print('Resultado: ','({})_c2'.format(resultado), '({})_c2'.format(-int(resultado,2)))
        #print('Resultado: ',pdua.Memory[0]+pdua.Memory[1], int(pdua.Memory[0]+pdua.Memory[1],2), '({})_c2'.format(resultado), '({})_c2'.format(-int(resultado,2)))

    #from pprint import pprint

    #pprint(list(zip(bin_instructions, readable_inst)))
