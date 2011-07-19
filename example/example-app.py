from wsgibrowserid.wsgiapp import Application


page = '''\
<html>
 <head>
  <script src="https://browserid.org/include.js"></script>
  <script src="/auth/wsgibrowserid.js"></script>
 </head>
 <body>
 <div id="loginstatus">login status</div>
  <script>
  function updateStatus() {
    var username = WSGIBrowserID.loginStatus();
    var el = document.getElementById('loginstatus');
    if (username) {
      el.innerHTML = 'Logged in as ' + username + ' <a href="#" onclick="WSGIBrowserID.logout(); updateStatus(); return false">logout</a>';
    } else {
      el.innerHTML = '<a href="#" onclick="WSGIBrowserID.login(updateStatus); return false">login</a>';
    }
  }
  //window.addEventListener('load', updateStatus(), false);
  updateStatus();
  </script>
 </body>
</html>
'''


class ExampleApp(object):

    def __init__(self, auth_app):
        self.auth_app = auth_app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith('/auth/'):
            environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '') + '/auth'
            environ['PATH_INFO'] = path_info[5:]
            return self.auth_app(environ, start_response)
        start_response('200 OK', [('content-type', 'text/html')])
        return [page]


if __name__ == '__main__':
    from wsgiref import simple_server
    app = ExampleApp(Application())
    server = simple_server.make_server('127.0.0.1', 8080, app)
    print 'server on http://localhost:8080'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
