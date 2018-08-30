
"""
Cmd-line interface to *sweep* the system, running tasks!
"""

import os
from datetime import datetime

from raven import Client

from sweeps.models import AbstractTask

sentry = Client()


def _get_subclasses():
    # This lib doesn't know about subclasses unless they're loaded
    # use this env var to find them.
    task_classes = os.environ.get('SWEEP_TASK_LIBS', None)
    if task_classes:
        for tc in task_classes.split(':'):
            __import__(tc)


def sweep(asof=None, _verbose=True):
    try:
        _get_subclasses()
        if not asof:
            asof = datetime.utcnow()
        for task_class in AbstractTask.__subclasses__():
            for task in task_class.query.filter(task_class.status=='ACTIVE'):
                task.sweep(asof, _verbose=_verbose)
    except Exception:
        sentry.captureException()
        raise


if __name__ == '__main__':
    sweep()
