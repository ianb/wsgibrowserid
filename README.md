# WSGI BrowserID

This is a very simple application to handle [browserid](http://browserid.org) logins, specifically to set signed cookies for your BrowserID login.  It is an application and a small Javascript file that lightly wraps the BrowserID library.  You don't need to integrate this into your application, or even have an application written in Python, to use this.  All you have to do is make sure that your Cookie signing algorithm is the same as WSGIBrowserID's signing algorithm.  And better, you can change WSGIBrowserID's signing to match your existing system.

## Configuration

Look in docs/example.wsgi for an example of how to setup the application.

The application uses pycurl, which you must install.  It has no other prerequesites.  Should be okay with Python 2.5 - 2.7.

## Using in your app

You must include `https://browserid.org/include.js`, and also include `/wsgibrowserid.js` (under whatever path you mount the application). This will define an object `WSGIBrowserID`.

There are three provided functions:

`WSGIBrowserID.login(callback)`:
  This logs the user in, calling `callback(data)` with all the data sent from `browserid.org` (e.g., `data.email`).  If the login fails it will call `callback(null)`.

`WSGIBrowserID.logout()`:
  Logs the user out.  Simply unsets the cookie.

`WSGIBrowserID.loginStatus()`:
  Returns the userid (email address), or null.

## To Do

* More examples of hashing functions, secret getters.

* Way to do HttpOnly cookies (I guess set a second cookie with the email)

* Way to confirm the login, not just trust the cookie is valid

* Maybe some timestamping, expiration, and other standard login cookie security practices

* Some callback(s) that the server can do on login (e.g., have it connect to `http://youapp.org/create_user?email=loggedinuser@address.com`)

* More formal logout than just deleting the cookie.  Or with HttpOnly, server-side delete of the cookie.

* Write the whole thing in PHP; same concept, another deployment technique.

* Maybe setup an App Engine recipe.

* No good error messages, and many "typical" errors aren't handled gracefully.
