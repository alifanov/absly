angular.module('CanvasAppServices', ['ngResource']).
    factory('Block', function($resource){
        return $resource('/api/canvas/:id/', {}, {
            query: {method: 'GET', params: {}, isArray: true}
        });
    }).
    factory('Element', function($resource){
        return $resource('/api/canvas/item/:id/', {}, {
            query: {method: 'GET', params: {}, isArray: true}
        });
    });
var app = angular.module('canvasapp', ['CanvasAppServices']);
app.controller('customerSegmentsCtrl', ['$scope', 'Block', 'Element', '$http', function ($scope, Block, Element, $http){

    $scope.editFlag = false;

    $scope.addElementForm = function(){
        $scope.editFlag = false;
        $("#add-element-modal-id").modal('show');
        $scope.newElement = angular.copy($scope.newElement);
        $scope.newElement.segment = $scope.segments.items[0];
        $scope.newElement.params = {};
        $scope.newElement.name = '';
        $scope.newElement.level = 0;
        angular.forEach($scope.activeBlock.questions, function(q, index){
            $scope.newElement.params[q.q] = '';
        });
        return false;
    };

    $scope.activities = null;
    $scope.costs = null;
    $scope.resources = null;
    $scope.channels = null;
    $scope.revenuestreams = null;
    $scope.relationship = null;
    $scope.propositions = null;
    $scope.partners = null;
    $scope.segments = null;

    $scope.activeSegment = null;

    $http({method: "GET", url: '/segments/json/'}).success(function(data, status, header, config){
        $scope.segments = data;
            $scope.newElement = {
            segment: $scope.segments.items[0],
            level: 0,
            name: ''
        };
    });
    $http({method: "GET", url: '/partners/json/'}).success(function(data, status, header, config){
        $scope.partners = data;
        $scope.initSegments($scope.partners.items);
    });
    $http({method: "GET", url: '/values/json/'}).success(function(data, status, header, config){
        $scope.propositions = data;
        $scope.initSegments($scope.propositions.items);
    });
    $http({method: "GET", url: '/activities/json/'}).success(function(data, status, header, config){
        $scope.activities = data;
        $scope.initSegments($scope.activities.items);
    });

    $http({method: "GET", url: '/costs/json/'}).success(function(data, status, header, config){
        $scope.costs = data;
        $scope.initSegments($scope.costs.items);
    });

    $http({method: "GET", url: '/resources/json/'}).success(function(data, status, header, config){
        $scope.resources = data;
        $scope.initSegments($scope.resources.items);
    });

    $http({method: "GET", url: '/channels/json/'}).success(function(data, status, header, config){
        $scope.channels = data;
        $scope.initSegments($scope.channels.items);
    });

    $http({method: "GET", url: '/relations/json/'}).success(function(data, status, header, config){
        $scope.relationship = data;
        $scope.initSegments($scope.relationship.items);
    });

    $http({method: "GET", url: '/revenue/json/'}).success(function(data, status, header, config){
        $scope.revenuestreams = data;
        $scope.initSegments($scope.revenuestreams.items);
    });

    $scope.initSegments = function(items){
        angular.forEach(items, function(v, i){
            angular.forEach($scope.segments.items, function(vv, ii){
                if(v.segment.name == vv.name){
                    v.segment = vv;
                }
            });
        });
    };

    $scope.activeBlock = $scope.segments;

    $scope.isSegment = function(){
        return $scope.activeBlock == $scope.segments;
    };

    $scope.setActiveSegment = function(s){
        if(s == $scope.activeSegment) $scope.activeSegment = null;
        else{
            $scope.activeSegment = s;
        }
        return false;
    };

    $scope.searchActiveSegment = function(el){
        if(!$scope.activeSegment) return true;
        if($scope.activeSegment == el.segment) return true;
        else return false;
    };

    $scope.activeSegmentClass = function(s, className){
        if (s == $scope.activeSegment) return className;
        return "";
    };

    $scope.testf = function(){
        console.log('test');
    };

    $scope.setActiveBlock = function(element){
        $scope.activeBlock = element;
    };

    $scope.saveDataToServer = function(){
        var data = [
            $scope.segments,
            $scope.propositions,
            $scope.costs,
            $scope.partners,
            $scope.resources,
            $scope.channels,
            $scope.relationship,
            $scope.activities,
            $scope.revenuestreams
        ];
        $.ajax({
            type: "POST",
            url: '/parse/json/',
            data: {
                'data': angular.toJson(data)
            }
        });
    };

    $scope.addNewElement = function(){
        if(!$scope.editFlag){
            var addedElement = angular.copy($scope.newElement);
            addedElement.segment = $scope.newElement.segment;
            $scope.activeBlock.items.push(addedElement);
            $scope.newElement.name = '';
        }
        $("#add-element-modal-id").modal('hide');
        $scope.saveDataToServer();
    };

    $scope.remove=function(item){
        var index=$scope.activeBlock.items.indexOf(item);
        $scope.activeBlock.deleted = item.pk;
        if(index != -1){
            $scope.activeBlock.items.splice(index,1);
        }
        $("#add-element-modal-id").modal('hide');
        $scope.saveDataToServer();
    };

    /* редактируем существующий элемент и ставим флаг что редактируем а не создаем заново */
    $scope.editElement = function(item){
        $scope.editFlag = true;
        $scope.newElement = item;
        $("#add-element-modal-id").modal('show');
    };
    $scope.setLevel = function(item, v){
        if(v != 0)
        {
            $scope.activeElement = item;
            $scope.activeLevel = v;
            console.log($scope.activeElement.level, v);
            $("#change-level-id").modal('show');
        }
    };
    $scope.upgradeLevelSave = function(){
        $scope.activeElement.level = $scope.activeLevel;
        $("#change-level-id").modal('hide');
        $scope.saveDataToServer();
    };
    $scope.getLevelClass = function(item, v){
        if(v <= item.level) return 'done';
        return '';
    }
}]);

$(function(){

    $(".ga-funnel-page select").change(function(){
        if($(this).val() != ''){
            $(this).parents('tr').find('.ga-funnel-events').addClass('hidden');
        }
        else{
            $(this).parents('tr').find('.ga-funnel-events').removeClass('hidden');
        }
    });

    $(".ga-funnel-events-category select").change(function(){
        if($(this).val() != ''){
            $(this).parents('tr').find('.ga-funnel-page').addClass('hidden');
        }
        else{
            $(this).parents('tr').find('.ga-funnel-page').removeClass('hidden');
        }
    });

    $("#date_range").change(function(){
        $.ajax({
            type: "POST",
            url: '/ga/config/funnel/',
            data: $("#date_range_form").serializeArray()
        });
        return false;
    });

    if($("#date_range").length){
        $("#date_range").change();
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