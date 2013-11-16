

from .models import AbstractTask

class SurveyConfig(object):
    def __init__(self, name, subject, delay_days):
        self.name = name
        self.subject = subject
        self.delay_days = delay_days

    @property
    def template(self):
        return 'survey-%s' % self.name

class SendEdSurvey(AbstractTask, db.Model):
    __tablename__ = 'ed_metrics_survey'

    SURVEY_PERIODS = {
        "WEEK-1" : SurveyConfig("WEEK-1", "Checking In", 7),
        "WEEK-2" : SurveyConfig("WEEK-2", "How's Your Thinkful Course Going?", 7),
    }

    def _get_survey_period(self):
        return EdMetricsSurvey.SURVEY_PERIODS[self.name]

    def get_instances(self, asof):
        period = self._get_survey_period()
        start_date = asof - period.delay_days
        pots = Potential.query.filter(Potential.close_date==start_date)
        for pot in pots:
            if pot.stage() == 'Current student':
                yield pot

    def run(self, pot):
        sp = self._get_survey_period()
        body = render_template(sp.template)

        recipient = pot.contact.email

        print recipient, '-->', sp.subject


def setup():
    ses1 = SendEdSurvey(name='WEEK-1')
    db.session.add(ses1)
    db.session.commit()

if __name__ == '__main__':
    setup()
