from zipfile import ZipFile
import pandas as pd
import re, shutil, math

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

def level_repr(level):
    integer_part = math.floor(level)
    fractional_part = level - integer_part
    repr = str(integer_part)
    if fractional_part >= 0.7:
        repr += '+'
    elif fractional_part <= 0.2:
        repr += '-'
    return repr