import os
import sys
golden_path = sys.argv[1]
output_path = sys.argv[2]


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
        cycle_info.append([register_line, memory_line])
    
    # if same alloted twice then ignore

    changes = {}

    for i in range(len(cycle_info)):
        if cycle_info[i][1].split(' ')[0] == '0':
            continue
        memory_loc = cycle_info[i][1].split(' ')[1]
        change_to = cycle_info[i][1].split(' ')[2]
        if memory_loc in changes and changes[memory_loc] == change_to:
            cycle_info[i][1] = '0'
        else:
            changes[memory_loc] = change_to
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

def check_relative_order(golden_cycle_info, output_cycle_info):
    unique_golden_order = [golden_cycle_info[0][0]]
    corresponding_memory_order = [[golden_cycle_info[0][1]]]
    for i in range(1,len(golden_cycle_info)):
        if not match_register(golden_cycle_info[i][0], unique_golden_order[-1]):
            unique_golden_order.append(golden_cycle_info[i][0])
            corresponding_memory_order.append([golden_cycle_info[i][1]])
        else:
            corresponding_memory_order[-1].append(golden_cycle_info[i][1])
    # for i in range(len(unique_golden_order)):
    #     print(unique_golden_order[i])
    #     if i < len(corresponding_memory_order):
    #         print(corresponding_memory_order[i])
    ouput_order = [x[0] for x in output_cycle_info]
    map_gold_to_out = {}
    curr_g = 0
    curr_o = 0
    while curr_g < len(unique_golden_order) and curr_o < len(ouput_order):
        if match_register(unique_golden_order[curr_g], ouput_order[curr_o]):
            map_gold_to_out[curr_g] = curr_o
            curr_g += 1
            curr_o += 1
        else:
            curr_o += 1
    
    for i in range(len(corresponding_memory_order)):
        for j in corresponding_memory_order[i]:
            if j == '0':
                continue
            flag = False
            # check if j is in between map_gold_to_out[i] and map_gold_to_out[i+1]
            for k in range(map_gold_to_out[i], map_gold_to_out[i+1]+1):
                if output_cycle_info[k][1] == j:
                    flag = True
                    break
            if not flag:
                return False
    return True
unpipelined_cycle_info = parse_file(golden_path)
# print(unpipelined_cycle_info)
output_cycle_info = parse_file(output_path)
# print(output_cycle_info)

print("Number of cycles taken:", len(output_cycle_info))
if unpipelined_cycle_info == output_cycle_info:
    print("1")
    exit()
if not check_register_order(unpipelined_cycle_info, output_cycle_info):
    print("0")
    print("Register order does not match")
    exit()
if not check_memory_order(unpipelined_cycle_info, output_cycle_info):
    print("0")
    print("Memory order does not match")
    exit()
if not check_relative_order(unpipelined_cycle_info, output_cycle_info):
    print("0")
    print("Relative memory-register order does not match")
    exit()

print("0.2")
print("Relative execution order is correct")

