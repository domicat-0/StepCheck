from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from data_classes import fileman
from data_parse import course_parse, ecfa_parse
from data_classes import basis

app = Flask(__name__)

@app.route('/')
def run_main():
    try:
        ecfa_res, course_res, username, ecfa_ovr = fileman.from_file()
    except FileNotFoundError:
        get_uploader()
    return render_template('test.html',
                           rows=ecfa_res.to_dict(orient='records'),
                           cols=ecfa_res.columns.to_list(),
                           c_rows=course_res.to_dict(orient='records'),
                           c_cols=course_res.columns.to_list(),
                           ptt=ecfa_ovr,
                           username = username)


@app.route('/upload')
def get_uploader():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return run_main()