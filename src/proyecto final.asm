variableA: 0b0
Q: 0b10000001
Q_1: 0b0
M: 0b11111101
count: 0x8
AUX: 0b0
bandera_Q: 0b0
bandera_A: 0b0

condicion_if:
  CALL lsb
  MOV ACC, Q_1
  MOV DPTR, ACC

  MOV ACC, A
  INV ACC
  MOV A, ACC
  MOV ACC, [DPTR]
  AND ACC, A
  MOV A, ACC
  MOV ACC, AUX
  MOV DPTR, ACC
  MOV ACC, A
  MOV [DPTR], ACC
  CALL lsb

  MOV ACC, Q_1
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  INV ACC
  AND ACC, A
  MOV A, ACC
  MOV ACC, AUX
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A

  JZ arithmetic_shift
  CALL lsb
  MOV ACC, A
  INV ACC
  MOV A, ACC
  MOV ACC, 0b1
  ADD ACC, A
  MOV A, ACC
  MOV ACC, Q_1
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A
  JN caso_10

  MOV ACC, M
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  MOV A, ACC
  MOV ACC, variableA
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A
  MOV [DPTR], ACC
  JMP arithmetic_shift

caso_10:
  MOV ACC, M
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  INV ACC
  MOV A, ACC
  MOV ACC, 0b1
  ADD ACC, A
  MOV A, ACC
  MOV ACC, variableA
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A
  MOV [DPTR], ACC

arithmetic_shift:
  MOV ACC, variableA
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  MOV A, ACC
  MOV ACC, 0b1
  AND ACC, A
  MOV A, ACC
  MOV ACC, bandera_Q
  MOV DPTR, ACC
  MOV ACC, A
  MOV [DPTR], ACC

  MOV ACC, variableA
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  MOV A, ACC
  MOV ACC, 0b10000000
  AND ACC, A
  MOV A, ACC
  MOV ACC, bandera_A
  MOV DPTR, ACC
  MOV ACC, A
  MOV [DPTR], ACC

  MOV ACC, variableA
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  RSH ACC, 0b1
  MOV [DPTR], ACC

  MOV ACC, bandera_A
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  MOV A, ACC
  MOV ACC, 0b0
  ADD ACC, A
  JZ corrimientoQ

  MOV ACC, 0b10000000
  MOV A, ACC
  MOV ACC, variableA
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A
  MOV [DPTR], ACC

corrimientoQ:
  CALL lsb
  MOV ACC, Q_1
  MOV DPTR, ACC
  MOV ACC, A
  MOV [DPTR], ACC

  MOV ACC, Q
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  RSH ACC, 0b1
  MOV [DPTR], ACC

  MOV ACC, bandera_Q
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  MOV A, ACC
  MOV ACC, 0b0
  ADD ACC, A
  JZ no_sumarMSB

  MOV ACC, 0b10000000
  MOV A, ACC
  MOV ACC, Q
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A
  MOV [DPTR], ACC

no_sumarMSB:
  MOV ACC, 0b1
  INV ACC
  MOV A, ACC
  MOV ACC, 0b1
  ADD ACC, A
  MOV A, ACC
  MOV ACC, count
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  ADD ACC, A
  MOV A, ACC
  MOV [DPTR], ACC

  MOV ACC, count
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  INV ACC
  MOV A, ACC
  MOV ACC, 0b1
  ADD ACC, A
  JN condicion_if
  HLT

lsb: 
  MOV ACC, Q
  MOV DPTR, ACC
  MOV ACC, [DPTR]
  MOV A, ACC
  MOV ACC, 0b1
  AND ACC, A
  MOV A, ACC
  RET
