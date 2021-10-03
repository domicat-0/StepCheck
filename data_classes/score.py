import datetime

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
            if self.note_data['miss'] == self.note_data['way_off'] == self.note_data['decent'] == 0:
                self.status = 'FC'
                if self.note_data['great'] == 0:
                    self.status = 'FEC'
                    if self.note_data['excellent'] == 0:
                        self.status = 'MAX'
        else:
            self.status = 'Fail'


    def as_dict(self):
        return dict({'hash': self.hash, 'status': self.status, 'grade': self.grade, 'diff': self.diff, 'percent': self.percent, 'timestamp': self.datetime}, **self.note_data)