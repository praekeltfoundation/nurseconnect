"use strict";function injectHtmlFragment(e,n,t,i){if(!window.XMLHttpRequest)return!1;var r=new XMLHttpRequest,a=new DOMParser;r.open("GET",e,!0),r.responsetype="Content-type",r.onreadystatechange=function(){if(4===r.readyState&&200===r.status){var e=a.parseFromString(r.responseText,"text/html").querySelector(n);t.appendChild(e),i()}},r.send(null)}!function(){function e(e,n,t){var i;if(t){var r=new Date;r.setTime(r.getTime()+24*t*60*60*1e3),i="; expires="+r.toGMTString()}else i="";document.cookie=e+"="+n+i+"; path=/"}var n;if(e("banner_version",1,30),1==performance.navigation.type&&"/"==window.location.pathname&&(n="banner_version",document.cookie=n+"=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;",e("banner_version",2,30)),1==function(e){var n,t,i=e+"=",r=document.cookie.split(";"),a=r.length;for(n=0;n<a;n+=1){for(t=r[n];" "===t.charAt(0);)t=t.substring(1);if(-1!==t.indexOf(i))return t.substring(i.length,t.length)}return""}("banner_version"));else;}(),function(){var e=document.getElementById("NavBar__search"),n=document.getElementById("search");e.addEventListener("click",function(){n.focus()}),function(e,n,t){var i;if(t){var r=new Date;r.setTime(r.getTime()+24*t*60*60*1e3),i="; expires="+r.toGMTString()}else i="";document.cookie=e+"="+n+i+"; path=/"}("banner_image",1,30);!function(e){var n=("; "+document.cookie).split(";"+e+"=");if(2==n.length)n.pop().split(";").shift()}("banner_image")}(),function(){var e=document.querySelector("[data-enhanced-nav]").children[0],n=document.getElementById("nav-enhanced"),t=document.querySelector(".FancyNav-toggle");injectHtmlFragment("/menu/","#site-nav",n,function(){e.addEventListener("click",function(e){e.preventDefault(),n.classList.toggle("is-open")}),t.addEventListener("click",function(e){e.preventDefault(),n.classList.toggle("is-open")}),n.children[1]})}();