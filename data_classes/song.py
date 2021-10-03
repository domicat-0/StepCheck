import re, hashlib, glob
from data_classes import basis
from data_classes.score import Score

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
                    diff = basis.diff_names.index((re.match(notesparse, self.raw_data[line+3]).groups()[0]).lower())
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
                    diff = basis.diff_names.index(parsed_line[1].lower())
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
                    delta = 2*(sp + 0.6*st + te + mo + ti + 3*g) // 5 - 6
                elif parsed_line[0] == 'TITLE':
                    self.title = parsed_line[1]


    def get_scores(self):

        data = None
        for song in basis.song_scores:
            if song.get('Dir') in self.path.replace('\\', '/'):
                data = song

        for song in basis.song_scores_waterfall:
            if song.get('Dir') in self.path.replace('\\', '/'):
                data = song

        if data is None:
            return -1

        for diff in data:
            diff_name = diff.get('Difficulty')
            diff_level = basis.diff_names.index(diff_name.lower())

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