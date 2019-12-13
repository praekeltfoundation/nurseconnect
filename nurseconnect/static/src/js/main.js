'use strict';
(function() {
  var searchLink = document.getElementById('NavBar__search'),
    searchFormField = document.getElementById('search');
    searchLink.addEventListener('click', function() {
      searchFormField.focus();
    });

//SET COOKIE
  function createCookie(name, value, days) {
  var expires;
  if(days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toGMTString();
  } else { expires = ""; }
      document.cookie = name + "=" + value + expires + "; path=/";
  }

  //READ COOKIE - WHEN USER FIRST ARRIVES
  function readCookie(c_name) {
  var value = "; " + document.cookie;
  var parts = value.split(";" + c_name + "=");
  if(parts.length == 2)
      return parts.pop().split(";").shift();
  }

  //SET COOKIE VALUE
  createCookie("banner_image", 1 , 30);
  var get_cookieValue = readCookie("banner_image")
})();
