# Copyright (c) 2005-2007 Twisted Matrix Laboratories.
# See LICENSE for details.
#
# Maintainer: Jonathan Lange <jml@twistedmatrix.com>
# Author: Robert Collins <robertc@robertcollins.net>


import StringIO
from zope.interface import implements

from twisted.trial.itrial import IReporter, ITestCase
from twisted.trial import unittest, runner, reporter, util
from twisted.python import failure, log, reflect
from twisted.scripts import trial
from twisted.plugins import twisted_trial
from twisted import plugin
from twisted.internet import defer


pyunit = __import__('unittest')


class CapturingDebugger(object):

    def __init__(self):
        self._calls = []

    def runcall(self, *args, **kwargs):
        self._calls.append('runcall')
        args[0](*args[1:], **kwargs)



class CapturingReporter(object):
    """
    Reporter that keeps a log of all actions performed on it.
    """

    implements(IReporter)

    stream = None
    tbformat = None
    args = None
    separator = None
    testsRun = None

    def __init__(self, *a, **kw):
        """
        Create a capturing reporter.
        """
        self._calls = []
        self.shouldStop = False


    def startTest(self, method):
        """
        Report the beginning of a run of a single test method
        @param method: an object that is adaptable to ITestMethod
        """
        self._calls.append('startTest')


    def stopTest(self, method):
        """
        Report the status of a single test method
        @param method: an object that is adaptable to ITestMethod
        """
        self._calls.append('stopTest')


    def cleanupErrors(self, errs):
        """called when the reactor has been left in a 'dirty' state
        @param errs: a list of L{twisted.python.failure.Failure}s
        """
        self._calls.append('cleanupError')


    def addSuccess(self, test):
        self._calls.append('addSuccess')


    def done(self):
        """
        Do nothing. These tests don't care about done.
        """



class TestTrialRunner(unittest.TestCase):

    def setUp(self):
        self.stream = StringIO.StringIO()
        self.runner = runner.TrialRunner(CapturingReporter, stream=self.stream)
        self.test = TestTrialRunner('test_empty')

    def test_empty(self):
        """
        Empty test method, used by the other tests.
        """

    def tearDown(self):
        self.runner._tearDownLogFile()

    def _getObservers(self):
        return log.theLogPublisher.observers

    def test_addObservers(self):
        """
        Tests that the runner add logging observers during the run.
        """
        originalCount = len(self._getObservers())
        self.runner.run(self.test)
        newCount = len(self._getObservers())
        self.failUnlessEqual(originalCount + 1, newCount)

    def test_addObservers_repeat(self):
        self.runner.run(self.test)
        count = len(self._getObservers())
        self.runner.run(self.test)
        newCount = len(self._getObservers())
        self.failUnlessEqual(count, newCount)

    def test_logFileAlwaysActive(self):
        """
        Test that a new file is opened on each run.
        """
        oldSetUpLogging = self.runner._setUpLogging
        l = []
        def setUpLogging():
            oldSetUpLogging()
            l.append(self.runner._logFileObserver)
        self.runner._setUpLogging = setUpLogging
        self.runner.run(self.test)
        self.runner.run(self.test)
        self.failUnlessEqual(len(l), 2)
        self.failIf(l[0] is l[1], "Should have created a new file observer")

    def test_logFileGetsClosed(self):
        """
        Test that file created is closed during the run.
        """
        oldSetUpLogging = self.runner._setUpLogging
        l = []
        def setUpLogging():
            oldSetUpLogging()
            l.append(self.runner._logFileObject)
        self.runner._setUpLogging = setUpLogging
        self.runner.run(self.test)
        self.failUnlessEqual(len(l), 1)
        self.failUnless(l[0].closed)



class TrialRunnerWithUncleanWarningsReporter(TestTrialRunner):
    """
    Tests for the TrialRunner's interaction with an unclean-error suppressing
    reporter.
    """

    def setUp(self):
        self.stream = StringIO.StringIO()
        self.runner = runner.TrialRunner(CapturingReporter, stream=self.stream,
                                         uncleanWarnings=True)
        self.test = TestTrialRunner('test_empty')



