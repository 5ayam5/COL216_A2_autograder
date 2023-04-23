addi $t1, $0, 0
addi $t2, $0, 3
addi $t3, $0, 0
addi $t4, $0, 3
addi $t5, $0, 0
outer_loop:
addi $t3, $0, 0
inner_loop:
add $t5, $t5, $t1
add $t5, $t5, $t3
addi $t3, $t3, 1
bne $t3, $t4, inner_loop
addi $t1, $t1, 1
bne $t1, $t2, outer_loop