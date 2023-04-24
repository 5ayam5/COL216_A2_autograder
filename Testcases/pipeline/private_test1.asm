addi $t1, $0, 8
addi $t2, $0, 12
sw $t1, 0($t2)
lw $t3, 0($t2)
add $t4, $t3, $t3
add $t5, $t3, $t4
sw $t5, 4($t2)
lw $t6, 4($t2)
add $t7, $t6, $t6