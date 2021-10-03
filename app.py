from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from data_parse import file_parse
import math
import pandas as pd

app = Flask(__name__)

@app.route('/')


def run_main():
    try:
        ecfa_res, course_res, username, ecfa_ovr = file_parse.from_file()
        print(ecfa_res.columns)


    except FileNotFoundError:
        print('Failure')
        get_uploader()

    ecfa_res.drop('Unnamed: 0', axis=1, inplace=True)

    by_level = {level:
                    ecfa_res[(level < ecfa_res['Level'])
                             & (ecfa_res['Level'] < level + 1)
                             ]
                    .sort_values('Potential', ascending=False)
                    .drop_duplicates('Level')
                    .sort_values('Level', ascending=False)
                    for level in [7, 8, 9, 10, 11, 12, 13, 14]}

    fail_by_level = {}
    fc_by_level = {}
    fec_by_level = {}
    max_by_level = {}

    for i in by_level.keys():
        lv = by_level[i]
        max_by_level[i] = lv[lv["Status"] == 'MAX']
        fec_by_level[i] = lv[lv["Status"] == 'FEC']
        fc_by_level[i] = lv[lv["Status"] == 'FC']
        by_level[i] = lv[lv["Status"] == 'Pass']
        fail_by_level[i] = lv[lv["Status"] == 'Fail']


    return render_template('main_page.html',
                           max_by_level = max_by_level,
                           fec_by_level = fec_by_level,
                           fc_by_level = fc_by_level,
                           by_level = by_level,
                           fail_by_level = fail_by_level,
                           cols=ecfa_res.columns.values,
                           c_rows=course_res.to_dict(orient='records'),
                           c_cols=course_res.columns.to_list(),
                           ptt=ecfa_ovr,
                           username = username,
                           _level = file_parse.level_repr)


@app.route('/upload')
def get_uploader():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return run_main()