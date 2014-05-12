$(document).ready(function(){
    $(".bookmarks-link").click(function(){
        $.ajax({
            type: 'GET',
            url: '/action/bookmarks/add/' + $(this).attr('rel') + '/'
        });
        return false;
    });

    $(".like-link").click(function(){
        var _this = $(this);
        $.ajax({
            type: 'GET',
            url: '/action/like/' + $(this).attr('rel') + '/',
            success: function(resp){
                _this.text(resp);
            }
        });
        return false;
    });

    $(".dislike-link").click(function(){
        var _this = $(this);
        $.ajax({
            type: 'GET',
            url: '/action/dislike/' + $(this).attr('rel') + '/',
            success: function(resp){
                _this.text(resp);
            }
        });
        return false;
    });

    $(".recals-label").click(function(){
        $(".recals-list").slideToggle();
        if ($(".recals-label span").hasClass('glyphicon-chevron-down')){
            $(".recals-label span").removeClass('glyphicon-chevron-down');
            $(".recals-label span").addClass('glyphicon-chevron-up');
        }
        else{
            $(".recals-label span").removeClass('glyphicon-chevron-up');
            $(".recals-label span").addClass('glyphicon-chevron-down');
        }
    });

    $(".profile-popover-link").popover({
        html: true,
        content: $(".profile-popover").html(),
        placement: 'bottom'
    });
    $(".login-popover-link").popover({
        html: true,
        content: $(".login-popover").html(),
        placement: 'bottom'
    });

    $(".login-popover-link").on('shown.bs.popover', function(){
        $("#login-popover-form-id").submit(function(){
            $(".login-error-msgs").text('');
            $.ajax({
                type:"POST",
                url: $(this).attr('action'),
                data: $(this).serializeArray(),
                success: function(response){
                    window.location = response;
                },
                error: function(xhr, ajaxOptions, thrownError){
                    $(".login-error-msgs").text('Ошибка: проверьте правильность логина и пароля');
                }
            });
            return false;
        });
    });

    if($("#map").length)
    {
        $(".maps-panel").css({
            'height': document.documentElement.clientHeight-50 + 'px'
        });
        $(".wrapper-map .container").css({
            'margin-top': '-' + (document.documentElement.clientHeight-50) + 'px'
        });
        $("#map").css({
            'height': document.documentElement.clientHeight - 50 + 'px'
        });

        map = new GMaps({
            div: '#map',
            zoom: 16,
            lat: -12.043333,
            lng: -77.028333,
            scrollwheel: false
        });
        map.addMarker({
            lat: 59.933129,
            lng: 30.348566,
            title: 'Бар "Синяя лошадь"'
        });
        map.addMarker({
            lat: 59.934806,
            lng: 30.333846,
            title: 'Бар "Фиолетовый кабан"'
        });
        GMaps.geolocate({
            success: function(position) {
                map.setCenter(position.coords.latitude, position.coords.longitude);
            },
            error: function(error) {
                alert('Geolocation failed: '+error.message);
            },
            not_supported: function() {
                alert("Your browser does not support geolocation");
            }
        });
    }

//    $('#company-tabs a').click(function (e) {
//        e.preventDefault();
//        $(this).tab('show');
//    })
});

$(window).load(function(){
    $('.bxslider').bxSlider({
        minSlides: 4,
        maxSlides: 4,
        slideWidth: 208,
        slideMargin: 10,
        adaptiveHeight: true,
        pager: false
    });

    $(".bxslider-inner").bxSlider({
        minSlides: 3,
        maxSlides: 3,
        slideWidth: 47,
        slideMargin:10,
        pager: false
    });

    $(".company-actions-slider").bxSlider({
        minSlides:1,
        maxSlides:1,
        slideWidth:800,
        slideMargin:10,
        pager: false,
        adaptiveHeight: true,
        mode: 'fade'
    });

})