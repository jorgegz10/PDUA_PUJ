import streamlit as st
from annotated_text import annotated_text
import pandas as pd
from io import StringIO
from src.compiler import remove_comments, split_instructions, decode_instructions, get_hex,c1,c2
from src.emulator import PDUAEmulator

uploaded_file = st.file_uploader("Choose a file", type=['asm'])
if uploaded_file is not None:
    # To read file as bytes:
    raw = uploaded_file.getvalue().decode("utf-8")
    #st.write(type(raw_asm))
    
    raw_asm = raw.split('\n')

    code_asm = remove_comments(raw_asm)
    instructions, jump_reference, variables = split_instructions(code_asm)

    hex_instructions, readable_inst = decode_instructions(instructions, jump_reference, variables)
    hex_instructions = [get_hex(x) for x in hex_instructions]
    pdua = PDUAEmulator()

    pdua.Reset()

    pdua.LoadProgram(hex_instructions, variables)
    Multiplicando_inicial = pdua.Memory[3]
    Multiplicador_inicial = pdua.Memory[1]
    ProgramCounter_list = [] #pdua.ProgramCounter
    readable_list = [] #readable_inst[pdua.ProgramCounter]
    reg_Acc_list = [] #pdua.Acc
    reg_A_list = [] #pdua.RegisterA
    reg_DPTR_list = [] # pdua.Dptr
    memory_list = [] # pdua.Memory
    ZeroFlag_list = [] #pdua.ZeroFlag
    NegativeFlag_list = [] #pdua.NegativeFlag
    OverflowFlag_list = [] #pdua.OverflowFlag


    while(not pdua.HaltFlag):

        try:
            pdua.Step() # revisar logica del shift
            ProgramCounter_list.append(pdua.ProgramCounter) #pdua.ProgramCounter
            readable_list.append(readable_inst[pdua.ProgramCounter]) #readable_inst[pdua.ProgramCounter]
            reg_Acc_list.append(pdua.Acc) #pdua.Acc
            reg_A_list.append(pdua.RegisterA) #pdua.RegisterA
            reg_DPTR_list.append(pdua.Dptr) # pdua.Dptr
            memory_list.append(pdua.Memory) # pdua.Memory
            ZeroFlag_list.append(pdua.ZeroFlag) #pdua.ZeroFlag
            NegativeFlag_list.append(pdua.NegativeFlag) #pdua.NegativeFlag
            OverflowFlag_list.append(pdua.OverflowFlag) #pdua.OverflowFlag
            

        except Exception as e:
            raise e
    
    df = pd.DataFrame({"PC": ProgramCounter_list, "ASM": readable_list,"Acc": reg_Acc_list,"A": reg_A_list, "DPTR":reg_DPTR_list})
    for i in range(len(df)-1):
        aa=list(df.iloc[i])
        bb=list(df.iloc[i+1])
        cc = [str(b) if a!=b else (str(b), "") for a,b in zip(aa,bb) ]

        annotated_text('|PC {: <3}'.format(cc[0]),'|{: <15}'.format(cc[1]),'|',cc[2],'|',cc[3],'|',cc[4])
    if Multiplicando_inicial[0] == '0':
        st.write('Multiplicando_inicial: ',Multiplicando_inicial, int(Multiplicando_inicial,2))
    else:
        resultado = c1(Multiplicando_inicial)
        resultado = c2(resultado)
        st.write('Multiplicando_inicial: ', '({})_c2'.format(resultado), -int(resultado,2))

    if Multiplicador_inicial[0] == '0':
        st.write('Multiplicador_inicial: ',Multiplicador_inicial, int(Multiplicador_inicial,2))
    else:
        resultado = c1(Multiplicador_inicial)
        resultado = c2(resultado)
        st.write('Multiplicador_inicial: ','({})_c2'.format(resultado), -int(resultado,2))
    
    if pdua.Memory[0][0] == '0':
        st.write('Resultado: ',pdua.Memory[0]+pdua.Memory[1], int(pdua.Memory[0]+pdua.Memory[1],2))
    else:
        resultado = c1(pdua.Memory[0]+pdua.Memory[1])
        resultado = c2(resultado, final=True)
        st.write('Resultado: ','({})_c2'.format(resultado), -int(resultado,2))