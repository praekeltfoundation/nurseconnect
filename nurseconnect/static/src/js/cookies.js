'use strict';
  (function() {
    //GET COOKIE
    //RECTIFY COOKIES IMPLEMENTATION
    function getCookie(cname) {
      var name = cname + "=",
          ca = document.cookie.split(';'),i,c,
          ca_length = ca.length;
      for (i = 0; i < ca_length; i += 1) {
          c = ca[i];
          while (c.charAt(0) === ' ') {
              c = c.substring(1);
          }
          if (c.indexOf(name) !== -1) {
              return c.substring(name.length, c.length);
          }
      }
      return "";
      }
      //SET COOKIE
      function setCookie(name, value, days) {
        var expires;
        if(days) {
          var date = new Date();
          date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
          expires = "; expires=" + date.toGMTString();
        } else {expires = "";}
        document.cookie = name + "=" + value + expires + "; path=/";
      }
      setCookie("banner_version", 1, 30);

    //DELETE COOKIE
    function delete_cookie(name) {
      document.cookie = name + '=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }

    if (performance.navigation.type == 1 && window.location.pathname == "/") {
      delete_cookie("banner_version");
      setCookie("banner_version", 2, 30);
    }
    var readCookieByValue = getCookie("banner_version");
      if(readCookieByValue == 1) {
        var imagePath = "{% spaceless %}{{banner_image}}{% endspaceless %}";
      } else {
        var imagePath = "{% spaceless %}{{banner_image_secondary}}{% endspaceless %}";
      }
  })();
