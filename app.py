from flask import Flask, render_template
import main
app = Flask(__name__)

@app.route('/')
def hello_world():
    df, rec = main.all_ecfa()
    cf = main.all_courses()
    ovr = main.ovr_ecfa(df, rec)
    return render_template('test.html',
                           rows=df.to_dict(orient='records'),
                           rec_rows=rec.to_dict(orient='records'),
                           c_rows=cf.to_dict(orient='records'),
                           c_cols=cf.columns.to_list(),
                           cols=df.columns.to_list(),
                           ptt=ovr,
                           username = main.name())