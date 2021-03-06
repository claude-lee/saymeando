# Copyright (c) 2001-2008 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.words.protocols.jabber.xmlstream}.
"""

from twisted.trial import unittest

from zope.interface.verify import verifyObject

from twisted.internet import defer, task
from twisted.internet.error import ConnectionLost
from twisted.test import proto_helpers
from twisted.words.xish import domish
from twisted.words.protocols.jabber import error, ijabber, jid, xmlstream



NS_XMPP_TLS = 'urn:ietf:params:xml:ns:xmpp-tls'



class IQTest(unittest.TestCase):
    """
    Tests both IQ and the associated IIQResponseTracker callback.
    """

    def setUp(self):
        authenticator = xmlstream.ConnectAuthenticator('otherhost')
        authenticator.namespace = 'testns'
        self.xmlstream = xmlstream.XmlStream(authenticator)
        self.clock = task.Clock()
        self.xmlstream._callLater = self.clock.callLater
        self.xmlstream.makeConnection(proto_helpers.StringTransport())
        self.xmlstream.dataReceived(
           "<stream:stream xmlns:stream='http://etherx.jabber.org/streams' "
                          "xmlns='testns' from='otherhost' version='1.0'>")
        self.iq = xmlstream.IQ(self.xmlstream, 'get')


    def testBasic(self):
        self.assertEquals(self.iq['type'], 'get')
        self.assertTrue(self.iq['id'])


    def testSend(self):
        self.xmlstream.transport.clear()
        self.iq.send()
        self.assertEquals("<iq type='get' id='%s'/>" % self.iq['id'],
                          self.xmlstream.transport.value())


    def testResultResponse(self):
        def cb(result):
            self.assertEquals(result['type'], 'result')

        d = self.iq.send()
        d.addCallback(cb)

        xs = self.xmlstream
        xs.dataReceived("<iq type='result' id='%s'/>" % self.iq['id'])
        return d


    def testErrorResponse(self):
        d = self.iq.send()
        self.assertFailure(d, error.StanzaError)

        xs = self.xmlstream
        xs.dataReceived("<iq type='error' id='%s'/>" % self.iq['id'])
        return d


    def testNonTrackedResponse(self):
        """
        Test that untracked iq responses don't trigger any action.

        Untracked means that the id of the incoming response iq is not
        in the stream's C{iqDeferreds} dictionary.
        """
        xs = self.xmlstream
        xmlstream.upgradeWithIQResponseTracker(xs)

        # Make sure we aren't tracking any iq's.
        self.failIf(xs.iqDeferreds)

        # Set up a fallback handler that checks the stanza's handled attribute.
        # If that is set to True, the iq tracker claims to have handled the
        # response.
        def cb(iq):
            self.failIf(getattr(iq, 'handled', False))

        xs.addObserver("/iq", cb, -1)

        # Receive an untracked iq response
        xs.dataReceived("<iq type='result' id='test'/>")


    def testCleanup(self):
        """
        Test if the deferred associated with an iq request is removed
        from the list kept in the L{XmlStream} object after it has
        been fired.
        """

        d = self.iq.send()
        xs = self.xmlstream
        xs.dataReceived("<iq type='result' id='%s'/>" % self.iq['id'])
        self.assertNotIn(self.iq['id'], xs.iqDeferreds)
        return d


    def testDisconnectCleanup(self):
        """
        Test if deferreds for iq's that haven't yet received a response
        have their errback called on stream disconnect.
        """

        d = self.iq.send()
        xs = self.xmlstream
        xs.connectionLost("Closed by peer")
        self.assertFailure(d, ConnectionLost)
        return d


    def testNoModifyingDict(self):
        """
        Test to make sure the errbacks cannot cause the iteration of the
        iqDeferreds to blow up in our face.
        """

        def eb(failure):
            d = xmlstream.IQ(self.xmlstream).send()
            d.addErrback(eb)

        d = self.iq.send()
        d.addErrback(eb)
        self.xmlstream.connectionLost("Closed by peer")
        return d


    def testRequestTimingOut(self):
        """
        Test that an iq request with a defined timeout times out.
        """
        self.iq.timeout = 60
        d = self.iq.send()
        self.assertFailure(d, xmlstream.TimeoutError)

        self.clock.pump([1, 60])
        self.failIf(self.clock.calls)
        self.failIf(self.xmlstream.iqDeferreds)
        return d


    def testRequestNotTimingOut(self):
        """
        Test that an iq request with a defined timeout does not time out
        when a response was received before the timeout period elapsed.
        """
        self.iq.timeout = 60
        d = self.iq.send()
        self.clock.callLater(1, self.xmlstream.dataReceived,
                             "<iq type='result' id='%s'/>" % self.iq['id'])
        self.clock.pump([1, 1])
        self.failIf(self.clock.calls)
        return d


    def testDisconnectTimeoutCancellation(self):
        """
        Test if timeouts for iq's that haven't yet received a response
        are cancelled on stream disconnect.
        """

        self.iq.timeout = 60
        d = self.iq.send()

        xs = self.xmlstream
        xs.connectionLost("Closed by peer")
        self.assertFailure(d, ConnectionLost)
        self.failIf(self.clock.calls)
        return d



class XmlStreamTest(unittest.TestCase):

    def onStreamStart(self, obj):
        self.gotStreamStart = True


    def onStreamEnd(self, obj):
        self.gotStreamEnd = True


    def onStreamError(self, obj):
        self.gotStreamError = True


    def setUp(self):
        """
        Set up XmlStream and several observers.
        """
        self.gotStreamStart = False
        self.gotStreamEnd = False
        self.gotStreamError = False
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        xs.addObserver('//event/stream/start', self.onStreamStart)
        xs.addObserver('//event/stream/end', self.onStreamEnd)
        xs.addObserver('//event/stream/error', self.onStreamError)
        xs.makeConnection(proto_helpers.StringTransportWithDisconnection())
        xs.transport.protocol = xs
        xs.namespace = 'testns'
        xs.version = (1, 0)
        self.xmlstream = xs


    def test_sendHeaderBasic(self):
        """
        Basic test on the header sent by sendHeader.
        """
        xs = self.xmlstream
        xs.sendHeader()
        splitHeader = self.xmlstream.transport.value()[0:-1].split(' ')
        self.assertIn("<stream:stream", splitHeader)
        self.assertIn("xmlns:stream='http://etherx.jabber.org/streams'",
                      splitHeader)
        self.assertIn("xmlns='testns'", splitHeader)
        self.assertIn("version='1.0'", splitHeader)
        self.assertTrue(xs._headerSent)


    def test_sendHeaderAdditionalNamespaces(self):
        """
        Test for additional namespace declarations.
        """
        xs = self.xmlstream
        xs.prefixes['jabber:server:dialback'] = 'db'
        xs.sendHeader()
        splitHeader = self.xmlstream.transport.value()[0:-1].split(' ')
        self.assertIn("<stream:stream", splitHeader)
        self.assertIn("xmlns:stream='http://etherx.jabber.org/streams'",
                      splitHeader)
        self.assertIn("xmlns:db='jabber:server:dialback'", splitHeader)
        self.assertIn("xmlns='testns'", splitHeader)
        self.assertIn("version='1.0'", splitHeader)
        self.assertTrue(xs._headerSent)


    def test_sendHeaderInitiating(self):
        """
        Test addressing when initiating a stream.
        """
        xs = self.xmlstream
        xs.thisEntity = jid.JID('thisHost')
        xs.otherEntity = jid.JID('otherHost')
        xs.initiating = True
        xs.sendHeader()
        splitHeader = xs.transport.value()[0:-1].split(' ')
        self.assertIn("to='otherhost'", splitHeader)
        self.assertIn("from='thishost'", splitHeader)


    def test_sendHeaderReceiving(self):
        """
        Test addressing when receiving a stream.
        """
        xs = self.xmlstream
        xs.thisEntity = jid.JID('thisHost')
        xs.otherEntity = jid.JID('otherHost')
        xs.initiating = False
        xs.sid = 'session01'
        xs.sendHeader()
        splitHeader = xs.transport.value()[0:-1].split(' ')
        self.assertIn("to='otherhost'", splitHeader)
        self.assertIn("from='thishost'", splitHeader)
        self.assertIn("id='session01'", splitHeader)


    def test_receiveStreamError(self):
        """
        Test events when a stream error is received.
        """
        xs = self.xmlstream
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345' version='1.0'>")
        xs.dataReceived("<stream:error/>")
        self.assertTrue(self.gotStreamError)
        self.assertTrue(self.gotStreamEnd)


    def test_sendStreamErrorInitiating(self):
        """
        Test sendStreamError on an initiating xmlstream with a header sent.

        An error should be sent out and the connection lost.
        """
        xs = self.xmlstream
        xs.initiating = True
        xs.sendHeader()
        xs.transport.clear()
        xs.sendStreamError(error.StreamError('version-unsupported'))
        self.assertNotEqual('', xs.transport.value())
        self.assertTrue(self.gotStreamEnd)


    def test_sendStreamErrorInitiatingNoHeader(self):
        """
        Test sendStreamError on an initiating xmlstream without having sent a
        header.

        In this case, no header should be generated. Also, the error should
        not be sent out on the stream. Just closing the connection.
        """
        xs = self.xmlstream
        xs.initiating = True
        xs.transport.clear()
        xs.sendStreamError(error.StreamError('version-unsupported'))
        self.assertNot(xs._headerSent)
        self.assertEqual('', xs.transport.value())
        self.assertTrue(self.gotStreamEnd)


    def test_sendStreamErrorReceiving(self):
        """
        Test sendStreamError on a receiving xmlstream with a header sent.

        An error should be sent out and the connection lost.
        """
        xs = self.xmlstream
        xs.initiating = False
        xs.sendHeader()
        xs.transport.clear()
        xs.sendStreamError(error.StreamError('version-unsupported'))
        self.assertNotEqual('', xs.transport.value())
        self.assertTrue(self.gotStreamEnd)


    def test_sendStreamErrorReceivingNoHeader(self):
        """
        Test sendStreamError on a receiving xmlstream without having sent a
        header.

        In this case, a header should be generated. Then, the error should
        be sent out on the stream followed by closing the connection.
        """
        xs = self.xmlstream
        xs.initiating = False
        xs.transport.clear()
        xs.sendStreamError(error.StreamError('version-unsupported'))
        self.assertTrue(xs._headerSent)
        self.assertNotEqual('', xs.transport.value())
        self.assertTrue(self.gotStreamEnd)


    def test_reset(self):
        """
        Test resetting the XML stream to start a new layer.
        """
        xs = self.xmlstream
        xs.sendHeader()
        stream = xs.stream
        xs.reset()
        self.assertNotEqual(stream, xs.stream)
        self.assertNot(xs._headerSent)


    def test_send(self):
        """
        Test send with various types of objects.
        """
        xs = self.xmlstream
        xs.send('<presence/>')
        self.assertEqual(xs.transport.value(), '<presence/>')

        xs.transport.clear()
        el = domish.Element(('testns', 'presence'))
        xs.send(el)
        self.assertEqual(xs.transport.value(), '<presence/>')

        xs.transport.clear()
        el = domish.Element(('http://etherx.jabber.org/streams', 'features'))
        xs.send(el)
        self.assertEqual(xs.transport.value(), '<stream:features/>')


    def test_authenticator(self):
        """
        Test that the associated authenticator is correctly called.
        """
        connectionMadeCalls = []
        streamStartedCalls = []
        associateWithStreamCalls = []

        class TestAuthenticator:
            def connectionMade(self):
                connectionMadeCalls.append(None)

            def streamStarted(self, rootElement):
                streamStartedCalls.append(rootElement)

            def associateWithStream(self, xs):
                associateWithStreamCalls.append(xs)

        a = TestAuthenticator()
        xs = xmlstream.XmlStream(a)
        self.assertEqual([xs], associateWithStreamCalls)
        xs.connectionMade()
        self.assertEqual([None], connectionMadeCalls)
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345'>")
        self.assertEqual(1, len(streamStartedCalls))
        xs.reset()
        self.assertEqual([None], connectionMadeCalls)



class TestError(Exception):
    pass



class AuthenticatorTest(unittest.TestCase):
    def setUp(self):
        self.authenticator = xmlstream.ListenAuthenticator()
        self.xmlstream = xmlstream.XmlStream(self.authenticator)


    def test_streamStart(self):
        """
        Test streamStart to fill the appropriate attributes from the
        stream header.
        """
        xs = self.xmlstream
        xs.makeConnection(proto_helpers.StringTransport())
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                         "xmlns:stream='http://etherx.jabber.org/streams' "
                         "from='example.org' to='example.com' id='12345' "
                         "version='1.0'>")
        self.assertEqual((1, 0), xs.version)
        self.assertIdentical(None, xs.sid)
        self.assertEqual('jabber:client', xs.namespace)
        self.assertIdentical(None, xs.otherEntity)
        self.assertEqual('example.com', xs.thisEntity.host)


    def test_streamStartLegacy(self):
        """
        Test streamStart to fill the appropriate attributes from the
        stream header for a pre-XMPP-1.0 header.
        """
        xs = self.xmlstream
        xs.makeConnection(proto_helpers.StringTransport())
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345'>")
        self.assertEqual((0, 0), xs.version)


    def test_streamBadVersionOneDigit(self):
        """
        Test streamStart to fill the appropriate attributes from the
        stream header for a version with only one digit.
        """
        xs = self.xmlstream
        xs.makeConnection(proto_helpers.StringTransport())
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345' version='1'>")
        self.assertEqual((0, 0), xs.version)


    def test_streamBadVersionNoNumber(self):
        """
        Test streamStart to fill the appropriate attributes from the
        stream header for a malformed version.
        """
        xs = self.xmlstream
        xs.makeConnection(proto_helpers.StringTransport())
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345' version='blah'>")
        self.assertEqual((0, 0), xs.version)



class ConnectAuthenticatorTest(unittest.TestCase):

    def setUp(self):
        self.gotAuthenticated = False
        self.initFailure = None
        self.authenticator = xmlstream.ConnectAuthenticator('otherHost')
        self.xmlstream = xmlstream.XmlStream(self.authenticator)
        self.xmlstream.addObserver('//event/stream/authd', self.onAuthenticated)
        self.xmlstream.addObserver('//event/xmpp/initfailed', self.onInitFailed)


    def onAuthenticated(self, obj):
        self.gotAuthenticated = True


    def onInitFailed(self, failure):
        self.initFailure = failure


    def testSucces(self):
        """
        Test successful completion of an initialization step.
        """
        class Initializer:
            def initialize(self):
                pass

        init = Initializer()
        self.xmlstream.initializers = [init]

        self.authenticator.initializeStream()
        self.assertEqual([], self.xmlstream.initializers)
        self.assertTrue(self.gotAuthenticated)


    def testFailure(self):
        """
        Test failure of an initialization step.
        """
        class Initializer:
            def initialize(self):
                raise TestError

        init = Initializer()
        self.xmlstream.initializers = [init]

        self.authenticator.initializeStream()
        self.assertEqual([init], self.xmlstream.initializers)
        self.assertFalse(self.gotAuthenticated)
        self.assertNotIdentical(None, self.initFailure)
        self.assertTrue(self.initFailure.check(TestError))


    def test_streamStart(self):
        """
        Test streamStart to fill the appropriate attributes from the
        stream header.
        """
        self.authenticator.namespace = 'testns'
        xs = self.xmlstream
        xs.makeConnection(proto_helpers.StringTransport())
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                         "xmlns:stream='http://etherx.jabber.org/streams' "
                         "from='example.com' to='example.org' id='12345' "
                         "version='1.0'>")
        self.assertEqual((1, 0), xs.version)
        self.assertEqual('12345', xs.sid)
        self.assertEqual('testns', xs.namespace)
        self.assertEqual('example.com', xs.otherEntity.host)
        self.assertIdentical(None, xs.thisEntity)
        self.assertNot(self.gotAuthenticated)
        xs.dataReceived("<stream:features>"
                          "<test xmlns='testns'/>"
                        "</stream:features>")
        self.assertIn(('testns', 'test'), xs.features)
        self.assertTrue(self.gotAuthenticated)



class ListenAuthenticatorTest(unittest.TestCase):
    def setUp(self):
        self.authenticator = xmlstream.ListenAuthenticator()
        self.xmlstream = xmlstream.XmlStream(self.authenticator)


    def test_streamStart(self):
        """
        Test streamStart to fill the appropriate attributes from the
        stream header.
        """
        xs = self.xmlstream
        xs.makeConnection(proto_helpers.StringTransport())
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                         "xmlns:stream='http://etherx.jabber.org/streams' "
                         "from='example.org' to='example.com' id='12345' "
                         "version='1.0'>")
        self.assertEqual((1, 0), xs.version)
        self.assertIdentical(None, xs.sid)
        self.assertEqual('jabber:client', xs.namespace)
        self.assertIdentical(None, xs.otherEntity)
        self.assertEqual('example.com', xs.thisEntity.host)



class TLSInitiatingInitializerTest(unittest.TestCase):
    def setUp(self):
        self.output = []
        self.done = []

        self.savedSSL = xmlstream.ssl

        self.authenticator = xmlstream.Authenticator()
        self.xmlstream = xmlstream.XmlStream(self.authenticator)
        self.xmlstream.send = self.output.append
        self.xmlstream.connectionMade()
        self.xmlstream.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345' version='1.0'>")
        self.init = xmlstream.TLSInitiatingInitializer(self.xmlstream)


    def tearDown(self):
        xmlstream.ssl = self.savedSSL


    def testWantedSupported(self):
        """
        Test start when TLS is wanted and the SSL library available.
        """
        self.xmlstream.transport = proto_helpers.StringTransport()
        self.xmlstream.transport.startTLS = lambda ctx: self.done.append('TLS')
        self.xmlstream.reset = lambda: self.done.append('reset')
        self.xmlstream.sendHeader = lambda: self.done.append('header')

        d = self.init.start()
        d.addCallback(self.assertEquals, xmlstream.Reset)
        starttls = self.output[0]
        self.assertEquals('starttls', starttls.name)
        self.assertEquals(NS_XMPP_TLS, starttls.uri)
        self.xmlstream.dataReceived("<proceed xmlns='%s'/>" % NS_XMPP_TLS)
        self.assertEquals(['TLS', 'reset', 'header'], self.done)

        return d

    if not xmlstream.ssl:
        testWantedSupported.skip = "SSL not available"


    def testWantedNotSupportedNotRequired(self):
        """
        Test start when TLS is wanted and the SSL library available.
        """
        xmlstream.ssl = None

        d = self.init.start()
        d.addCallback(self.assertEquals, None)
        self.assertEquals([], self.output)

        return d


    def testWantedNotSupportedRequired(self):
        """
        Test start when TLS is wanted and the SSL library available.
        """
        xmlstream.ssl = None
        self.init.required = True

        d = self.init.start()
        self.assertFailure(d, xmlstream.TLSNotSupported)
        self.assertEquals([], self.output)

        return d


    def testNotWantedRequired(self):
        """
        Test start when TLS is not wanted, but required by the server.
        """
        tls = domish.Element(('urn:ietf:params:xml:ns:xmpp-tls', 'starttls'))
        tls.addElement('required')
        self.xmlstream.features = {(tls.uri, tls.name): tls}
        self.init.wanted = False

        d = self.init.start()
        self.assertEquals([], self.output)
        self.assertFailure(d, xmlstream.TLSRequired)

        return d


    def testNotWantedNotRequired(self):
        """
        Test start when TLS is not wanted, but required by the server.
        """
        tls = domish.Element(('urn:ietf:params:xml:ns:xmpp-tls', 'starttls'))
        self.xmlstream.features = {(tls.uri, tls.name): tls}
        self.init.wanted = False

        d = self.init.start()
        d.addCallback(self.assertEqual, None)
        self.assertEquals([], self.output)
        return d


    def testFailed(self):
        """
        Test failed TLS negotiation.
        """
        # Pretend that ssl is supported, it isn't actually used when the
        # server starts out with a failure in response to our initial
        # C{starttls} stanza.
        xmlstream.ssl = 1

        d = self.init.start()
        self.assertFailure(d, xmlstream.TLSFailed)
        self.xmlstream.dataReceived("<failure xmlns='%s'/>" % NS_XMPP_TLS)
        return d



class TestFeatureInitializer(xmlstream.BaseFeatureInitiatingInitializer):
    feature = ('testns', 'test')

    def start(self):
        return defer.succeed(None)



class BaseFeatureInitiatingInitializerTest(unittest.TestCase):

    def setUp(self):
        self.xmlstream = xmlstream.XmlStream(xmlstream.Authenticator())
        self.init = TestFeatureInitializer(self.xmlstream)


    def testAdvertized(self):
        """
        Test that an advertized feature results in successful initialization.
        """
        self.xmlstream.features = {self.init.feature:
                                   domish.Element(self.init.feature)}
        return self.init.initialize()


    def testNotAdvertizedRequired(self):
        """
        Test that when the feature is not advertized, but required by the
        initializer, an exception is raised.
        """
        self.init.required = True
        self.assertRaises(xmlstream.FeatureNotAdvertized, self.init.initialize)


    def testNotAdvertizedNotRequired(self):
        """
        Test that when the feature is not advertized, and not required by the
        initializer, the initializer silently succeeds.
        """
        self.init.required = False
        self.assertIdentical(None, self.init.initialize())



class ToResponseTest(unittest.TestCase):

    def test_toResponse(self):
        """
        Test that a response stanza is generated with addressing swapped.
        """
        stanza = domish.Element(('jabber:client', 'iq'))
        stanza['type'] = 'get'
        stanza['to'] = 'user1@example.com'
        stanza['from'] = 'user2@example.com/resource'
        stanza['id'] = 'stanza1'
        response = xmlstream.toResponse(stanza, 'result')
        self.assertNotIdentical(stanza, response)
        self.assertEqual(response['from'], 'user1@example.com')
        self.assertEqual(response['to'], 'user2@example.com/resource')
        self.assertEqual(response['type'], 'result')
        self.assertEqual(response['id'], 'stanza1')


    def test_toResponseNoFrom(self):
        """
        Test that a response is generated from a stanza without a from address.
        """
        stanza = domish.Element(('jabber:client', 'iq'))
        stanza['type'] = 'get'
        stanza['to'] = 'user1@example.com'
        response = xmlstream.toResponse(stanza)
        self.assertEqual(response['from'], 'user1@example.com')
        self.failIf(response.hasAttribute('to'))


    def test_toResponseNoTo(self):
        """
        Test that a response is generated from a stanza without a to address.
        """
        stanza = domish.Element(('jabber:client', 'iq'))
        stanza['type'] = 'get'
        stanza['from'] = 'user2@example.com/resource'
        response = xmlstream.toResponse(stanza)
        self.failIf(response.hasAttribute('from'))
        self.assertEqual(response['to'], 'user2@example.com/resource')


    def test_toResponseNoAddressing(self):
        """
        Test that a response is generated from a stanza without any addressing.
        """
        stanza = domish.Element(('jabber:client', 'message'))
        stanza['type'] = 'chat'
        response = xmlstream.toResponse(stanza)
        self.failIf(response.hasAttribute('to'))
        self.failIf(response.hasAttribute('from'))


    def test_noID(self):
        """
        Test that a proper response is generated without id attribute.
        """
        stanza = domish.Element(('jabber:client', 'message'))
        response = xmlstream.toResponse(stanza)
        self.failIf(response.hasAttribute('id'))



class DummyFactory(object):
    """
    Dummy XmlStream factory that only registers bootstrap observers.
    """
    def __init__(self):
        self.callbacks = {}


    def addBootstrap(self, event, callback):
        self.callbacks[event] = callback



class DummyXMPPHandler(xmlstream.XMPPHandler):
    """
    Dummy XMPP subprotocol handler to count the methods are called on it.
    """
    def __init__(self):
        self.doneMade = 0
        self.doneInitialized = 0
        self.doneLost = 0


    def makeConnection(self, xs):
        self.connectionMade()


    def connectionMade(self):
        self.doneMade += 1


    def connectionInitialized(self):
        self.doneInitialized += 1


    def connectionLost(self, reason):
        self.doneLost += 1



class XMPPHandlerTest(unittest.TestCase):
    """
    Tests for L{xmlstream.XMPPHandler}.
    """

    def test_interface(self):
        """
        L{xmlstream.XMPPHandler} implements L{ijabber.IXMPPHandler}.
        """
        verifyObject(ijabber.IXMPPHandler, xmlstream.XMPPHandler())


    def test_send(self):
        """
        Test that data is passed on for sending by the stream manager.
        """
        class DummyStreamManager(object):
            def __init__(self):
                self.outlist = []

            def send(self, data):
                self.outlist.append(data)

        handler = xmlstream.XMPPHandler()
        handler.parent = DummyStreamManager()
        handler.send('<presence/>')
        self.assertEquals(['<presence/>'], handler.parent.outlist)


    def test_makeConnection(self):
        """
        Test that makeConnection saves the XML stream and calls connectionMade.
        """
        class TestXMPPHandler(xmlstream.XMPPHandler):
            def connectionMade(self):
                self.doneMade = True

        handler = TestXMPPHandler()
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        handler.makeConnection(xs)
        self.assertTrue(handler.doneMade)
        self.assertIdentical(xs, handler.xmlstream)


    def test_connectionLost(self):
        """
        Test that connectionLost forgets the XML stream.
        """
        handler = xmlstream.XMPPHandler()
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        handler.makeConnection(xs)
        handler.connectionLost(Exception())
        self.assertIdentical(None, handler.xmlstream)



class XMPPHandlerCollectionTest(unittest.TestCase):
    """
    Tests for L{xmlstream.XMPPHandlerCollection}.
    """

    def setUp(self):
        self.collection = xmlstream.XMPPHandlerCollection()


    def test_interface(self):
        """
        L{xmlstream.StreamManager} implements L{ijabber.IXMPPHandlerCollection}.
        """
        verifyObject(ijabber.IXMPPHandlerCollection, self.collection)


    def test_addHandler(self):
        """
        Test the addition of a protocol handler.
        """
        handler = DummyXMPPHandler()
        handler.setHandlerParent(self.collection)
        self.assertIn(handler, self.collection)
        self.assertIdentical(self.collection, handler.parent)


    def test_removeHandler(self):
        """
        Test removal of a protocol handler.
        """
        handler = DummyXMPPHandler()
        handler.setHandlerParent(self.collection)
        handler.disownHandlerParent(self.collection)
        self.assertNotIn(handler, self.collection)
        self.assertIdentical(None, handler.parent)



class StreamManagerTest(unittest.TestCase):
    """
    Tests for L{xmlstream.StreamManager}.
    """

    def setUp(self):
        factory = DummyFactory()
        self.streamManager = xmlstream.StreamManager(factory)


    def test_basic(self):
        """
        Test correct initialization and setup of factory observers.
        """
        sm = self.streamManager
        self.assertIdentical(None, sm.xmlstream)
        self.assertEquals([], sm.handlers)
        self.assertEquals(sm._connected,
                          sm.factory.callbacks['//event/stream/connected'])
        self.assertEquals(sm._authd,
                          sm.factory.callbacks['//event/stream/authd'])
        self.assertEquals(sm._disconnected,
                          sm.factory.callbacks['//event/stream/end'])
        self.assertEquals(sm.initializationFailed,
                          sm.factory.callbacks['//event/xmpp/initfailed'])


    def test_connected(self):
        """
        Test that protocol handlers have their connectionMade method called
        when the XML stream is connected.
        """
        sm = self.streamManager
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        sm._connected(xs)
        self.assertEquals(1, handler.doneMade)
        self.assertEquals(0, handler.doneInitialized)
        self.assertEquals(0, handler.doneLost)


    def test_connectedLogTrafficFalse(self):
        """
        Test raw data functions unset when logTraffic is set to False.
        """
        sm = self.streamManager
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        sm._connected(xs)
        self.assertIdentical(None, xs.rawDataInFn)
        self.assertIdentical(None, xs.rawDataOutFn)


    def test_connectedLogTrafficTrue(self):
        """
        Test raw data functions set when logTraffic is set to True.
        """
        sm = self.streamManager
        sm.logTraffic = True
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        sm._connected(xs)
        self.assertNotIdentical(None, xs.rawDataInFn)
        self.assertNotIdentical(None, xs.rawDataOutFn)


    def test_authd(self):
        """
        Test that protocol handlers have their connectionInitialized method
        called when the XML stream is initialized.
        """
        sm = self.streamManager
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        sm._authd(xs)
        self.assertEquals(0, handler.doneMade)
        self.assertEquals(1, handler.doneInitialized)
        self.assertEquals(0, handler.doneLost)


    def test_disconnected(self):
        """
        Test that protocol handlers have their connectionLost method
        called when the XML stream is disconnected.
        """
        sm = self.streamManager
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        sm._disconnected(xs)
        self.assertEquals(0, handler.doneMade)
        self.assertEquals(0, handler.doneInitialized)
        self.assertEquals(1, handler.doneLost)


    def test_addHandler(self):
        """
        Test the addition of a protocol handler while not connected.
        """
        sm = self.streamManager
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)

        self.assertEquals(0, handler.doneMade)
        self.assertEquals(0, handler.doneInitialized)
        self.assertEquals(0, handler.doneLost)


    def test_addHandlerInitialized(self):
        """
        Test the addition of a protocol handler after the stream
        have been initialized.

        Make sure that the handler will have the connected stream
        passed via C{makeConnection} and have C{connectionInitialized}
        called.
        """
        sm = self.streamManager
        xs = xmlstream.XmlStream(xmlstream.Authenticator())
        sm._connected(xs)
        sm._authd(xs)
        handler = DummyXMPPHandler()
        handler.setHandlerParent(sm)

        self.assertEquals(1, handler.doneMade)
        self.assertEquals(1, handler.doneInitialized)
        self.assertEquals(0, handler.doneLost)


    def test_sendInitialized(self):
        """
        Test send when the stream has been initialized.

        The data should be sent directly over the XML stream.
        """
        factory = xmlstream.XmlStreamFactory(xmlstream.Authenticator())
        sm = xmlstream.StreamManager(factory)
        xs = factory.buildProtocol(None)
        xs.transport = proto_helpers.StringTransport()
        xs.connectionMade()
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345'>")
        xs.dispatch(xs, "//event/stream/authd")
        sm.send("<presence/>")
        self.assertEquals("<presence/>", xs.transport.value())


    def test_sendNotConnected(self):
        """
        Test send when there is no established XML stream.

        The data should be cached until an XML stream has been established and
        initialized.
        """
        factory = xmlstream.XmlStreamFactory(xmlstream.Authenticator())
        sm = xmlstream.StreamManager(factory)
        handler = DummyXMPPHandler()
        sm.addHandler(handler)

        xs = factory.buildProtocol(None)
        xs.transport = proto_helpers.StringTransport()
        sm.send("<presence/>")
        self.assertEquals("", xs.transport.value())
        self.assertEquals("<presence/>", sm._packetQueue[0])

        xs.connectionMade()
        self.assertEquals("", xs.transport.value())
        self.assertEquals("<presence/>", sm._packetQueue[0])

        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345'>")
        xs.dispatch(xs, "//event/stream/authd")

        self.assertEquals("<presence/>", xs.transport.value())
        self.failIf(sm._packetQueue)


    def test_sendNotInitialized(self):
        """
        Test send when the stream is connected but not yet initialized.

        The data should be cached until the XML stream has been initialized.
        """
        factory = xmlstream.XmlStreamFactory(xmlstream.Authenticator())
        sm = xmlstream.StreamManager(factory)
        xs = factory.buildProtocol(None)
        xs.transport = proto_helpers.StringTransport()
        xs.connectionMade()
        xs.dataReceived("<stream:stream xmlns='jabber:client' "
                        "xmlns:stream='http://etherx.jabber.org/streams' "
                        "from='example.com' id='12345'>")
        sm.send("<presence/>")
        self.assertEquals("", xs.transport.value())
        self.assertEquals("<presence/>", sm._packetQueue[0])


    def test_sendDisconnected(self):
        """
        Test send after XML stream disconnection.

        The data should be cached until a new XML stream has been established
        and initialized.
        """
        factory = xmlstream.XmlStreamFactory(xmlstream.Authenticator())
        sm = xmlstream.StreamManager(factory)
        handler = DummyXMPPHandler()
        sm.addHandler(handler)

        xs = factory.buildProtocol(None)
        xs.connectionMade()
        xs.transport = proto_helpers.StringTransport()
        xs.connectionLost(None)

        sm.send("<presence/>")
        self.assertEquals("", xs.transport.value())
        self.assertEquals("<presence/>", sm._packetQueue[0])
