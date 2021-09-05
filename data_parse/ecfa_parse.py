import pandas as pd
import numpy as np
import glob

from data_classes import basis
from data_classes.song import Song

def ptt(level, score):
    if score < 0.7:
        return 0
    elif 0.7 < score < 0.9:
        delta = 10*score - 8.5 # -1.5 to 0.5
    elif 0.9 < score < 0.96:
        delta = 15*score - 13 # 0.5 to 1.4
    elif score != 1:
        delta = 20*score - 17.8 # 1.4 to 2.2
    else:
        delta = 2.5
    return round(level + delta, 2)

def parse_all():
    zeta = glob.glob(basis.game_dir+'/Songs/ECFA*/*/*.sm') + glob.glob(basis.game_dir+'/Songs/ECFA*/*/*.ssc')
    songs = []
    scores = []
    ecfa_results = []
    for i in zeta:
        s = Song(i, True)
        if s.bad:
            continue
        for i in s.scores:
            ecfa_results.append({'Title': s.title,
                       'Difficulty': basis.diff_names[i.diff],
                       'Level': s.diffs[i.diff]/10,
                       'Percent': round(i.percent * 100, 2),
                       'Potential': ptt(s.diffs[i.diff]/10, i.percent),
                       'Timestamp': i.datetime})

    ecfa_results = pd.DataFrame(ecfa_results)
    return ecfa_results

def ecfa_ovr(data):
    rec = data.sort_values(by='Timestamp')[::-1]
    rec = rec.head(30)
    rec = rec.sort_values(by='Potential')[::-1]
    data = data.sort_values(by='Potential')[::-1]
    rec = rec.head(10)
    data = data.head(30)

    v = data['Potential'][:50]
    w = rec['Potential'][:20]
    return round(np.mean(v)*0.8 + np.mean(w)*0.2  * (1/70) * (len(v) + len(w)), 2)