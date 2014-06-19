saymeando
=========

A bittorrent client in Python


Next steps:
* Thread id in logging
* Log different log levels
* move logging to separate class
* http://stackoverflow.com/questions/12479570/given-a-torrent-file-how-do-i-generate-a-magnet-link-in-python
* http://twistedmatrix.com/documents/13.2.0/core/howto/logging.html
* http://stackoverflow.com/questions/13748222/twisted-log-level-switch
* https://twistedmatrix.com/documents/12.0.0/core/howto/clients.html
* 

log.msg("This is important!", logLevel=logging.CRITICAL)
log.msg("Don't mind", logLevel=logging.DEBUG)
log.msg("This is just FYI", logLevel=logging.INFO)
log.msg("This is a no no", logLevel=logging.ERROR)
* 

Next steps:
- having a TestHelper class to store all testdata, or have helper functions, or make stuff global
- modify test_createServer to test that the server is actually a kademlia server type
- write tests to read and analyse log file
- look into twisted logging create my own Logpublisher and set it in twisted.log module?
- Have a 3pp folder and store all 3pp files there
- logging: in the code only state: log("The file doesn't exist, 20140619 8:44, FileNotFound Error")
- run code with flag -logLevel = log.DEBUG for instance
- if DEBUG level, take the entire string, if ERROR level, take part 0 and 1 and if INFO only 0. Or something like that
- locating peers in network
- look into the commit with pep8, do you really need to commit twice?
- remember to use present tense when commit changes
- get familiar with gitk
- learn more about git, eg git commit --amend
