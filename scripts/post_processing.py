import pandas as pd
from sys import argv
from os import listdir, mkdir
from os.path import join, exists
import matplotlib.pyplot as plt
from collections import Counter


def post_processing(dir, columns, func, output_dir):
    files = listdir(dir)
    for file in files:
        df = pd.read_csv(join(dir, file), header=None)
        df.columns = columns

        filtered = list(map(lambda x: x[1], filter(lambda x: x is not None, map(func, df.iterrows()))))
        counts = Counter(filtered)
        plt.scatter(counts.keys(), counts.values())
        plt.title(file)
        plt.ylabel('Number of entries')
        plt.savefig(join(output_dir, file.split('.')[0] + '.png'))
        plt.clf()

if __name__ == '__main__':
    if len(argv) != 3:
        print('Usage: python post_processing.py <path_to_csv_file> <output_dir>')
        exit(1)

    dir = argv[1]
    output_dir = argv[2]
    if not exists(output_dir):
        mkdir(output_dir)

    pipeline_columns = ['entry_number', '5_stage_nobypass', '5_stage_bypass', '79_stage_nobypass', '79_stage_bypass']
    func_79_nobypass = lambda row: (row[1]['entry_number'], row[1]['79_stage_nobypass']) if row[1]['79_stage_nobypass'] > 0 else None
    func_79_bypass = lambda row: (row[1]['entry_number'], row[1]['79_stage_bypass']) if row[1]['79_stage_bypass'] > 0 else None

    if not exists(join(output_dir, '79_stage_nobypass')):
        mkdir(join(output_dir, '79_stage_nobypass'))
    post_processing(join(dir, 'pipeline_csvs'), pipeline_columns, func_79_nobypass, join(output_dir, '79_stage_nobypass'))

    if not exists(join(output_dir, '79_stage_bypass')):
        mkdir(join(output_dir, '79_stage_bypass'))
    post_processing(join(dir, 'pipeline_csvs'), pipeline_columns, func_79_bypass, join(output_dir, '79_stage_bypass'))

    branch_predictor_columns = ['entry_number', '1_0', '1_1', '1_2', '1_3', '2_0', '2_1', '2_2', '2_3', '3_0', '3_1', '3_2', '3_3']
    func_bp = lambda row: (row[1]['entry_number'], (((row[1]['3_0'] + row[1]['3_1'] + row[1]['3_2'] + row[1]['3_3']) * 25) // 10))

    if not exists(join(output_dir, 'branch_predictor')):
        mkdir(join(output_dir, 'branch_predictor'))
    post_processing(join(dir, 'branch_predictor_csvs'), branch_predictor_columns, func_bp, join(output_dir, 'branch_predictor'))
