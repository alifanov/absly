var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

$(function(){

    $(document).on('click', 'a.canvas-element-item-edit', function(){
        $.ajax({
            type: "GET",
            url:"/canvas/block/new/form/",
            data: {
                'element': $(this).attr('rel')
            },
            success: function(resp)
            {
                $("#add-element-modal-id .canvas-modal-body").html(resp.data);
            }
        });
        $("#add-element-modal-id").modal('show');
        return false;
    });

    var saveElement = function(){
        var d = $("#edit-canvas-element-form-id").serializeArray();
        if($(this).hasClass('del-btn')){
            d.push({
                name: 'delete',
                value: '1'
            });
        }
        $.ajax({
            type: "POST",
            url: "/canvas/block/new/form/",
            data: d,
            success: function(resp){
                if(resp.deleted){
                    $("#element-"+resp.deleted).remove();
                }
                if($("#edit-canvas-element-form-id .edit-btn").text() == 'Add'){
                    $("#block-"+resp.block).append(resp.data);
                }
                else{
                    $("#element-"+resp.pk).html($(resp.data).html());
                }
                $("#add-element-modal-id").modal('hide');
            }
        });
        return false;
    };

    $(document).on('submit', "#edit-canvas-element-form-id", saveElement);
    $(document).on('click', "#edit-canvas-element-form-id .del-btn", saveElement);

    $(document).on('click', "a.add-canvas-block-item", function(){
        $.ajax({
            type: "GET",
            url:"/canvas/block/new/form/",
            data: {
                'block': $(this).attr('rel')
            },
            success: function(resp)
            {
                $("#add-element-modal-id .canvas-modal-body").html(resp.data);
            }
        });
        $("#add-element-modal-id").modal('show');
        return false;
    });

    $(document).on("keypress", 'form#add-element-modal-id input[type="text"]', function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            e.preventDefault();
            return false;
        }
    });

    $("#id_user_sum").keyup(function(){
        delay(function(){
        $.ajax({
            url: '/ga/config/funnel/',
            type: "POST",
            data: $("#ga-funnel-config-form").serializeArray()
        });
        }, 1000);
    });

    $(".ga-funnel-page select").change(function(){
        if($(this).val() != ''){
            $(this).parents('tr').find('.ga-funnel-events').addClass('hidden');
        }
        else{
            $(this).parents('tr').find('.ga-funnel-events').removeClass('hidden');
        }
        $.ajax({
            url: '/ga/config/funnel/',
            type: "POST",
            data: $("#ga-funnel-config-form").serializeArray()
        });
    });

    $(".ga-funnel-events-category select").change(function(){
        if($(this).val() != ''){
            $(this).parents('tr').find('.ga-funnel-page').addClass('hidden');
        }
        else{
            $(this).parents('tr').find('.ga-funnel-page').removeClass('hidden');
        }
        $.ajax({
            url: '/ga/config/funnel/',
            type: "POST",
            data: $("#ga-funnel-config-form").serializeArray()
        });
    });

    $("#id_date_range").change(function(){
        $.ajax({
            type: "POST",
            url: '/ga/config/funnel/',
            data: $("#date_range_form").serializeArray()
        });
        return false;
    });

    if($("#id_date_range").length){
        $("#id_date_range").change();
    }

    $("#ga_account").change(function(){
        $.ajax({
            type: "POST",
            url: '/ga/config/account/',
            data: $(".ga-config-profile-form").serializeArray(),
            success: function(resp){
                $(".ga-webprops").html(resp.data);
                $("#ga_webprops").change();
                $(".ga-profile").html('');
            }
        });
    });

    if($("#ga_account").length){
        $("#ga_account").change();
    }


    $(document).on('change', '#ga_profile', function(){
        $.ajax({
            type: "POST",
            url: '/ga/config/profile/',
            data: $(".ga-config-profile-form").serializeArray()
        });
    });

    $(document).on('change', '#ga_webprops', function(){
        $.ajax({
            type: "POST",
            url: '/ga/config/webprops/',
            data: $(".ga-config-profile-form").serializeArray(),
            success: function(resp){
                $(".ga-profile").html(resp.data);
                $("#ga_profile").change();
            }
        });
    });

    $(document).on('submit', "form.summary-block-add", function(){
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: $(this).serializeArray(),
            success: function(){
                location.reload()
            }
        });
        return false;
    });

    $(".es-edit-block a").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            url: '/summary/update/block/'+_this.attr('rel') + '/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
            }
        })
    });


    $(".summary-add-linkedin").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            data: {
                'id': _this.val()
            },
            url: '/summary/linkedin/block/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
            }
        })
    });
    $(".summary-add-text").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            data: {
                'id': _this.val()
            },
            url: '/summary/text/block/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
            }
        })
    });
    $(".summary-add-image").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            url: '/summary/image/block/',
            data: {
                'id': _this.val()
            },
            success: function(resp){
                $(".modal-form-body").html(resp.data);
            }
        })
    });
    $(".summary-add-link").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            url: '/summary/link/block/',
            data: {
                'id': _this.val()
            },
            success: function(resp){
                $(".modal-form-body").html(resp.data);
            }
        })
    });

    $("#ga_account").change(function(){
        $("#ga_profile").remove();
        $("#ga_webprop").remove();
    });
    $("#ga_webprop").change(function(){
        $("#ga_profile").remove();
    });

    $(".add-canvas-block-item").mouseover(function(){
        var slug = $(this).attr('rel');
        $("#canvas-block-slug-id").val(slug);
    });

    $(document).on('click', '.definition-level a', function(){
        return false;
    });

    $(".es-item-text-view").click(function(){
        var tarea = $(this).parents('.es-item-text').eq(0).find('textarea');
        tarea.text($(this).text());
        tarea.show();
        tarea.focus();
        $(this).parents('.es-item').eq(0).find('.es-item-btns button').show();
        $(this).hide();
    });

    $('.es-item-btns button').click(function(){
        var titem = $(this).parents('.es-item').eq(0);
        var titemtext = $(this).parents('.es-item').find('.es-item-text').eq(0);
        var tarea = $(this).parents('.es-item').find('.es-item-text-area');
        var tview = $(this).parents('.es-item').find('.es-item-text-view');
        tview.text(tarea.val());
        if(tarea.val() == ''){
            titem.find('h4').removeClass('text-success');
            titem.find('h4').addClass('text-danger');
            titemtext.removeClass('done');
            titemtext.addClass('empty');
        }
        else{
            titem.find('h4').removeClass('text-danger');
            titem.find('h4').addClass('text-success');
            titemtext.removeClass('empty');
            titemtext.addClass('done');

            var tform = titem.find('form').eq(0);
            $.ajax({
                type: "POST",
                url: tform.attr('action'),
                data: tform.serializeArray()
            });
        }
        tarea.hide();
        tview.show();
        $(this).hide();
    });

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

    if($("#graphics").length)
    {
        var r = Raphael('graphics', 400, 250);
        r.piechart(70, 50, 50, [76, 70, 67, 71, 69]);
        r.piechart(70, 170, 50, [70, 67, 71, 69, 76, 76, 76]);

        var fin = function () {
                this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
            },
            fout = function () {
                this.flag.animate({opacity: 0}, 300, function () {this.remove();});
            };
        r.barchart(200, 20, 200, 100, [[55, 20, 13, 32, 5, 1, 2, 10]]).hover(fin, fout);
        r.barchart(200, 140, 200, 100, [[32, 5, 1, 2, 10, 55, 20, 13, 55, 20, 13, 55, 20, 13]]).hover(fin, fout);
    }

    if($("#charts").length)
    {
        var r2 = Raphael('charts', 200, 50);

        r2.barchart(0, 0, 200, 70, [[10, 20, 30, 2, 20, 50]]);
    }
    if($("#spec-chart-0").length)
    {
        var r0 = Raphael('spec-chart-0', 100, 50);
        var r1 = Raphael('spec-chart-1', 100, 50);
        var r2 = Raphael('spec-chart-2', 100, 50);

        r0.barchart(0, 0, 100, 70, [[50, 20, 30, 2, 20, 50]]);
        r1.barchart(0, 0, 100, 70, [[10, 20, 10, 2, 20, 50]]);
        r2.barchart(0, 0, 100, 70, [[40, 20, 40, 49, 20, 50]]);
    }
    if($("#metrics-chart-1").length)
    {
        var r0 = Raphael('metrics-chart-1', 100, 100);
        var r1 = Raphael('metrics-chart-2', 100, 100);
        var r2 = Raphael('metrics-chart-3', 100, 100);
        var r3 = Raphael('metrics-chart-4', 100, 100);

        r0.barchart(0, 0, 100, 100, [[50, 20, 30, 2, 20, 50]]);
        r1.barchart(0, 0, 100, 100, [[10, 20, 10, 2, 20, 50]]);
        r2.barchart(0, 0, 100, 100, [[40, 20, 40, 49, 20, 50]]);
        r3.barchart(0, 0, 100, 100, [[50, 1, 30, 2, 20, 74]]);
    }

    $(".steps-done-item a").click(function(){
        $(this).parents('.steps-done-item').find('.steps-done-item-desc').slideToggle();
        return false;
    });
});