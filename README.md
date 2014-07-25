saymeando
=========

A bittorrent client in Python

Next steps:

* http://twistedmatrix.com/documents/13.2.0/core/howto/logging.html
* http://stackoverflow.com/questions/13748222/twisted-log-level-switch
* log.msg("Don't mind", logLevel=logging.DEBUG)
* log.msg("This is just FYI", logLevel=logging.INFO)
* log.msg("This is a no no", logLevel=logging.ERROR)
* 1) have sections for log chapters, product shouldn't know about test, not even logging
* 1) look into twisted logging create my own Logpublisher and set it in twisted.log module?
* 2) Have a 3pp folder and store all 3pp files there, like bencode
* 1) logging: in the code only state: log("The file doesn't exist, 20140619 8:44, FileNotFound Error")
* 1) run code with flag -logLevel = log.DEBUG for instance
* 1) Log different log levels
* 1) if DEBUG level, take the entire string, if ERROR level, take part 0 and 1 and if INFO only 0. Or something like that
* http://stackoverflow.com/questions/3347019/how-can-one-use-the-logging-module-in-python-with-the-unittest-module?rq=1
* try coverage, Coverage.py
* locating peers in network
* https://twistedmatrix.com/documents/12.0.0/core/howto/clients.html
* http://stackoverflow.com/questions/12479570/given-a-torrent-file-how-do-i-generate-a-magnet-link-in-python


DONE
=====
* verify with one test that logged version is in logfile.
* move decorator to testhelper
* have constants for logging messages
* First cache the log with same log id in dict or list or
* write tests to read and analyse log file
* test the logging of all testcases