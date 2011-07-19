(function (exports) {

  var browseridLocation = "__URL__";
  var cookieName = "__COOKIE__";

  // FIXME: should get if navigator.id.getVerifiedEmail is available?

  function login(callback) {
    navigator.id.getVerifiedEmail(function(assertion) {
      if (assertion) {
        var req = new XMLHttpRequest();
        req.open('GET', browseridLocation+'?assertion=' + encodeURIComponent(assertion));
        req.onreadystatechange = function () {
          if (req.readyState != 4) {
            // Not ready
            return;
          }
          if (req.status != 200) {
            if (callback) {
              // FIXME: no way to note the kind of error
              callback(false);
            }
            return;
          }
          var data = JSON.parse(req.responseText);
          callback(data);
        };
        req.send();
        // This code will be invoked once the user has successfully
        // selected an email address they control to sign in with.
      } else {
        if (callback) {
          callback(false);
        }
      }
    });
  }

  function loginStatus() {
    var cookie = readCookie(cookieName);
    if (! cookie) {
      return null;
    }
    return decodeCookie(cookie);
  }

  __DECODE_COOKIE__

  function logout() {
    eraseCookie(cookieName);
  }

  function createCookie(name, value, days) {
    if (days) {
      var date = new Date();
      date.setTime(date.getTime()+(days*24*60*60*1000));
      var expires = "; expires="+date.toGMTString();
    } else {
      var expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
  }

  function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i=0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0)==' ')
        c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0)
        return c.substring(nameEQ.length,c.length);
    }
    return null;
  }

  function eraseCookie(name) {
    createCookie(name, "", -1);
  }

  exports.login = login;
  exports.loginStatus = loginStatus;
  exports.logout = logout;

})(window.WSGIBrowserID = {});
