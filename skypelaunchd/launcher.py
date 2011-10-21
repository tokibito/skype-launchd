# coding: utf-8
import os
import logging
import subprocess

SCRIPT_NAME = 'launch_skype'
PIDFILE = '/var/run/skype/%s.pid'


class Launcher(object):
    def __init__(self):
        self.notifiers = []

    def get_script_path(self):
        """起動スクリプトのパスを返す
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, SCRIPT_NAME)

    def get_pid_file_path(self, username):
        """pidfileのパス
        """
        return PIDFILE % username

    def connect_notifier(self, notifier):
        """通知を追加
        """
        self.notifiers.append(notifier)

    def launch_skype(self, username, password, dispnum):
        """skypeを起動する
        """
        logging.info('launch skype username=%s, dispnum=%s' % (
            username, dispnum))
        return_code = subprocess.call(
            [self.get_script_path(), username, password, str(dispnum)])
        self.launched(username, dispnum, return_code)
        return return_code

    def launched(self, username, dispnum, return_code):
        """通知
        """
        for notifier in self.notifiers:
            notifier(username, dispnum, return_code,
                self.get_pid_file_path(username))
