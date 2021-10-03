from zipfile import ZipFile
import os, re, shutil
import pandas as pd

from data_parse import ecfa_parse, course_parse

files = ['profile_data.txt',
         'ecfa_data.csv',
         'course_data.csv'] 


def to_file():
    from data_classes import basis
    ecfa_res = ecfa_parse.parse_all()
    course_res = course_parse.parse_all()
    ecfa_ovr = ecfa_parse.ecfa_ovr(ecfa_res)
    print(ecfa_res.sort_values('Timestamp'))
    ecfa_res.to_csv('ecfa_data.csv')
    course_res.to_csv('course_data.csv')
    with open('profile_data.txt', 'w') as f:
        f.write('Name:{}\n'.format(basis.username))
        f.write('ECFA:{}\n'.format(ecfa_ovr))

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