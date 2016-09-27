'use strict';

!function() {
    var MenuAnchor = document.querySelector('[data-enhanced-nav]').children[0];
    var FancyNav = document.getElementById('nav-enhanced');
    var FancyNavToggle = document.querySelector('.FancyNav-toggle');
    var MenuFragment;

    // Initialise the nav.
    var navInit = function() {
        // Prevent default redirect behaviour
        MenuAnchor.addEventListener('click', function(e) {
            e.preventDefault();

            FancyNav.classList.toggle('is-open');
        });

        FancyNavToggle.addEventListener('click', function(e) {
            e.preventDefault();

            FancyNav.classList.toggle('is-open');
        });

        MenuFragment = FancyNav.children[1];

        console.log(MenuFragment);

        MenuFragment.classList.remove('Menu--highContrast');
        MenuFragment.classList.add('Menu--centeredItems');
    }

    // Fetch the #site-nav element from /menu/, and inject it into #nav-enhanced. Pretty straight forward stuff.
    injectHtmlFragment('/menu/', '#site-nav', FancyNav, navInit);
}();

var fancyNav = (function () {
    // Private
    // -------

    // Public
    // -------
    return {

    }
})();
