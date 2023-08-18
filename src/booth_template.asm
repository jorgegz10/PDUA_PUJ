; Template para Algoritmo de booth
registroA: 0b0
Q: 0b10000001 ; Multiplicador
Q_1: 0b0
M: 0b11111101; Multiplicando
count: 0x8



inicio:
	; Se carga el mutliplier a A
	mov ACC, Q
    mov DPTR, ACC
	mov ACC, [DPTR]
	mov A, ACC

	hlt ; Se detiene la ejecucion