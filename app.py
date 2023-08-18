import streamlit as st
import pandas as pd
from io import StringIO
from src.compiler import remove_comments, split_instructions, decode_instructions, get_hex,c1,c2
from src.emulator import PDUAEmulator
if 'allow_file' not in st.session_state:
    st.session_state['allow_file'] = False

def get_answer(Multiplicando_inicial, Multiplicador_inicial, pdua):
        if Multiplicando_inicial[0] == '0':
            #st.write('Multiplicando_inicial: ',Multiplicando_inicial, int(Multiplicando_inicial,2))
            _multiplicando_inicial = ('Multiplicando_inicial: ',Multiplicando_inicial, int(Multiplicando_inicial,2))
        else:
            resultado = c1(Multiplicando_inicial)
            resultado = c2(resultado)
            _multiplicando_inicial = ('Multiplicando_inicial: ', '({})_c2'.format(resultado), -int(resultado,2))

        if Multiplicador_inicial[0] == '0':
            _multiplicador_inicial = ('Multiplicador_inicial: ',Multiplicador_inicial, int(Multiplicador_inicial,2))
        else:
            resultado = c1(Multiplicador_inicial)
            resultado = c2(resultado)
            _multiplicador_inicial = ('Multiplicador_inicial: ','({})_c2'.format(resultado), -int(resultado,2))
        
        if pdua.Memory[0][0] == '0':
            _resultado = ('Resultado: ',pdua.Memory[0]+pdua.Memory[1], int(pdua.Memory[0]+pdua.Memory[1],2))
        else:
            resultado = c1(pdua.Memory[0]+pdua.Memory[1])
            resultado = c2(resultado, final=True)
            _resultado = ('Resultado: ','({})_c2'.format(resultado), -int(resultado,2))
        return _multiplicando_inicial, _multiplicador_inicial, _resultado

if 'df' in st.session_state:
    st.session_state['allow_file'] = True

uploaded_file = st.file_uploader("Seleccione Codigo Ensamblador para PDUA", type=['asm'],
                                 disabled=st.session_state['allow_file'])
if uploaded_file is not None or 'uploaded_file' in st.session_state:
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = uploaded_file
    else:
        uploaded_file = st.session_state['uploaded_file']
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
    pdua.check_variables()
    pdua.check_halt()

    Multiplicando_inicial = pdua.Memory[3]
    Multiplicador_inicial = pdua.Memory[1]
    ProgramCounter_list = [] #pdua.ProgramCounter
    readable_list = [] #readable_inst[pdua.ProgramCounter]
    reg_Acc_list = [] #pdua.Acc
    reg_A_list = [] #pdua.RegisterA
    reg_DPTR_list = [] # pdua.Dptr
    memory_A_list = [] # pdua.Memory[]
    memory_Q_list = [] # pdua.Memory[]
    memory_Q_1_list = [] # pdua.Memory[]
    memory_M_list = [] # pdua.Memory[]
    memory_Count_list = [] # pdua.Memory[]
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
            memory_A_list.append(pdua.Memory[0]) # pdua.Memory[0]
            memory_Q_list.append(pdua.Memory[1]) # pdua.Memory[1]
            memory_Q_1_list.append(pdua.Memory[2]) # pdua.Memory[2]
            memory_M_list.append(pdua.Memory[3])# pdua.Memory[3]
            memory_Count_list.append(pdua.Memory[4]) # pdua.Memory[4]
            ZeroFlag_list.append(pdua.ZeroFlag) #pdua.ZeroFlag
            NegativeFlag_list.append(pdua.NegativeFlag) #pdua.NegativeFlag
            OverflowFlag_list.append(pdua.OverflowFlag) #pdua.OverflowFlag
            

        except Exception as e:
            raise e
    
    st.write('hi')
    
    df = pd.DataFrame({"PC": ProgramCounter_list,
                       "ASM": readable_list,
                       "Acc": reg_Acc_list,
                       "A": reg_A_list,
                       "DPTR": reg_DPTR_list,
                       "A": memory_A_list,
                       "Q": memory_Q_list,
                       "Q-1": memory_Q_1_list,
                       "M": memory_M_list,
                       "Count": memory_Count_list,
                       "Flag_Z": ZeroFlag_list,
                       "Flag_ N": NegativeFlag_list,
                       "Flag_c": OverflowFlag_list,
                       })
    
    if 'df' not in st.session_state:
        st.session_state['df'] = df
    if 'row' not in st.session_state:
        st.session_state['row'] = 0
    if 'max' not in st.session_state:
        st.session_state['max'] = len(df)
    
    if st.button('Step()'):
        if st.session_state['row'] < st.session_state['max']:
            st.session_state['row'] += 1
    if st.button('run all'):
        st.session_state['row'] = st.session_state['max']
        _multiplicando_inicial, _multiplicador_inicial, _resultado = get_answer(Multiplicando_inicial, Multiplicador_inicial, pdua)
        col1, col2, col3 = st.columns(3)
        col1.metric(_multiplicando_inicial[0], _multiplicando_inicial[2], _multiplicando_inicial[1])
        col2.metric(_multiplicando_inicial[0], _multiplicador_inicial[2], _multiplicando_inicial[1])
        col3.metric(_resultado[0], _resultado[2], _resultado[1])
    
    st.dataframe(st.session_state['df'][:st.session_state['row']], hide_index=True, use_container_width=True)
    # for i in range(len(df)-1):
    #     aa=list(df.iloc[i])
    #     bb=list(df.iloc[i+1])
    #     cc = [str(b) if a!=b else (str(b), "") for a,b in zip(aa,bb) ]

    #     annotated_text('|PC {: <3}'.format(cc[0]),'|{: <15}'.format(cc[1]),'|',cc[2],'|',cc[3],'|',cc[4])
    