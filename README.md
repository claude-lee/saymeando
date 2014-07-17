saymeando
=========

A bittorrent client in Python

Next steps:
* 1) Log different log levels
* http://stackoverflow.com/questions/12479570/given-a-torrent-file-how-do-i-generate-a-magnet-link-in-python
* http://twistedmatrix.com/documents/13.2.0/core/howto/logging.html
* http://stackoverflow.com/questions/13748222/twisted-log-level-switch
* https://twistedmatrix.com/documents/12.0.0/core/howto/clients.html
* log.msg("Don't mind", logLevel=logging.DEBUG)
* log.msg("This is just FYI", logLevel=logging.INFO)
* log.msg("This is a no no", logLevel=logging.ERROR)
* 1) write tests to read and analyse log file
* 1) look into twisted logging create my own Logpublisher and set it in twisted.log module?
* 2) Have a 3pp folder and store all 3pp files there, like bencode
* 1) logging: in the code only state: log("The file doesn't exist, 20140619 8:44, FileNotFound Error")
* 1) run code with flag -logLevel = log.DEBUG for instance
* 1) if DEBUG level, take the entire string, if ERROR level, take part 0 and 1 and if INFO only 0. Or something like that
* locating peers in network
* learn more about git, eg git commit --amend
* http://stackoverflow.com/questions/3347019/how-can-one-use-the-logging-module-in-python-with-the-unittest-module?rq=1
* http://stackoverflow.com/questions/15971735/running-single-test-from-unittest-testcase-via-command-line
* 1) have sections for log chapters, product shouldn't know about test, not even logging
* try coverage
* 1) yes, have constants for logging messages
* log.section("discovery")
* discovery >> 2014-07-11 09:35:53+0200 [-] --testgettingTorrent---------------------
* discovery >> 2014-07-11 09:35:53+0200 [-] [5] OPENING torrent file
* log.section("retrieval")
* retrieval >> 2014-07-11 09:35:53+0200 [-] #--testgettingTorrent---------------------#
* retrieval >> 2014-07-11 09:35:53+0200 [-] [5] OPENING torrent file
* 1) move decorator to testhelper


DONE
=====
* verify with one test that logged version is in logfile.
