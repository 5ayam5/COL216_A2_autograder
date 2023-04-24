import os
import sys

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

def check_correctness(unpipelined_cycle_info, output_cycle_info):
    if not check_register_order(unpipelined_cycle_info, output_cycle_info):
        return False
    if not check_memory_order(unpipelined_cycle_info, output_cycle_info):
        return False
    if not check_relative_order(unpipelined_cycle_info, output_cycle_info):
        return False
    return True

def check_output(unpipelined_cycle_info, output_path, test_case_to_be_checked):
    try:
        output_cycle_info = parse_file(output_path)

        cycles = len(output_cycle_info)
        if test_case_to_be_checked == '5':
            if unpipelined_cycle_info == output_cycle_info:
                cycles = 1
            elif check_correctness(unpipelined_cycle_info, output_cycle_info):
                cycles = 0
            else:
                cycles = -1
            return cycles

        if check_correctness(unpipelined_cycle_info, output_cycle_info):
            return cycles
        else:
            return -1
    except Exception:
        return -2

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 check.py <golden_path> <output_dir>")
        exit(1)
    golden_path = sys.argv[1]
    output_dir = sys.argv[2]


    for testcase in os.listdir(golden_path):
        f = open(os.path.join(output_dir, testcase + ".csv"), 'w+')
        unpipelined_cycle_infos = dict()
        unpipelined_cycle_infos[('5', 'nobypass')] = parse_file(os.path.join(golden_path, testcase, '5_nobypass'))
        unpipelined_cycle_infos[('5', 'bypass')] = parse_file(os.path.join(golden_path, testcase, '5_bypass'))
        unpipelined_cycle_infos[('79', 'nobypass')] = unpipelined_cycle_infos[('79', 'bypass')] = parse_file(os.path.join(golden_path, testcase, '79'))

        for student in os.listdir(os.path.join(output_dir, "pipeline")):
            f.write(student[:-3] + ',')
            for stage in ('5', '79'):
                for case in ('nobypass', 'bypass'):
                    f.write(str(check_output(unpipelined_cycle_infos[(stage, case)], os.path.join(output_dir, "pipeline", student, testcase, stage + '_' + case), stage)) + ',')
            f.seek(f.tell() - 1)
            f.write('\n')

        f.close()
