
CODE 0	; 0
;program exit point
	halt 0


DATA 2	; 0
dump 2e342e31 65642d35 76 312f3730 30322f38 3231 303a3132 31333a31 0 5 0 c 18 
dump 0 0 0
dump 0
dump 65726f43 0 65726f63 0 44 4c 0 0 

CODE 2	; 8
	proc	; __ext_core_SetNTVOptional
	; line a5
	break	; c
	; line a6
	break	; 10
	push.c 64
	;$par
	sysreq.n 0 1
	;$exp
	; line a7
	break	; 28
	push.c 78
	;$par
	sysreq.n 0 1
	;$exp
	; line a8
	break	; 40
	push.c 88
	;$par
	sysreq.n 0 1
	;$exp
	; line a9
	break	; 58
	push.c 9c
	;$par
	sysreq.n 0 1
	;$exp
	; line aa
	break	; 70
	sysreq.n 1 0
	;$exp
	zero.pri
	retn


DATA 2	; 64
dump 46746547 75746165 74536572 73757461 0 75716552 46657269 75746165 6572 43646441 616d6d6f 694c646e 6e657473 7265 6f6d6552 6f436576 
dump 6e616d6d 73694c64 656e6574 72 

DATA 13	; b4
dump 0

DATA 0	; b8
dump 4d537950 65542058 7473 59656874 616d4b34 6e 74736554 756c7020 6e692d67 726f6620 65687420 53795020 5620584d 4d 302e30 70747468 
dump 2f2f3a73 68746967 632e6275 742f6d6f 34596568 6e616d4b 7379702f 2f786d b8 d0 c4 f0 f4 

CODE 0	; 88
	proc	; OnPluginStart
	; line c
	break	; 8c
	; line d
	break	; 90
	;$lcl percent fffffffc
	push.c 64
	;$exp
	; line e
	break	; 9c
	;$lcl i fffffff8
	push.c 0
	;$exp
	jump 8d
l.8b		; b0
	; line e
	break	; b0
	inc.s fffffff8
	;$exp
l.8d
	load.s.pri fffffff8
	const.alt a
	jsgeq 8c
	;$exp
	; line f
	break	; d4
	load.s.both fffffff8 fffffffc
	add
	stor.s.pri fffffffc
	;$exp
	jump 8b
l.8c		; f8
	stack 4
	; line 11
	break	; 100
	const.pri cafed00d
	heap 4
	stor.i
	push.alt
	;$par
	const.pri deadbeef
	heap 4
	stor.i
	push.alt
	;$par
	const.pri 40a9999a
	heap 4
	stor.i
	push.alt
	;$par
	push.adr fffffffc
	;$par
	const.pri 73
	heap 4
	stor.i
	push.alt
	;$par
	push2.c 180 12c
	;$par
	sysreq.n 2 7
	heap fffffff0
	;$exp
	; line 12
	break	; 18c
	push.c 0
	call Test
	;$exp
	stack 4
	zero.pri
	retn


DATA 0	; 12c
dump 66207325 74636e75 256e6f69 6f772063 25206b72 20252564 2d2f2b28 332e2520 6f202966 68742066 69742065 2021656d 6c206f4e 65676e6f 78302072 2d207825 
dump 6f6e202d 65772077 20657227 58257830 21 6d726f46 7461 

CODE 0	; 1b0
	proc	; Test
	; line 16
	break	; 1b4
	; line 17
	break	; 1b8
	push.c 188
	;$par
	sysreq.n 2 1
	;$exp
	zero.pri
	retn


DATA 0	; 188
dump 6c6c6143 54206465 28747365 29 

STKSIZE 1000