class DryRunMixin(object):

    suppress = [util.suppress(
        category=DeprecationWarning,
        message="Test visitors deprecated in Twisted 8.0")]


    def setUp(self):
        self.log = []
        self.stream = StringIO.StringIO()
        self.runner = runner.TrialRunner(CapturingReporter,
                                         runner.TrialRunner.DRY_RUN,
                                         stream=self.stream)
        self.makeTestFixtures()


    def makeTestFixtures(self):
        """
        Set C{self.test} and C{self.suite}, where C{self.suite} is an empty
        TestSuite.
        """


    def test_empty(self):
        """
        If there are no tests, the reporter should not receive any events to
        report.
        """
        result = self.runner.run(runner.TestSuite())
        self.assertEqual(result._calls, [])


    def test_singleCaseReporting(self):
        """
        If we are running a single test, check the reporter starts, passes and
        then stops the test during a dry run.
        """
        result = self.runner.run(self.test)
        self.assertEqual(result._calls, ['startTest', 'addSuccess', 'stopTest'])


    def test_testsNotRun(self):
        """
        When we are doing a dry run, the tests should not actually be run.
        """
        self.runner.run(self.test)
        self.assertEqual(self.log, [])



class DryRunTest(DryRunMixin, unittest.TestCase):
    """
    Check that 'dry run' mode works well with Trial tests.
    """
    def makeTestFixtures(self):
        class MockTest(unittest.TestCase):
            def test_foo(test):
                self.log.append('test_foo')
        self.test = MockTest('test_foo')
        self.suite = runner.TestSuite()



class PyUnitDryRunTest(DryRunMixin, unittest.TestCase):
    """
    Check that 'dry run' mode works well with stdlib unittest tests.
    """
    def makeTestFixtures(self):
        class PyunitCase(pyunit.TestCase):
            def test_foo(self):
                pass
        self.test = PyunitCase('test_foo')
        self.suite = pyunit.TestSuite()



class TestRunner(unittest.TestCase):
    def setUp(self):
        self.config = trial.Options()
        # whitebox hack a reporter in, because plugins are CACHED and will
        # only reload if the FILE gets changed.

        parts = reflect.qual(CapturingReporter).split('.')
        package = '.'.join(parts[:-1])
        klass = parts[-1]
        plugins = [twisted_trial._Reporter(
            "Test Helper Reporter",
            package,
            description="Utility for unit testing.",
            longOpt="capturing",
            shortOpt=None,
            klass=klass)]


        # XXX There should really be a general way to hook the plugin system
        # for tests.
        def getPlugins(iface, *a, **kw):
            self.assertEqual(iface, IReporter)
            return plugins + list(self.original(iface, *a, **kw))

        self.original = plugin.getPlugins
        plugin.getPlugins = getPlugins

        self.standardReport = ['startTest', 'addSuccess', 'stopTest',
                               'startTest', 'addSuccess', 'stopTest',
                               'startTest', 'addSuccess', 'stopTest',
                               'startTest', 'addSuccess', 'stopTest',
                               'startTest', 'addSuccess', 'stopTest',
                               'startTest', 'addSuccess', 'stopTest',
                               'startTest', 'addSuccess', 'stopTest']


    def tearDown(self):
        plugin.getPlugins = self.original


    def parseOptions(self, args):
        self.config.parseOptions(args)


    def getRunner(self):
        r = trial._makeRunner(self.config)
        r.stream = StringIO.StringIO()
        self.addCleanup(r._tearDownLogFile)
        return r


    def test_runner_can_get_reporter(self):
        self.parseOptions([])
        result = self.config['reporter']
        my_runner = self.getRunner()
        try:
            self.assertEqual(result, my_runner._makeResult().__class__)
        finally:
            my_runner._tearDownLogFile()


    def test_runner_get_result(self):
        self.parseOptions([])
        my_runner = self.getRunner()
        result = my_runner._makeResult()
        self.assertEqual(result.__class__, self.config['reporter'])


    def test_uncleanWarningsOffByDefault(self):
        """
        By default Trial sets the 'uncleanWarnings' option on the runner to
        False. This means that dirty reactor errors will be reported as
        errors. See L{test_reporter.TestDirtyReactor}.
        """
        self.parseOptions([])
        runner = self.getRunner()
        self.assertNotIsInstance(runner._makeResult(),
                                 reporter.UncleanWarningsReporterWrapper)


    def test_getsUncleanWarnings(self):
        """
        Specifying '--unclean-warnings' on the trial command line will cause
        reporters to be wrapped in a device which converts unclean errors to
        warnings.  See L{test_reporter.TestDirtyReactor} for implications.
        """
        self.parseOptions(['--unclean-warnings'])
        runner = self.getRunner()
        self.assertIsInstance(runner._makeResult(),
                              reporter.UncleanWarningsReporterWrapper)


    def test_runner_working_directory(self):
        self.parseOptions(['--temp-directory', 'some_path'])
        runner = self.getRunner()
        try:
            self.assertEquals(runner.workingDirectory, 'some_path')
        finally:
            runner._tearDownLogFile()


    def test_runner_normal(self):
        self.parseOptions(['--temp-directory', self.mktemp(),
                           '--reporter', 'capturing',
                           'twisted.trial.test.sample'])
        my_runner = self.getRunner()
        loader = runner.TestLoader()
        suite = loader.loadByName('twisted.trial.test.sample', True)
        result = my_runner.run(suite)
        self.assertEqual(self.standardReport, result._calls)


    def test_runner_debug(self):
        self.parseOptions(['--reporter', 'capturing',
                           '--debug', 'twisted.trial.test.sample'])
        my_runner = self.getRunner()
        debugger = CapturingDebugger()
        def get_debugger():
            return debugger
        my_runner._getDebugger = get_debugger
        loader = runner.TestLoader()
        suite = loader.loadByName('twisted.trial.test.sample', True)
        result = my_runner.run(suite)
        self.assertEqual(self.standardReport, result._calls)
        self.assertEqual(['runcall'], debugger._calls)



