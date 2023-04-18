import os
import sys
test_case_name = 'public_test4'
unpipelined_path = os.path.join('unpipelined_outputs', test_case_name+'.out')
output_path = sys.argv[1]


def parse_file(file_path):
    with open(file_path, 'r') as f:
        raw_lines = f.readlines()
    lines = []
    for line in raw_lines:
        line = line.strip()
        if line == '':
            break
        lines.append(line)
    assert len(lines) % 2 == 0, "Number of lines in output file must be even"
    cycle_info = []
    for i in range(0, len(lines), 2):
        register_line = lines[i]
        memory_line = lines[i + 1]
        assert len(register_line.split(' ')) == 32, f"Register line at {i} does not have 32 registers"
        len_memory_line = int(memory_line.split(' ')[0])
        if len_memory_line > 0:
            assert len(memory_line.split(' ')) == 2*len_memory_line+1, f"Memory line at {i} does not have correct number of memory locations"
        cycle_info.append((register_line, memory_line))
    return cycle_info

def match_register(register_line1, register_line2):
    registers1 = register_line1.split(' ')
    registers2 = register_line2.split(' ')
    for i in range(32):
        if registers1[i] != registers2[i]:
            return False
    return True

def get_unique_register_order(register_order):
    out = [register_order[0]]
    for i in range(1,len(register_order)):
        if not match_register(register_order[i], out[-1]):
            out.append(register_order[i])
    return out

def check_register_order(golden_cycle_info, output_cycle_info):
    unique_golden_register_order = get_unique_register_order([x[0] for x in golden_cycle_info])
    unique_output_register_order = get_unique_register_order([x[0] for x in output_cycle_info])
    if len(unique_golden_register_order) != len(unique_output_register_order):
        return False
    for i in range(len(unique_golden_register_order)):
        if not match_register(unique_golden_register_order[i], unique_output_register_order[i]):
            return False
    return True

def check_memory_order(golden_cycle_info, output_cycle_info):
    non_zero_golden_memory_locs = [i[1] for i in golden_cycle_info if i[1] != '0']
    non_zero_output_memory_locs = [i[1] for i in output_cycle_info if i[1] != '0']
    if len(non_zero_golden_memory_locs) != len(non_zero_output_memory_locs):
        return False
    for i in range(len(non_zero_golden_memory_locs)):
        if non_zero_golden_memory_locs[i] != non_zero_output_memory_locs[i]:
            return False
    return True


unpipelined_cycle_info = parse_file(unpipelined_path)
output_cycle_info = parse_file(output_path)
print(check_register_order(unpipelined_cycle_info, output_cycle_info))
print(check_memory_order(unpipelined_cycle_info, output_cycle_info))
