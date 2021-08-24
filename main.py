# Imports
import hashlib, re, lxml.etree, glob
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import configparser
from flask import Markup

parser = configparser.ConfigParser()
parser.read('config.ini')

diff_names = ['beginner', 'easy', 'medium', 'hard', 'challenge', 'edit']
grade_thresholds = [1, 0.99, 0.98, 0.96, 0.94, 0.92, 0.89, 0.86, 0.83, 0.8, 0.76, 0.72, 0.68, 0.64, 0.6, 0.55]
ecfa_grade_thresholds = [1, 0.99, 0.97, 0.95, 0.9, 0.8, 0.7]

# game_dir = 'C:/Games/StepMania 5.3 Outfox'
game_dir = parser['Location']['game_dir']
stats_url_waterfall = game_dir + '/Save/LocalProfiles/{}/WF-Stats.xml'.format(parser['Location']['profile'])
stats_url = game_dir + '/Save/LocalProfiles/{}/Stats.xml'.format(parser['Location']['profile'])
root_waterfall = lxml.etree.parse(stats_url_waterfall).getroot()
root = lxml.etree.parse(stats_url).getroot()
for i in root:
    if i.tag == 'SongScores':
        song_scores = i
    if i.tag == 'CourseScores':
        course_scores = i
    if i.tag == 'GeneralData':
        for j in i:
            if j.tag == 'DisplayName':
                username = j.text

for i in root_waterfall:
    if i.tag == 'SongScores':
        song_scores_waterfall = i
    if i.tag == 'CourseScores':
        course_scores_waterfall = i



class Song:
    def __init__(self, path, ecfa=False):

        self.path = path

        self.bad = False
        self.scores = []



        self.is_sm = False
        self.is_ssc = False
        if self.path[-1] == 'm':
            self.is_sm = True
        elif self.path[-1] == 'c':
            self.is_ssc = True
        with open(self.path, 'r', encoding='utf-8') as f:
            self.raw_data = [a.rstrip() for a in f.readlines()]
        with open(self.path, 'rb') as f:
            h = hashlib.md5()
            h.update(f.read())
            self.hash = h.hexdigest()

        if self.get_scores() == -1:
            self.bad = True

        self.diffs = [None for _ in range(6)]
        self.title = None


        if self.is_sm:
            lineparse = r'#(.*):(.*);'
            notesparse = r'\s*(.*):'
            intro = True
            for line in range(len(self.raw_data)):
                if '#NOTES' in self.raw_data[line]:
                    if re.match(notesparse, self.raw_data[line+1]).groups()[0] != 'dance-single':
                        continue
                    diff = diff_names.index((re.match(notesparse, self.raw_data[line+3]).groups()[0]).lower())
                    self.diffs[diff] = int(re.match(notesparse, self.raw_data[line+4]).groups()[0]) * 10 + 5
                    intro = False
                elif intro:
                    if not (parsed_line := re.match(lineparse, self.raw_data[line])):
                        continue
                    if parsed_line.groups()[0] == 'TITLE':
                        self.title = parsed_line.groups()[1]


        elif self.is_ssc:
            lineparse = r'#(.*):(.*);'
            in_data = False
            delta = 5
            for line in range(len(self.raw_data)):
                if re.match(lineparse, self.raw_data[line]):
                    parsed_line = re.match(lineparse, self.raw_data[line]).groups()
                else:
                    continue
                if parsed_line[0] == 'NOTEDATA':
                    in_data = True
                elif parsed_line[0] == 'STEPSTYPE' and parsed_line[1] != 'dance-single':
                    in_data = False
                elif parsed_line[0] == 'DIFFICULTY' and in_data:
                    diff = diff_names.index(parsed_line[1].lower())
                elif parsed_line[0] == 'METER' and in_data:
                    self.diffs[diff] = int(parsed_line[1]) * 10 + delta
                    in_data = False
                    delta = 5
                elif ecfa == True and parsed_line[0] == 'CHARTSTYLE' and parsed_line[1]:
                    ecfa_regex = r'speed=(\d+),stamina=(\d+),tech=(\d+),movement=(\d+),timing=(\d+),gimmick=(.*)'
                    m = re.match(ecfa_regex, parsed_line[1]).groups()
                    sp, st, te, mo, ti, g = [int(i) for i in m[:5]] + [m[5]]
                    g = ['none', 'light', 'medium', 'heavy', 'cmod'].index(g)
                    g %= 4
                    delta = 2*(sp + st + te + mo + ti + 3*g) // 5 - 7
                elif parsed_line[0] == 'TITLE':
                    self.title = parsed_line[1]


    def get_scores(self):

        data = None
        for song in song_scores:
            if song.get('Dir') in self.path.replace('\\', '/'):
                data = song

        for song in song_scores_waterfall:
            if song.get('Dir') in self.path.replace('\\', '/'):
                data = song

        if data is None:
            return -1

        for diff in data:
            diff_name = diff.get('Difficulty')
            diff_level = diff_names.index(diff_name.lower())

            high_score_list = []
            for k in diff:
                if k.tag == 'HighScoreList':
                    high_score_list = k

            score = None
            for k in high_score_list:
                if k.tag == 'HighScore':
                    score = k

                if score is None:
                    continue

                self.scores.append(Score(score, self.hash, diff_level))