class TestTrialSuite(unittest.TestCase):

    def test_imports(self):
        # FIXME, HTF do you test the reactor can be cleaned up ?!!!
        from twisted.trial.runner import TrialSuite
        # silence pyflakes warning
        silencePyflakes = TrialSuite



class TestUntilFailure(unittest.TestCase):
    class FailAfter(unittest.TestCase):
        """
        A test  case that fails when run 3 times in a row.
        """
        count = []
        def test_foo(self):
            self.count.append(None)
            if len(self.count) == 3:
                self.fail('Count reached 3')

    def setUp(self):
        TestUntilFailure.FailAfter.count = []
        self.test = TestUntilFailure.FailAfter('test_foo')
        self.stream = StringIO.StringIO()
        self.runner = runner.TrialRunner(reporter.Reporter, stream=self.stream)

    def test_runUntilFailure(self):
        """
        Test that the runUntilFailure method of the runner actually fail after
        a few runs.
        """
        result = self.runner.runUntilFailure(self.test)
        self.failUnlessEqual(result.testsRun, 1)
        self.failIf(result.wasSuccessful())
        self.assertEquals(self._getFailures(result), 1)

    def _getFailures(self, result):
        """
        Get the number of failures that were reported to a result.
        """
        return len(result.failures)



class UncleanUntilFailureTests(TestUntilFailure):
    """
    Test that the run-until-failure feature works correctly with the unclean
    error suppressor.
    """

    def setUp(self):
        TestUntilFailure.setUp(self)
        self.runner = runner.TrialRunner(reporter.Reporter, stream=self.stream,
                                         uncleanWarnings=True)

    def _getFailures(self, result):
        """
        Get the number of failures that were reported to a result that
        is wrapped in an UncleanFailureWrapper.
        """
        return len(result._originalReporter.failures)



class BreakingSuite(runner.TestSuite):
    """
    A L{TestSuite} that logs an error when it is run.
    """

    def run(self, result):
        try:
            raise RuntimeError("error that occurs outside of a test")
        except RuntimeError, e:
            log.err(failure.Failure())



class TestLoggedErrors(unittest.TestCase):
    """
    It is possible for an error generated by a test to be logged I{outside} of
    any test. The log observers constructed by L{TestCase} won't catch these
    errors. Here we try to generate such errors and ensure they are reported to
    a L{TestResult} object.
    """

    def tearDown(self):
        self.flushLoggedErrors(RuntimeError)


    def test_construct(self):
        """
        Check that we can construct a L{runner.LoggedSuite} and that it
        starts empty.
        """
        suite = runner.LoggedSuite()
        self.assertEqual(suite.countTestCases(), 0)


    def test_capturesError(self):
        """
        Chek that a L{LoggedSuite} reports any logged errors to its result.
        """
        result = reporter.TestResult()
        suite = runner.LoggedSuite([BreakingSuite()])
        suite.run(result)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0][0].id(), runner.NOT_IN_TEST)
        self.failUnless(result.errors[0][1].check(RuntimeError))



class TestTestHolder(unittest.TestCase):

    def setUp(self):
        self.description = "description"
        self.holder = runner.TestHolder(self.description)


    def test_holder(self):
        """
        Check that L{runner.TestHolder} takes a description as a parameter
        and that this description is returned by the C{id} and
        C{shortDescription} methods.
        """
        self.assertEqual(self.holder.id(), self.description)
        self.assertEqual(self.holder.shortDescription(), self.description)


    def test_holderImplementsITestCase(self):
        """
        L{runner.TestHolder} implements L{ITestCase}.
        """
        self.assertIdentical(self.holder, ITestCase(self.holder))



