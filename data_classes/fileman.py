from zipfile import ZipFile
import os, re, shutil
import pandas as pd

from data_classes import basis
from data_parse import ecfa_parse, course_parse

files = ['profile_data.txt',
         'ecfa_data.csv',
         'course_data.csv']

def from_file():
    with ZipFile('./data.zip', 'r') as z:
        z.extractall('./temp/')

    course_res = pd.read_csv('./temp/course_data.csv')
    ecfa_res = pd.read_csv('./temp/ecfa_data.csv')

    with open('./temp/profile_data.txt') as f:
        lines = f.readlines()
        gex = r'(.*):(.*)'
        for i in lines:
            m = re.match(gex, i)
            key = m.group(1)
            val = m.group(2)
            if key == 'Name':
                username = val
            elif key == 'ECFA':
                ecfa_ovr = val

    shutil.rmtree('./temp')
    return ecfa_res, course_res, username, ecfa_ovr


def to_file():
    ecfa_res = ecfa_parse.parse_all()
    course_res = course_parse.parse_all()
    ecfa_ovr = ecfa_parse.ecfa_ovr(ecfa_res)

    ecfa_res.to_csv('ecfa_data.csv')
    course_res.to_csv('course_data.csv')
    with open('profile_data.txt', 'w') as f:
        f.write('Name:{};\n'.format(basis.username))
        f.write('ECFA:{};\n'.format(ecfa_ovr))

    files = ['profile_data.txt',
             'ecfa_data.csv',
             'course_data.csv']  # Add to this when new files are added

    try:
        os.remove('data.zip')
    except FileNotFoundError:
        pass
    with ZipFile('data.zip', 'x') as z:
        for i in files:
            z.write(i)
            os.remove(i)