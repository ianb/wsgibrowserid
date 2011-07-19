## The path where you keep the source:
wsgibrowserid_path = '/path/to/src/wsgibrowserid'

## The hash algorithm; this is a function like:
##   def hasher(email, secret, environ):
##       return urllib.quote(email + ' ' + md5.new(email + secret).hexdigest())
##   hasher.decodeCookie = """\
## function decodeCookie(cookie) {
##   return decodeURIComponent(cookie).split(' ')[0];
## }
## """
## The default uses hmac.
hasher = None

## The name of the cookie to set:
cookie_name = 'auth'


## You can set one of these:
## secret_getter is a function (no arguments) that returns the secret
secret_getter = None
## secret is an actual secret (a string):
secret = None
## secret_file is a file where the secret is stored; if the file doesn't exist
## then wsgibrowserid will create the file with a new secret:
secret_file = None


## The domain (audience) that your app is hosted on; you don't have to set this.
## You also need the port if it's not :80 (or https/443)
audience = None


## You shouldn't need to edit after here:

import sys
sys.path.insert(0, wsgibrowserid_path)
from wsgibrowserid.wsgiapp import Application
application = Application(
    audience=audience, hasher=hasher,
    secret_getter=secret_getter, cookie_name=cookie_name)
