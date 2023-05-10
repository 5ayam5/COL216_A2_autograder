import pandas as pd
from sys import argv

def get_df(file):
    # the first row of the csv file is the header
    df = pd.read_csv(file, header=0)
    return df

def filter_resubmissions(df):
    df = df[df['Valid?'] == 'yes']
    return df['Name of submitter on Moodle'].tolist()

if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: python filter_resubmissions.py <file>')
        exit(1)
    df = get_df(argv[1])
    resubmissions = filter_resubmissions(df)
    for resubmission in resubmissions:
        print(resubmission)
