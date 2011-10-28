# coding: utf-8
import os
import cgi
import time
import json
from optparse import OptionParser
from wsgiref import simple_server

from skypelaunchd.launcher import Launcher


class Application(object):
    def __init__(self):
        self.launcher = Launcher()
        self.processes = []

    def __call__(self, environ, start_response):
        """entry point
        """
        http_method = environ.get('REQUEST_METHOD')
        path = environ.get('PATH_INFO')
        params = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        post_env = environ.copy()
        post_data = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=post_env,
            keep_blank_values=True)
        return self.dispatch(path, http_method, params, post_data, environ, start_response)

    def add_process(self, pid, username, dispnum):
        """プロセス情報保持
        """
        self.processes.append({
            'pid': pid,
            'username': username,
            'dispnum': dispnum,
        })

    def remove_process(self, pid):
        new_processes = []
        for process in self.processes:
            if process['pid'] != pid:
                new_processes.append(process)
        self.processes = new_processes

    def dispatch(self, path, http_method, params, post_data, environ, start_response):
        """ディスパッチャ
        """
        if path == '/start':
            if http_method != 'POST':
                return self.badrequest(start_response)
            return self.start_request(post_data, environ, start_response)
        elif path == '/stop':
            if http_method != 'POST':
                return self.badrequest(start_response)
            return self.stop_request(post_data, environ, start_response)
        elif path == '/status':
            if http_method != 'GET':
                return self.badrequest(start_response)
            return self.status_request(post_data, environ, start_response)
        else:
            return self.badrequest(start_response)

    def status_request(self, post_data, environ, start_response):
        """ステータス情報
        """
        result = {
            'processes': self.processes,
        }
        return self.ok(start_response, result)

    def start_request(self, post_data, environ, start_response):
        """起動
        """
        username = post_data.getvalue('username')
        password = post_data.getvalue('password')
        dispnum = post_data.getvalue('dispnum')
        if not dispnum:
            return self.badrequest(start_response)
        try:
            dispnum = int(dispnum)
        except ValueError:
            return self.badrequest(start_response)
        if not username or len(username) is 0:
            return self.badrequest(start_response)
        if not password or len(password) is 0:
            return self.badrequest(start_response)
        pid = self.launch(username, password, dispnum)
        if not pid:
            return self.badrequest(start_response)
        self.add_process(pid, username, dispnum)
        return self.ok(start_response, {'pid': pid})

    def stop_request(self, post_data, environ, start_response):
        """停止
        """
        pid_raw = post_data.getvalue('pid')
        try:
            pid = int(pid_raw)
        except ValueError:
            return self.badrequest(start_response)
        self.launcher.kill_process(pid)
        self.remove_process(pid)
        return self.ok(start_response)

    def launch(self, username, password, dispnum):
        """skype起動
        """
        return_code = self.launcher.launch_skype(username, password, dispnum)
        pidpath = self.launcher.get_pid_file_path(username)
        for i in range(10):
            time.sleep(1)
            if os.path.exists(pidpath):
                f = open(pidpath)
                pid = int(f.read())
                break
        else:
            pid = None
        return pid

    def ok(self, start_response, data=None):
        start_response('200 OK', [
            ('Content-Type', 'application/json')
        ])
        result = {
            'status': "OK",
        }
        result.update(data or {})
        return json.dumps(result)

    def badrequest(self, start_response):
        start_response('400 BadRequest', [
            ('Content-Type', 'application/json')
        ])
        return '{"status": "NG"}'



def run(host, port, app):
    server = simple_server.make_server(host, port, app)
    server.serve_forever()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--host', dest='host', default='localhost', help='hostname')
    parser.add_option('--port', dest='port', default=4300,
        type='int', help='port number')

    options, args = parser.parse_args()

    app = Application()

    print "Serving skype-launchd on", options.host, "port", options.port, "..."

    try:
        run(options.host, options.port, app)
    except KeyboardInterrupt:
        pass
