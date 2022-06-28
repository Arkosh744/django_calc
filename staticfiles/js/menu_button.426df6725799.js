jQuery(document).ready(function () {

    $('.dismiss, .overlay').on('click', function () {
        $('.sidebar').removeClass('active');
        $('.overlay').removeClass('active');
        $('.open-menu').show()
        $('.dismiss').hide()
    });

    $('.open-menu').on('click', function (e) {
        e.preventDefault();
        $('.sidebar').addClass('active');
        $('.overlay').addClass('active');
        $('.open-menu').hide()
        $('.dismiss').show()
        // close opened sub-menus
        $('.collapse.show').toggleClass('show');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

    $(window).resize(function() {
        // This will fire each time the window is resized:
        if($(window).width() <= 1024) {
            // if larger or equal
            $('.header-bar-menu a div').hide();
        } else {
            // if smaller
            $('.header-bar-menu a div').show();
        }
    }).resize(); // This will simulate a resize to trigger the initial run.
});
