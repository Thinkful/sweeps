

"""
Example sweeps implementation that sends surveys 
(well, prints out that a someone should receive a survey).
"""

from optparse import OptionParser
from sweeps.models import AbstractTask
from sweeps.sweep import sweep
from main import db

class SurveyRecipient(db.Model):
    __tablename__ = 'sweeps_example_recipient'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))

    def __repr__(self):
        return self.email

class SendSurvey(AbstractTask, db.Model):
    __tablename__ = 'sweeps_example_survey'

    def get_instances(self, asof):
        for pot in SurveyRecipient.query.all():
            yield pot

    def run(self, recipient):
        print '  %s gets a %s survey!' % (recipient, self.name)

def setup():
    # Set up the Task to run
    for name in ['week1', 'week2', 'week3']:
        survey = SendSurvey(name=name)
        db.session.add(survey)
    
    # Create the instances to run once for each task
    for recip in ['recipient@one.com', 'recipient@two.com']:
        sr = SurveyRecipient(email=recip)
        db.session.add(sr)

    db.session.commit()

if __name__ == '__main__':
    parser = OptionParser("%prog")
    parser.add_option("--setup", action="store_true", help="setup the db")
    (options, args) = parser.parse_args()

    if options.setup:
        db.create_all()
        setup()

