# coding: utf-8
import time
import logging

def logging_notifier(username, dispnum, return_code, pidpath):
    """logging
    """
    try:
        f = open(pidpath)
        pid = int(f.read())
    except IOError:
        pid = None
    logging.info('[%s]username=%s, dispnum=%s, pid=%s, ' % (
        time.localtime(),
        dispnum,
        pid)
