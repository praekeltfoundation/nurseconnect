'use strict';
/**
* DJANGO
* Add additional banner image field - get field-tag into a variables as a cookie value?
*
*/
(function() {

  var searchLink = document.getElementById('static-menu__search'),
      searchFormField = document.getElementById('search-query');
      searchLink.addEventListener('click', function() {
        searchFormField.focus();
        console.log('Search activated...');
      });

  //SET COOKIE
  function createCookie(name, value, days) {
    var expires;
    if(days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toGMTString();
    } else {
      expires = "";
    }
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
  console.log("Same here",get_cookieValue);
})();
