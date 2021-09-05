import glob
from flask import Markup
import pandas as pd

from data_classes.course import Course
from data_classes import basis


def parse_all():
    zeta = glob.glob(basis.game_dir+'/Courses/*/*.crs')
    courses = []
    scores = []
    course_res = []
    for i in zeta:
        s = Course(i)
        if s.bad:
            # continue
            pass
        for i in s.scores:
            course_res.append({'Title': s.title,
                       'Songs': Markup('<br/>'.join(s.songs)),
                       'Percent': round(i.percent * 100, 2),
                       'Timestamp': i.datetime})
        return pd.DataFrame(course_res)