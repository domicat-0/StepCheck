import re, hashlib, glob
from data_classes import basis
from data_classes.score import Score
from data_classes.song import Song

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
                self.songs.append(Song(glob.glob(basis.game_dir + '/Songs/' + parsed_line[1] + '/*.s*')[0]).title)
                if '*' in parsed_line[1]:
                    self.bad = True


    def get_scores(self):

        data = None
        for course in basis.course_scores:
            if course.get('Path') in self.path.replace('\\', '/'):
                for trail in course:
                    if trail.get('CourseDifficulty') == 'Medium':
                        data = trail
                    break

        for course in basis.course_scores_waterfall:
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