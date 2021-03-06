
"""
Base models for tasks and statuses
"""

import traceback
from datetime import datetime
from main import db, app, TFBase
import model_meta


class TaskStatus(TFBase, db.Model):
    """A single run of a single task on a single object.

    Conceptually, though not enforced, a task's run status
    is immutable once the task has completed.
    """
    __tablename__ = 'sweeps_statuses'
    id = db.Column(db.Integer, primary_key=True)
    task_table = db.Column(db.String(50), nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    instance_table = db.Column(db.String(50), nullable=False)
    instance_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    started = db.Column(db.DateTime)
    ended = db.Column(db.DateTime)

    @staticmethod
    def new(task, instance):
        return TaskStatus(
            task_table=task.__tablename__,
            task_id=task.id,
            instance_table=instance.__tablename__,
            instance_id=instance.id,
            started=datetime.utcnow())

    def set_status(self, status, ended=None):
        self.status = status
        if ended:
            self.ended = ended
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def start(task, instance):
        tr = TaskStatus.new(task, instance)
        tr.set_status('RUNNING')
        return tr

    def successful(self):
        self.set_status('SUCCESS', datetime.utcnow())

    def failed(self):
        self.set_status('FAILED', datetime.utcnow())


class AbstractTask(object):
    """The interface for a task.
    Must be subclassed, see skeleten funcs below.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_asof = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.Enum("ACTIVE", "RETIRED", name='sweeps_task_status_types'))

    def allowed_to_run(self, instance):
        # TODO Note we don't protect against race conditions
        return TaskStatus.query \
            .filter(TaskStatus.task_table == self.__tablename__) \
            .filter(TaskStatus.task_id == self.id) \
            .filter(TaskStatus.instance_table == instance.__tablename__) \
            .filter(TaskStatus.instance_id == instance.id) \
            .filter(TaskStatus.status.in_(['SUCCESS', 'RUNNING'])).count() == 0

    def _run_one(self, instance):
        tr = TaskStatus.start(self, instance)
        try:
            self.run(instance)
            tr.successful()
        except Exception, e:
            tr.failed()
            print traceback.format_exc()

    def sweep(self, asof, _verbose=True):
        # Prevent a DetachedInstanceError
        db.session.add(self)

        if _verbose:
            print "Sweeping %s %s asof %s" % (
                self.__class__.__name__, self.name, asof)
        num_swept = 0
        with app.test_request_context():
            for instance in self.get_instances(asof):
                if self.allowed_to_run(instance):
                    self._run_one(instance)
                    num_swept += 1
        if _verbose:
            print "Swept %s." % (num_swept)

    def get_instances(self, asof):
        raise Exception("Incomplete subclass!")

    def run(self, instance):
        raise Exception("Incomplete subclass!")

# SQLAlchemy relationships can be made here if they are to classes
# outside this module.
# mkrelationships will be called after all the modules listed in
# model_meta.all_modules have been imported

def mkrelationships():
    pass


model_meta.init_module('sweeps.models', mkrelationships)