class TestErrorHolder(TestTestHolder):
    """
    Test L{runner.ErrorHolder} shares behaviour with L{runner.TestHolder}.
    """

    def setUp(self):
        self.description = "description"
        # make a real Failure so we can construct ErrorHolder()
        try:
            1/0
        except ZeroDivisionError:
            error = failure.Failure()
        self.holder = runner.ErrorHolder(self.description, error)



class TestMalformedMethod(unittest.TestCase):
    """
    Test that trial manages when test methods don't have correct signatures.
    """
    class ContainMalformed(unittest.TestCase):
        """
        This TestCase holds malformed test methods that trial should handle.
        """
        def test_foo(self, blah):
            pass
        def test_bar():
            pass
        test_spam = defer.deferredGenerator(test_bar)

    def _test(self, method):
        """
        Wrapper for one of the test method of L{ContainMalformed}.
        """
        stream = StringIO.StringIO()
        trialRunner = runner.TrialRunner(reporter.Reporter, stream=stream)
        test = TestMalformedMethod.ContainMalformed(method)
        result = trialRunner.run(test)
        self.failUnlessEqual(result.testsRun, 1)
        self.failIf(result.wasSuccessful())
        self.failUnlessEqual(len(result.errors), 1)

    def test_extraArg(self):
        """
        Test when the method has extra (useless) arguments.
        """
        self._test('test_foo')

    def test_noArg(self):
        """
        Test when the method doesn't have even self as argument.
        """
        self._test('test_bar')

    def test_decorated(self):
        """
        Test a decorated method also fails.
        """
        self._test('test_spam')



class DestructiveTestSuiteTestCase(unittest.TestCase):
    """
    Test for L{runner.DestructiveTestSuite}.
    """

    def test_basic(self):
        """
        Thes destructive test suite should run the tests normally.
        """
        called = []
        class MockTest(unittest.TestCase):
            def test_foo(test):
                called.append(True)
        test = MockTest('test_foo')
        result = reporter.TestResult()
        suite = runner.DestructiveTestSuite([test])
        self.assertEquals(called, [])
        suite.run(result)
        self.assertEquals(called, [True])
        self.assertEquals(suite.countTestCases(), 0)


    def test_shouldStop(self):
        """
        Test the C{shouldStop} management: raising a C{KeyboardInterrupt} must
        interrupt the suite.
        """
        called = []
        class MockTest(unittest.TestCase):
            def test_foo1(test):
                called.append(1)
            def test_foo2(test):
                raise KeyboardInterrupt()
            def test_foo3(test):
                called.append(2)
        result = reporter.TestResult()
        loader = runner.TestLoader()
        loader.suiteFactory = runner.DestructiveTestSuite
        suite = loader.loadClass(MockTest)
        self.assertEquals(called, [])
        suite.run(result)
        self.assertEquals(called, [1])
        # The last test shouldn't have been run
        self.assertEquals(suite.countTestCases(), 1)


    def test_cleanup(self):
        """
        Checks that the test suite cleanups its tests during the run, so that
        it ends empty.
        """
        class MockTest(unittest.TestCase):
            def test_foo(test):
                pass
        test = MockTest('test_foo')
        result = reporter.TestResult()
        suite = runner.DestructiveTestSuite([test])
        self.assertEquals(suite.countTestCases(), 1)
        suite.run(result)
        self.assertEquals(suite.countTestCases(), 0)



class TestRunnerDeprecation(unittest.TestCase):

    class FakeReporter(reporter.Reporter):
        """
        Fake reporter that does *not* implement done() but *does* implement
        printErrors, separator, printSummary, stream, write and writeln
        without deprecations.
        """

        done = None
        separator = None
        stream = None

        def printErrors(self, *args):
            pass

        def printSummary(self, *args):
            pass

        def write(self, *args):
            pass

        def writeln(self, *args):
            pass


    def test_reporterDeprecations(self):
        """
        The runner emits a warning if it is using a result that doesn't
        implement 'done'.
        """
        trialRunner = runner.TrialRunner(None)
        result = self.FakeReporter()
        trialRunner._makeResult = lambda: result
        def f():
            # We have to use a pyunit test, otherwise we'll get deprecation
            # warnings about using iterate() in a test.
            trialRunner.run(pyunit.TestCase('id'))
        self.assertWarns(
            DeprecationWarning,
            "%s should implement done() but doesn't. Falling back to "
            "printErrors() and friends." % reflect.qual(result.__class__),
            __file__, f)
