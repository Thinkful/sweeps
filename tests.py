

import sys, os, unittest
from main import db
from sweeps.models import AbstractTask, TaskStatus
from sweeps.example import setup
from sweeps.sweep import sweep

class TestSweeps(unittest.TestCase):

	def setUp(self):
		db.drop_all()
		db.create_all()
		setup()

	def tearDown(self):
		db.drop_all()

	def assertSweep(self, starting_count=0):
		ae = self.assertEquals
		ae(TaskStatus.query.count(), starting_count)
		sweep()
		ae(TaskStatus.query.count(), 6)
		ae(TaskStatus.query.filter(TaskStatus.status=='SUCCESS').count(), 6)

	def test_run_task(self):
		self.assertSweep()

	def test_task_runs_only_once(self):
		self.assertSweep()
		self.assertSweep(starting_count=6)

if __name__ == '__main__':
    loader = unittest.TestLoader()
    if len(sys.argv) > 1:
        print "Only running these unit tests: ", sys.argv[1:]
        tests = loader.loadTestsFromNames(sys.argv[1:])
    else:
        print "Running all unit tests!"
        tests = loader.discover('.')
    testRunner = unittest.runner.TextTestRunner()
    result = testRunner.run(tests) 
    if result.wasSuccessful() == False: 
        exit(1)
