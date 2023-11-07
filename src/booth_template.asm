; Template para Algoritmo de booth

; Observe que los comentarios están especificados usando ";"
; por lo tanto, todo lo que encuentre despues de este simbolo así será tratado.


; Hasta este punto del curso se asume llena la información a operar en memoria
; Acá se describe como cargar los datos para la ejecución y como usarlos

; Cada variable que se desee usar debe definirse usando un nombre, una serie de caracteres (Palabras) 
; Para identificar ques es una variable se debe usar ":" y posteriormente agregar el valor inicial
; el valor inicial puede agregarse en binario o hexadecimal, recuerde agregar el prefijo correspondiente
; "0b" para binario o "0x para hexadecimal".
; Aunque parece una asignación directa, recuerde que debe usar el DTPR para acceder a esta información
; pues al hacer referencia al nombre de la variable, se accederá a la posición de memoria de la misma,
; no a su contenido.

; Para el algoritmo de booth son necesarias las siguientes variables
; aunque el nombre no es importante, es recomendable mantenerlo.
; Es importante mantener el orden de estas variables, pues la visualización de la interfaz web
; se basa en la dirección de memoria, no en el nombre de la variable.

variableA: 0b0 
Q: 0b10000001 ; Multiplicador
Q_1: 0b0
M: 0b11111101; Multiplicando
count: 0x8

; Es importante destacar una diferencia en este punto, un indice para realizar saltos en el código
; se define usando el simbolo ":" al igual que la definición de una variable
; La diferencia radica en la asignación del valor, es decir, si no se detecta valor, 
; se establece esa pocisión de código como indice

inicio:
	; Es importante resaltar una diferencia en esta implementación,
	; por simplicidad en el código cuando se usa una instrucción que contiene "CTE"
	; esto se reemplaza bien sea por el valor (binario o hexadecimal) que se desea usar
	; o por el nombre de la variable / indice al cual se hace referencía
	; es decir: No se escribiría la siguiente instrucción de cargar dirección 
	; de memoria de Q en Acc como:
	; mov ACC, CTE
	; Q
	; en esta implementación se debe escribir así:
	; mov ACC, Q


	; Evalúa sí Acc es cero
	jz load_a
ind_1:
	; Se carga la variable Q a registro A
	mov ACC, Q
    mov DPTR, ACC
	mov ACC, [DPTR]
	mov A, ACC
	call fn_1 

	hlt ; Se detiene la ejecucion


load_a:
	; Se carga Variable A a Acc
	mov ACC, variableA
    mov DPTR, ACC
	mov ACC, [DPTR]
	jz ind_1
	hlt

fn_1:
	; Se carga Variable count a Acc
	mov ACC, count
    mov DPTR, ACC
	mov ACC, [DPTR]
	ret ;retorna al punto donde se ejecutó CALL CTE