// Helper function to AJAX in and inject an HTML fragment.
function injectHtmlFragment(fragmentUrl, htmlFragment, fragmentDestination, cb) {
    if (!window.XMLHttpRequest) return false;

    var request = new XMLHttpRequest();
    var parser = new DOMParser(); // Allows us to parse the response using standard DOM traversal.

    request.open('GET', fragmentUrl, true);
    request.responsetype = 'Content-type', 'text-html';

    request.onreadystatechange = function() {
        console.log('request loaded')
        if (request.readyState === 4 && request.status === 200) {
            var doc = parser.parseFromString(request.responseText, 'text/html');
            var fragmentSrc =  doc.querySelector(htmlFragment);

            fragmentDestination.appendChild(fragmentSrc);

            cb();
        }
    }

    request.send(null);
}