class Course:
    def __init__(self, path):

        self.path = path
        with open(self.path, 'rb') as f:
            h = hashlib.md5()
            h.update(f.read())
            self.hash = h.hexdigest()

        self.bad = False
        self.scores = []

        if self.get_scores() == -1:
            self.bad = True

        self.title = None
        self.songs = []

        with open(self.path, 'r', encoding='utf-8') as f:
            self.raw_data = [a.rstrip() for a in f.readlines()]
        with open(self.path, 'rb') as f:
            h = hashlib.md5()
            h.update(f.read())
            self.hash = h.hexdigest()


        lineparse = r'#(.*?):(.*?)(?::(.*?))?;'
        in_data = False
        for line in range(len(self.raw_data)):
            if re.match(lineparse, self.raw_data[line]):
                parsed_line = re.match(lineparse, self.raw_data[line]).groups()
            else:
                continue
            if parsed_line[0] == 'COURSE':
                self.title = parsed_line[1]
            elif parsed_line[0] == 'METER':
                self.level = int(parsed_line[2])
            elif parsed_line[0] == 'SONG':
                self.songs.append(Song(glob.glob(game_dir + '/Songs/' + parsed_line[1] + '/*.s*')[0]).title)
                if '*' in parsed_line[1]:
                    self.bad = True


    def get_scores(self):

        data = None
        for course in course_scores:
            if course.get('Path') in self.path.replace('\\', '/'):
                for trail in course:
                    if trail.get('CourseDifficulty') == 'Medium':
                        data = trail
                    break

        for course in course_scores_waterfall:
            if course.get('Path') in self.path.replace('\\', '/'):
                for trail in course:
                    if trail.get('CourseDifficulty') == 'Medium':
                        data = trail
                break

        #if data is None:
        #    return -1

        high_score_list = []
        for k in data:
            if k.tag == 'HighScoreList':
                high_score_list = k

        score = None
        for k in high_score_list:
            if k.tag == 'HighScore':
                score = k

            if score is None:
                continue

            self.scores.append(Score(score, self.hash, None))


class Score:
    def __init__(self, score, hash, diff):
        self.hash = hash
        self.diff = diff
        self.note_data = {}
        for metric in score:
            tag = metric.tag
            if tag == 'TapNoteScores':
                tap_note = metric
            elif tag == 'HoldNoteScores':
                hold_note = metric
            elif tag == 'PercentDP':
                self.percent = float(metric.text)
            elif tag == 'MaxCombo':
                self.combo = int(metric.text)
            elif tag == 'Grade':
                self.grade = metric.text
            elif tag == 'DateTime':
                self.datetime = datetime.datetime.fromisoformat(metric.text)

        for metric in tap_note:
            tag = metric.tag
            if metric.tag == 'W1':
                self.note_data['fantastic'] = int(metric.text)
            if metric.tag == 'W2':
                self.note_data['excellent'] = int(metric.text)
            if metric.tag == 'W3':
                self.note_data['great'] = int(metric.text)
            if metric.tag == 'W4':
                self.note_data['decent'] = int(metric.text)
            if metric.tag == 'W5':
                self.note_data['way_off'] = int(metric.text)
            if metric.tag == 'Miss':
                self.note_data['miss'] = int(metric.text)
            if metric.tag == 'HitMine':
                self.note_data['mine'] = int(metric.text)

        for metric in hold_note:
            if metric.tag == 'Held':
                self.note_data['held'] = int(metric.text)

        self.status = 'Pass'
        if self.grade != 'Failed':
            if self.note_data['miss'] == self.note_data['way_off'] == self.note_data['decent'] == self.note_data['great'] == 0:
                self.status = 'FC'
                if self.note_data['great'] == 0:
                    self.status = 'FEC'
                    if self.note_data['excellent'] == 0:
                        self.status = 'MAX'
        else:
            self.status = 'Fail'


    def as_dict(self):
        return dict({'hash': self.hash, 'status': self.status, 'grade': self.grade, 'diff': self.diff, 'percent': self.percent, 'timestamp': self.datetime}, **self.note_data)

def ptt_ecfa(level, score):
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


def all_ecfa():
    zeta = glob.glob(game_dir+'/Songs/ECFA*/*/*.sm') + glob.glob(game_dir+'/Songs/ECFA*/*/*.ssc')
    songs = []
    scores = []
    p1 = []
    for i in zeta:
        s = Song(i, True)
        if s.bad:
            continue
        for i in s.scores:
            p1.append({'Title': s.title,
                       'Difficulty': diff_names[i.diff],
                       'Level': s.diffs[i.diff]/10,
                       'Percent': round(i.percent * 100, 2),
                       'Potential': ptt_ecfa(s.diffs[i.diff]/10, i.percent),
                       'Timestamp': i.datetime})

    p1 = pd.DataFrame(p1)
    p2 = p1.sort_values(by='Timestamp')[::-1]
    p2 = p2.head(30)
    p2 = p2.sort_values(by='Potential')[::-1]
    p1 = p1.sort_values(by='Potential')[::-1]
    p2 = p2.head(10)
    p1 = p1.head(30)
    return p1, p2 # Top 50, top 20 of recent 50

def all_courses():
    zeta = glob.glob(game_dir+'/Courses/*/*.crs')
    courses = []
    scores = []
    p1 = []
    for i in zeta:
        s = Course(i)
        if s.bad:
            # continue
            pass
        for i in s.scores:
            p1.append({'Title': s.title,
                       'Songs': Markup('<br>'.join(s.songs)),
                       'Percent': round(i.percent * 100, 2),
                       'Timestamp': i.datetime})
        return pd.DataFrame(p1)

def ovr_ecfa(data, rec):
    v = data['Potential'][:50]
    w = rec['Potential'][:20]
    return round(np.mean(v)*0.8 + np.mean(w)*0.2  * (1/70) * (len(v) + len(w)), 2)

def name():
    return username
