addi $t1, $0, 10
addi $t2, $0, 20
add $t3, $t1, $t2
sw $t3, 0($t1)
addi $t4, $0, 30
lw $t5, 0($t1)
add $t6, $t5, $t4
add $t7, $t6, $t3