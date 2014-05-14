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

    var r = Raphael('graphics', 640, 480);
    к.barchart(0, 0, 620, 260, [76, 70, 67, 71, 69], {})ж
});