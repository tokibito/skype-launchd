# coding: utf-8
import cgi
from optparse import OptionParser
from wsgiref import simple_server

from skypelaunchd.launcher import Launcher


class Application(object):
    def __init__(self):
        self.launcher = Launcher()

    def __call__(self, environ, start_response):
        """entry point
        """
        http_method = environ.get('REQUEST_METHOD')
        path = environ.get('PATH_INFO')
        params = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        self.dispatch(path, http_method, params, environ, start_response)

    def dispatch(self, path, http_method, params, environ, start_response):
        if http_method != 'GET':
            return self.badrequest(start_response)
        if path != '/':
            return self.badrequest(start_response)
        username = params.get('username') and params['username'][0]
        password = params.get('password') and params['password'][0]
        dispnum = params.get('dispnum') and params['dispnum'][0]
        try:
            dispnum = int(dispnum)
        except ValueError:
            return self.badrequest(start_response)
        pid = self.launch(username, password, dispnum)
        return self.ok(pid, start_response)

    def launch(self, username, password, dispnum):
        """skype起動
        """
        return_code = self.launcher.launch_skype(username, password, dispnum)
        pidpath = self.launcher.get_pid_file_path(username)
        try:
            f = open(pidpath)
            pid = int(f.read())
        except IOError:
            pid = None
        return pid

    def ok(self, pid, start_response):
        start_response('200 OK', [
            ('Content-Type', 'application/json')
        ])
        return '{"status": "OK"}'

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

    run(options.host, options.port, app)
