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

    var r = Raphael('graphics', 600, 300);
    r.piechart(70, 50, 50, [76, 70, 67, 71, 69]);

    var fin = function () {
            this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
        },
        fout = function () {
            this.flag.animate({opacity: 0}, 300, function () {this.remove();});
        };
    r.barchart(200, 20, 300, 100, [[55, 20, 13, 32, 5, 1, 2, 10]]).hover(fin, fout);
});