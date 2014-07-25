var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

function updateTopStatistics(){
    $.ajax({
        url: "/update/top/statistics/",
        type: "GET",
        success: function(resp){
            $("#main-stats .certainly-level .number").text(resp.certainly_level +'%');
            $("#main-stats .money .number").text('$'+resp.money_sum);
            $("#main-stats .money .date").text('Last '+resp.money_time + ' months');
        }
    });
}

function resort_steps(){
    var order_steps = $(".steps-recomendations .steps-wrapper .row").sort(function(a,b){
          var aName = parseInt($(a).attr('data-sort'));
          var bName = parseInt($(b).attr('data-sort'));
          return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
    });
    $(".steps-wrapper").html(order_steps);
    $(".steps-wrapper .row span.icon-sort-up").removeClass('icon-sort-up');
    var sort_order = {};
    $(".steps-wrapper .row").each(function(i,v){
        sort_order[$(v).attr('data-steps-group')] = $(v).attr('data-sort');
        if($(v).attr('data-sort') != '0'){
            $(v).find('a.sort-step span').addClass('icon-sort-up');
        }
    });
    $.ajax({
        type: "GET",
        url: '/steps/sort/',
        data: sort_order
    });
}


$(function(){
    $(".snapshot-edit form").submit(function(){
        $.ajax({
            type: "POST",
            url: "/summary/snapshot/",
            data: $(this).serializeArray(),
            success: function(r){
                $(".snapshot-alert").slideDown(500);
                $(".snapshot-edit").slideUp(500);
                $(".snapshot-alert span a").text(r.link);
                $(".snapshot-alert span a").attr('href',r.link);
            }
        });
        return false;
    });

    $(".es-snapshot-btn").click(function(){
        $(".snapshot-edit").slideDown(500);
        $(this).hide();
        return false;
    });

    $(".snapshot-edit .cancel-btn").click(function(){
        $(".snapshot-edit").slideUp(500);
        $(".es-snapshot-btn").show();
        return false;
    });


    if($('.reveal').length){
        $(".reveal").on('click', function(){
            if($("#id_password").attr('type') == 'password'){
                $("#id_password").attr('type', 'text');
            }
            else{
                $("#id_password").attr('type', 'password');
            }
            return false;
        })
    }

    $(document).on('click', ".del-summary-block", function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            url: "/summary/del/block/"+$(this).val() + "/",
            success: function(){
                $("#esb-"+_this.val()).remove();
                $("#add-summary-text-block-modal-id").modal('hide');
            }
        });
        return false;
    });

    if($("#summary-menu").length){
        var menu_pos = $("#summary-menu").offset().top;
        $(window).scroll(function(){
            if($(window).scrollTop() > menu_pos){
                $("#summary-menu").css({
                    'position': 'fixed',
                    top: '0'
                })
            }
            else{
                $("#summary-menu").css({
                    'position': 'static'
                })
            }
        });
    }

    resort_steps();

    $(document).on('click', '.sort-step', function(){
        var row = $(this).parent().parent();
        if(row.find('span.icon-sort-up')){
            if (row.prev('.row').length){
                row.attr('data-sort', parseInt(row.attr('data-sort'))-1);
                var n_row = row.prev('.row');
                n_row.attr('data-sort', parseInt(n_row.attr('data-sort'))+1);
                resort_steps();
            }
        }
        return false;
    });

    $(".create-customer-btn").click(function(){
        $(this).parent().find('.del-customer-btn').show();
        $(this).parent().find('.create-customer-btn').hide();
        var item = $(this).parents().find('.create-customer-group:hidden').eq(0);
        item.show();
        item.find('input').val('');
        item.find('select').select2('val', '');
        item.find('.del-customer-btn').show();
        item.find('.create-customer-btn').hide();
//        $(this).parents().find('.create-customer-group:hidden').eq(0).show();
//        $(this).hide();
        var item_last = $(this).parents().find('.create-customer-group:visible:last');
        item_last.find('.del-customer-btn').hide();
        if($('.create-customer-group:hidden').length){
            item_last.find('.create-customer-btn').show();
        }
        return false;
    });

    $(".del-customer-btn").click(function(){
        $(this).parent().parent().hide();
        $(this).hide();
        if($('.create-customer-group:hidden').length){
            $('.create-customer-group:visible:last').find('.create-customer-btn').show();
        }
        return false;
    });

    $("input:checkbox, input:radio").uniform();
    $(".select-customer").select2({
        placeholder: "Кто ваши потребители ?"
    });

    $("#id_is_first").click(function(){
        if($(this).is(":checked")){
            $(".addon-create-project").slideUp();
        }
        else{
            $(".addon-create-project").slideDown();
        }
    });

    $(".knob").knob({
        readOnly: true
    });

    $(window).scroll(function(){
		if ($(this).scrollTop() > 100) {
			$('.scrollToTop').fadeIn();
		} else {
			$('.scrollToTop').fadeOut();
		}
	});

	//Click event to scroll to top
	$('.scrollToTop').click(function(){
		$('html, body').animate({scrollTop : 0},800);
		return false;
	});

    $(".steps-wrapper .add-step").click(function(){
        $.ajax({
            type: "GET",
            url: "/steps/add/",
            data: {
                'dir': $(this).attr('value')
            },
            success: function(resp){
                $("#edit-recomendation-modal-id .modal-content").html(resp.data);
                $("#id_deadline").datepicker({
                    format: 'yyyy-mm-dd',
                    orientation: 'auto',
                    language: 'ru',
                    todayHighlight: true
                });
                $("#edit-recomendation-modal-id").modal('show');
                }
        });
        return false;
    });

    $(document).on('click', '.delete-log-btn', function(){
        if($("#id_delete_log").val() != ''){
            $.ajax({
                type: "GET",
                url: "/steps/del/"+$(this).val()+"/",
                data: {
                    'comment': $("#id_delete_log").val()
                },
                success: function(){
                    $("#edit-recomendation-modal-id").modal('hide');
                    location.reload();
                }
            });
        }
        return false;
    });

    $(document).on('click', '.step-delete', function(){
        $(".step-edit-form .modal-footer").hide();
        $(".step-edit-form .modal-body .row").slideUp();
        $(".step-edit-form .modal-body .step-delete-log").slideDown();
        return false;
    });

    $(document).on('click', '.done-log-btn', function(){
        if($("#id_done_log").val() != ''){
            $.ajax({
                type: "GET",
                url: "/steps/done/"+$(this).val()+"/",
                data: {
                    'comment': $("#id_done_log").val()
                },
                success: function(){
                    $("#edit-recomendation-modal-id").modal('hide');
                    location.reload();
                }
            });
        }
        return false;
    });

    $(document).on('click', '.step-done', function(){
        $(".step-edit-form .modal-footer").hide();
        $(".step-edit-form .modal-body .row").slideUp();
        $(".step-edit-form .modal-body .step-done-log").slideDown();
        return false;
    });
    $(document).on('click', '.step-save', function(){
        $.ajax({
            type: "POST",
            url: $("#step-edit-modal-form").attr('action'),
            data: $("#step-edit-modal-form").serializeArray(),
            success: function(){
                $("#edit-recomendation-modal-id").modal('hide');
                location.reload();
            }
        });
        return false;
    });

    $(document).on('click', ".step-edit-link", function(){
        $.ajax({
            type: "GET",
            url: "/steps/edit/"+$(this).attr('rel')+'/',
            success: function(resp){
                $("#edit-recomendation-modal-id .modal-content").html(resp.data);
                $("#id_deadline").datepicker({
                    format: 'yyyy-mm-dd',
                    todayHighlight: true,
                    language: 'ru'
                });
                $("#edit-recomendation-modal-id").modal('show');
                }
        });
        return false;
    });

    $(document).on('submit', '#step-view-modal-form', function(){
        $.ajax({
            url: $(this).attr('action'),
            type: "POST",
            data: $(this).serializeArray(),
            success:function(resp){
                $("#edit-recomendation-modal-id").modal('hide');
                location.reload();
            }
        });
        return false;
    });

    $(document).on('submit', '#recomendation-view-modal-form', function(){
        $.ajax({
            url: $(this).attr('action'),
            type: "POST",
            data: $(this).serializeArray(),
            success:function(resp){
                $("#edit-recomendation-modal-id").modal('hide');
                location.reload();
            }
        });
        return false;
    });

    $(document).on('click', ".recomendation-link", function(){
        $.ajax({
            url: "/steps/recomendation/",
            type: "GET",
            data: {
                'r': $(this).attr('rel')
            },
            success: function(resp){
                $("#edit-recomendation-modal-id .modal-content").html(resp.data);
                $("#edit-recomendation-modal-id").modal('show');
            }
        });
        return false;
    });

    $(document).on('submit', '#canvas-log-modal-form', function(){
        $.ajax({
            url: "/canvas/change/level/log/",
            type: "POST",
            data: $(this).serializeArray(),
            success: function(resp){
                $("#element-"+resp.pk).html($(resp.data).html());
                updateTopStatistics();
            }
        });
        $("#change-level-id").modal('hide');
        return false;
    });

    $(document).on('click', '.definition-level a', function(){
        $.ajax({
            url: "/canvas/change/level/log/",
            type: "GET",
            data: {
                'element': $(this).parent().parent().parent().parent().attr('id').split('-')[1],
                'new': $(this).attr('rel')
            },
            success: function(resp){
                $("#change-level-id .modal-content").html(resp.data);
                $("#change-level-id").modal('show');
            }
        });
        return false;
    });

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
                updateTopStatistics();
            }
        });
        location.reload();
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
            data: $("#ga-funnel-config-form").serializeArray(),
            success: function(){
                $(".alert-save-ga-config").show();
                setTimeout(function(){
                    $(".alert-save-ga-config").fadeOut(500);
                }, 3000)
            }
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
            data: $("#ga-funnel-config-form").serializeArray(),
            success: function(){
                $(".alert-save-ga-config").show();
                setTimeout(function(){
                    $(".alert-save-ga-config").fadeOut(500);
                }, 3000)
            }
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
            data: $("#ga-funnel-config-form").serializeArray(),
            success: function(){
                $(".alert-save-ga-config").show();
                setTimeout(function(){
                    $(".alert-save-ga-config").fadeOut(500);
                }, 3000)
            }
        });
    });

    $("#id_date_range").change(function(){
        $.ajax({
            type: "POST",
            url: '/ga/config/funnel/',
            data: $("#date_range_form").serializeArray(),
            success: function(){
                $(".alert-save-ga-config").show();
                setTimeout(function(){
                    $(".alert-save-ga-config").fadeOut(500);
                }, 3000)
            }
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
            data: $(".ga-config-profile-form").serializeArray(),
            success: function(){
                $(".alert-save-ga-config").show();
                setTimeout(function(){
                    $(".alert-save-ga-config").fadeOut(500);
                }, 3000)
            }
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
        var formData = new FormData($(this)[0]);
        $.ajax({
            type: "POST",
            url: $(this).attr('action'),
            data: formData,
            processData: false,
            contentType: false,
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
                $(".modal-title").html(resp.title);
            }
        })
    });


    $(".summary-add-ms").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            data: {
                'id': _this.val()
            },
            url: '/summary/ms/block/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
                $(".modal-title").text(resp.title);
            }
        })
    });
    $(".summary-add-ir").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            data: {
                'id': _this.val()
            },
            url: '/summary/ir/block/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
                $(".modal-title").text(resp.title);
            }
        })
    });
    $(".summary-add-cb").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            data: {
                'id': _this.val()
            },
            url: '/summary/cb/block/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
                $(".modal-title").text(resp.title);
            }
        })
    });
    $(".summary-add-angellist").click(function(){
        var _this = $(this);
        $.ajax({
            type: "GET",
            data: {
                'id': _this.val()
            },
            url: '/summary/angellist/block/',
            success: function(resp){
                $(".modal-form-body").html(resp.data);
                $(".modal-title").text(resp.title);
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
                $(".modal-title").text(resp.title);
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
                $(".modal-title").text(resp.title);
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
                $(".modal-title").text(resp.title);
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
                $(".modal-title").text(resp.title);
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