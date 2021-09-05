import configparser, lxml
from lxml import etree

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