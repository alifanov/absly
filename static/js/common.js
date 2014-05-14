$(function(){
    $(".remove-news-btn").click(function(){
        var _this = $(this);
        $.ajax({
            type: 'GET',
            url: '/events/delete/' + $(this).attr('rel') + '/',
            success: function(){
                _this.parents('.events-item').slideUp();
            }
        });
        return false;
    });

//    var r = Raphael();
    var r = Raphael('graphics', 640, 480);
// Creates pie chart at with center at 320, 200,
// radius 100 and data: [55, 20, 13, 32, 5, 1, 2]
    r.piechart(320, 240, 100, [55, 20, 13, 32, 5, 1, 2]);});