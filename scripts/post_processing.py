import pandas as pd
from sys import argv
from os import listdir, mkdir
from os.path import join, exists, basename
from math import ceil
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

scores = defaultdict(lambda: {'5_stage_nobypass': 0, '5_stage_bypass': 0,
                     '79_stage_nobypass': 0, '79_stage_bypass': 0, 'branch_predictor': 0, 'penalty': 0})


def scoring_5(case, score_dict, value, prefix_sum, total):
    if value is not None:
        if value == 0:
            score_dict[case] += 2
        elif value == 1:
            score_dict[case] += 10


def scoring_79(case, score_dict, value, prefix_sum, total):
    if value is not None:
        if prefix_sum < total * 0.1 or prefix_sum > total * 0.9:
            score_dict[case] += 2
        else:
            score_dict[case] += 10


def scoring_bp(case, score_dict, value, prefix_sum, total):
    score_dict[case] += value


def post_processing(dir, columns, func, scoring, output_dir, plot=False):
    files = listdir(dir)
    for file in files:
        df = pd.read_csv(join(dir, file), header=None)
        df.columns = columns

        filtered = list(map(lambda x: x[1], filter(
            lambda x: x[1] is not None, map(func, df.iterrows()))))
        if file == 'branchtrace.txt.csv':
            filtered = [x + 1 for x in filtered]
        counts = Counter(filtered)

        total = len(filtered)
        prefix_sums = {None: 0}
        curr = 0
        for key in sorted(counts.keys()):
            curr += counts[key]
            prefix_sums[key] = curr

        for student in df.iterrows():
            temp = func(student)
            if file == 'branchtrace.txt.csv':
                temp = (temp[0], temp[1] + 1)
            scoring(basename(output_dir),
                    scores[temp[0]], temp[1], prefix_sums[temp[1]], total)

        if plot:
            plt.scatter(counts.keys(), counts.values())
            plt.title(file)
            plt.ylabel('Number of entries')
            plt.savefig(join(output_dir, file.split('.')[0] + '.png'))
            plt.clf()


def apply_penalty(resubmissions):
    for student in resubmissions.iterrows():
        key = student[1]['Entry Numbers']
        penalty = student[1]['Penalty?']
        if 'z' in penalty:
            scores[key]['penalty'] += 1
        if 'm' in penalty:
            scores[key]['penalty'] += 1
        if 'f' in penalty:
            scores[key]['penalty'] += 1
        if 'o' in penalty:
            scores[key]['penalty'] += 2


if __name__ == '__main__':
    if len(argv) != 4:
        print('Usage: python post_processing.py <path_to_results_dir> <output_dir> <resubmissions.csv>')
        exit(1)

    dir = argv[1]
    output_dir = argv[2]
    if not exists(output_dir):
        mkdir(output_dir)
    resubmissions = pd.read_csv(argv[3], header=0)

    pipeline_columns = ['entry_number', '5_stage_nobypass',
                        '5_stage_bypass', '79_stage_nobypass', '79_stage_bypass']

    def func_5_nobypass(row): return (
        row[1]['entry_number'], row[1]['5_stage_nobypass'] if row[1]['5_stage_nobypass'] > 0 else None)

    def func_5_bypass(row): return (
        row[1]['entry_number'], row[1]['5_stage_bypass'] if row[1]['5_stage_bypass'] > 0 else None)

    def func_79_nobypass(row): return (
        row[1]['entry_number'], row[1]['79_stage_nobypass'] if row[1]['79_stage_nobypass'] > 0 else None)

    def func_79_bypass(row): return (
        row[1]['entry_number'], row[1]['79_stage_bypass'] if row[1]['79_stage_bypass'] > 0 else None)

    post_processing(join(dir, 'pipeline_csvs'), pipeline_columns,
                    func_5_nobypass, scoring_5, '5_stage_nobypass')
    post_processing(join(dir, 'pipeline_csvs'), pipeline_columns,
                    func_5_bypass, scoring_5, '5_stage_bypass')

    if not exists(join(output_dir, '79_stage_nobypass')):
        mkdir(join(output_dir, '79_stage_nobypass'))
    post_processing(join(dir, 'pipeline_csvs'), pipeline_columns, func_79_nobypass,
                    scoring_79, join(output_dir, '79_stage_nobypass'), True)

    if not exists(join(output_dir, '79_stage_bypass')):
        mkdir(join(output_dir, '79_stage_bypass'))
    post_processing(join(dir, 'pipeline_csvs'), pipeline_columns,
                    func_79_bypass, scoring_79, join(output_dir, '79_stage_bypass'), True)

    branch_predictor_columns = ['entry_number', '1_0', '1_1', '1_2',
                                '1_3', '2_0', '2_1', '2_2', '2_3', '3_0', '3_1', '3_2', '3_3']

    def func_bp(row): return (row[1]['entry_number'], ceil(
        10 * (row[1]['3_0'] + row[1]['3_1'] + row[1]['3_2'] + row[1]['3_3']) / 4))

    if not exists(join(output_dir, 'branch_predictor')):
        mkdir(join(output_dir, 'branch_predictor'))
    post_processing(join(dir, 'branch_predictor_csvs'), branch_predictor_columns,
                    func_bp, scoring_bp, join(output_dir, 'branch_predictor'), True)

    apply_penalty(resubmissions)

    with open(join(output_dir, 'scores.csv'), 'w+') as f:
        f.write("Entrynum 1,Entrynum 2,5 stage nobypass,5 stage bypass,79 stage nobypass,79 stage bypass,branch predictor,report,penalty\n")
        for key in scores.keys():
            entrynum1, entrynum2 = key.split('_')
            f.write("{},{},{},{},{},{},{},,{}\n".format(
                entrynum1, entrynum2, scores[key]['5_stage_nobypass'] * 1.0 / 90, scores[key]['5_stage_bypass'] * 1.0 / 90,
                scores[key]['79_stage_nobypass'] * 1.0 / 90, scores[key]['79_stage_bypass'] * 1.0 / 90,
                scores[key]['branch_predictor'] * 1.0 / 60, scores[key]['penalty'] / 2))
