

"""
Very simple way to run arbitrary tasks that need to be audited and retriable.
"""

from datetime import datetime

class TaskStatus(db.Model):
    """A single run of a single task on a single object.
    
    Conceptually, though not enforced, a task's run status 
    is immutable once the task has completed.
    """
    id
    task_table
    task_id
    instance_table
    instance_id
    ended
    status

    @staticmethod
    def new(self, task, instance):
        return TaskStatus(
            task_table=task.__tablename__,
            task_id=task.id,
            instance_table=instance.__tablename__,
            instance_id=instance.id,
            started=datetime.utcnow)

    def set_status(self, status, ended=None):
        tr.status = status
        if ended:
            tf.ended = ended
        db.session.add(tr)
        db.session.commit()

    @staticmethod
    def start(self, task, instance):
        tr = TaskStatus.new(task, instance)
        tr.set_status('RUNNING')
        return tr

    def successful(self):
        tr.set_status('SUCCESS', datetime.utcnow)

    def failed(self):
        tr.set_status('FAIL', datetime.utcnow)


class AbstractTask(object):
    """The interface for a task.
    Must be subclassed, see skeleten funcs below.
    """
    id
    name

    def allowed_to_run(self, instance):
        # TODO Note we don't protect against race conditions
        return TaskStatus.query \
            .filter(instance_table==instance.__tablename__) \
            .filter(instance_id==instance.id) \
            .filter(status==['SUCCESS', 'RUNNING']).count() == 0

    def _run_one(self, instance):
        try:
            tr = TaskStatus.start(self, instance)
            self.run(pot)
            tr.successful()
            print "Success", pot
        except Exception, e:
            tr.failed()
            print "Failed", pot, e

    def run_all(self, asof):
        for instance in self.get_instances(asof):
            if self.allowed_to_run(instance):
                print "Running", instance
                self._run_one(instance)
            else:
                print "Not running", instance

    def get_instances(self, asof):
        raise Exception("Incomplete subclass!")

    def run(self, instance):
        raise Exception("Incomplete subclass!")


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

def main():
    asof = datetime.utcnow()
    for task in AbstractTask.__subclasses__():
        task.run_all(asof)

if __name__ == '__main__':
    main()
