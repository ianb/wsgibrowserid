import pycurl
import os
import cgi
import urllib
try:
    import simplejson as json
except ImportError:
    import json

here = os.path.dirname(__file__)


class Application(object):

    def __init__(self, audience=None, hasher=None, secret_getter=None,
                 cookie_name="auth"):
        self.js = {}
        self.audience = audience
        self.hasher = get_hasher(hasher)
        self.secret_getter = get_secret_getter(secret_getter)
        self._secret = None
        self.cookie_name = cookie_name

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info == '/wsgibrowserid.js':
            return self.js_file(environ, start_response)
        elif path_info == '/check':
            return self.check(environ, start_response)
        else:
            start_response('404 Not Found', [('Content-type', 'text/plain')])
            return ['Not Found']

    def js_file(self, environ, start_response):
        base_url = self.base_url(environ)
        if base_url not in self.js:
            fp = open(os.path.join(here, 'wsgibrowserid.js'))
            try:
                c = fp.read()
            finally:
                fp.close()
            url = base_url.rstrip('/') + '/check'
            c = c.replace('__URL__', url)
            c = c.replace('__COOKIE__', self.cookie_name)
            c = c.replace('__DECODE_COOKIE__', self.hasher.decodeCookie)
            self.js[base_url] = c
        ## FIXME: should add cache headers here, content-length, conditional
        ## gets, etc:
        start_response('200 OK', [('Content-Type', 'text/javascript')])
        return [self.js[base_url]]

    def base_url(self, environ):
        scheme = environ['wsgi.url_scheme']
        base_url = scheme + '://'
        host = environ.get('HTTP_HOST', environ.get('SERVER_NAME', ''))
        if ':' in host:
            host, port = host.split(':', 1)
        else:
            port = ''
        if scheme == 'http' and port and port != '80':
            host += ':' + port
        elif scheme == 'https' and port and port != '443':
            host += ':' + port
        base_url += host + environ.get('SCRIPT_NAME', '')
        return base_url

    def check(self, environ, start_response):
        qs = dict(cgi.parse_qsl(environ.get('QUERY_STRING')))
        audience = self.audience
        if audience is None:
            audience = environ['HTTP_HOST']
        url = 'https://browserid.org/verify?assertion=%s&audience=%s' % (
            urllib.quote(qs['assertion']), urllib.quote(audience))
        resp = get_url(url)
        data = json.loads(resp)
        print data
        if data.get('audience') != audience:
            resp_data = {'status': 'failed',
                         'error': 'Bad audience in response: %r' % data.get('audience')}
        else:
            resp_data = data
        resp_data = json.dumps(resp_data)
        headers = [('Content-Type', 'application/json'),
                   ('Content-Length', str(len(resp_data)))]
        headers.extend(self.extra_headers(environ, data))
        start_response('200 OK', headers)
        return [resp_data]

    def extra_headers(self, environ, data):
        email = data['email']
        secret = self.secret_getter()
        ## FIXME: need a nonce or something too, though hasher could handle it
        ## Also a way to refresh the cookie
        hash = urllib.quote(self.hasher(email, secret, environ))
        return [('Set-Cookie', self.cookie_name + '=' + hash + '; Path=/')]


def get_url(url):
    x = []
    curl = pycurl.Curl()
    curl.setopt(pycurl.WRITEFUNCTION, x.append)
    #curl.setopt(pycurl.CAINFO, "myFineCA.crt")
    curl.setopt(pycurl.SSL_VERIFYPEER, 1)
    curl.setopt(pycurl.SSL_VERIFYHOST, 2)
    curl.setopt(pycurl.URL, url)
    curl.perform()
    #assert curl.getinfo(pycurl.CURLINFO_RESPONSE_CODE) == 200
    return ''.join(x)


def get_hasher(hasher):
    ## FIXME: load hashers or something
    if not hasher:
        return default_hasher
    if isinstance(hasher, basestring):
        return get_object(hasher)
    return hasher


def default_hasher(email, secret, environ):
    import hmac
    return email + ' ' + hmac.new(secret, email).hexdigest()

default_hasher.decodeCookie = """\
function decodeCookie(cookie) {
  cookie = decodeURIComponent(cookie);
  cookie = cookie.split(' ');
  if (cookie.length && cookie[0]) {
    return cookie[0];
  }
  return null;
}
"""


def get_secret_getter(secret_getter, secret=None, secret_file=None):
    if secret_getter:
        if secret:
            raise Exception('Cannot provide secret_getter and secret')
        if secret_file:
            raise Exception('Cannot provide secret_getter and secret_file')
        if isinstance(secret_getter, basestring):
            return get_object(secret_getter)
        return secret_getter
    if secret:
        if secret_file:
            raise Exception('Cannot provide secret and secret_file')

        def secret_getter():
            return secret
        return secret_getter
    secret_file = secret_file or DEFAULT_SECRET_FILENAME
    return FileSecret(secret_file)


class FileSecret(object):
    def __init__(self, filename):
        self.filename = filename
        self._secret = None

    def __call__(self):
        ## FIXME: lock on this?
        if self._secret is not None:
            return self._secret
        if not os.path.exists(self.filename):
            fp = open(self.filename, 'wb')
            fp.write(generate_secret())
            fp.close()
        fp = open(self.filename, 'rb')
        secret = fp.read().strip()
        fp.close()
        self._secret = secret
        return secret


def generate_secret(length=20):
    s = os.urandom(length).encode('base64').replace('\n', '')
    ## Since base64 expands it:
    return s[:length]


def get_object(name):
    if ':' in name:
        name, obj = name.split(':', 1)
    else:
        obj = None
    if name.endswith('.py'):
        ns = {}
        execfile(name, ns)
        if not obj:
            ## FIXME: not sure what to do?
            raise Exception('Must give %s:obj_name' % name)
        return ns[obj]
    else:
        __import__(name)
        import sys
        mod = sys.modules[name]
        if not obj:
            raise Exception('You must give %s:obj_name' % name)
        result = eval(obj, mod.__dict__)
        return result


DEFAULT_SECRET_FILENAME = '/tmp/wsgibrowserid-secret.txt'


def make_app(global_conf=None, audience=None, hasher=None,
             secret_getter=None,
             secret=None,
             secret_file=None,
             cookie_name="auth"):
    audience = audience or None
    hasher = get_hasher(hasher)
    secret_getter = get_secret_getter(secret_getter, secret, secret_file)
    return Application(audience=audience, hasher=hasher, secret_getter=secret_getter,
                       cookie_name=cookie_name)
