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

    $scope.addElementForm = function(){
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

    $scope.activities = {
        name: 'Key Activities',
        items: [],
        questions: [
            {
                q: 'Какой процесс создает основную ценность ?',
                ans: [
                    'личные продажи',
                    'разработка платформы',
                    'отношения с клиентами',
                    'разработка новшеств',
                    'исследования',
                    'маркетинг'
                ]
            }
        ]
    };
    $scope.costs = {
        name: 'Cost Structure',
        items: [],
        questions: [
            {
                q: 'КАКИЕ ВАШИ ОСНОВНЫЕ ЗАТРАТЫ?',
                ans: [
                    'исследования и разработки',
                    'прямые продажи',
                    'плата партнерам и поставщикам',
                    'затраты на транзакцию',
                    'производство продукции',
                    'материалы и оборудование',
                    'маркетинг',
                    'обслуживание и поддержка'
                ]
            },
            {
                q: 'ТИПЫ ЗАТРАТ',
                ans: [
                    'постоянные',
                    'переменные'
                ]
            }
        ]
    };
    $scope.resources = {
        name: 'Key Resources',
        items: []
    };
    $scope.channels = {
        name: 'Channels',
        items: []
    };
    $scope.revenuestreams = {
        name: 'Revenue Streams',
        items: []
    };
    $scope.relationship = {
        name: 'Customer Relationship',
        items: [],
        questions: [{
            q: 'Тип взаимоотношений с клиентами',
            ans: [
                'автоматизировано',
                'персонально',
                'комбинировано'
            ]
        }]
    };
    $scope.propositions = {
        name: 'Value Proposition',
        items: []
    };
    $scope.partners = {};

    $scope.activeSegment = null;

    $scope.segments = {
        name: 'Customer segments',
        questions: [
            {
                q: 'Кто ваши клиенты ?',
                ans: [
                    'бизнес',
                    'люди'
                ]
            }
        ],
        items: [
            {
                "name": 'Startups CEO',
                level: 0,
                levels: [
                    {
                        name: 'Гипотеза',
                        log: ''
                    },
                    {
                        name: 'Проверено фактами',
                        log: ''
                    },
                    {
                        name: 'Проверено действиями',
                        log: ''
                    },
                    {
                        name: 'Проверено деньгами',
                        log: ''
                    }
                ]
            },
            {
                "name": 'Venture Funds',
                level: 0,
                levels: [
                    {
                        name: 'Гипотеза',
                        log: ''
                    },
                    {
                        name: 'Проверено фактами',
                        log: ''
                    },
                    {
                        name: 'Проверено действиями',
                        log: ''
                    },
                    {
                        name: 'Проверено деньгами',
                        log: ''
                    }
                ]

            }
        ]
    };
    $http({method: "GET", url: '/segments/json/'}).success(function(data, status, header, config){
        $scope.segments = data;
    });
    $http({method: "GET", url: '/partners/json/'}).success(function(data, status, header, config){
        $scope.partners = data;
    });

    $scope.newElement = {
        segment: $scope.segments.items[0],
        level: 0,
        name: ''
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

    $scope.addNewElement = function(){
        var params = [];
        var addedElement = angular.copy($scope.newElement);
        addedElement.segment = $scope.newElement.segment;
        $scope.activeBlock.items.push(addedElement);
        $scope.newElement.name = '';
        $("#add-element-modal-id").modal('hide');
    };

    $scope.remove=function(item){
        var index=$scope.activeBlock.items.indexOf(item);
        if(index != -1){
            $scope.activeBlock.items.splice(index,1);
        }
    };
    $scope.editElement = function(item){
        $scope.newElement = item;
        $("#add-element-modal-id").modal('show');
    };
    $scope.setLevel = function(item, v){
        $scope.activeElement = item;
        $scope.activeElement.level = v;
        $("#change-level-id").modal('show');
    };
    $scope.upgradeLevelSave = function(){
        $("#change-level-id").modal('hide');
    };
    $scope.getLevelClass = function(item, v){
        if(v <= item.level) return 'done';
        return '';
    }
}]);

$(function(){
//    $("#add-element-modal-id form").submit(function(){
//        $.ajax({
//            type: 'POST',
//            url: '/canvas/element/add/',
//            data: $(this).serializeArray(),
//            success: function(resp){
//                $("#add-element-modal-id .alert-success").slideDown();
//                $("#add-element-modal-id form").slideUp();
//
//                setTimeout(function(){
//                    location.reload();
//                }, 1000);
//            }
//        });
//        return false;
//    });
//
    $(".add-canvas-block-item").mouseover(function(){
        var slug = $(this).attr('rel');
        $("#canvas-block-slug-id").val(slug);
    });

//    $(".add-canvas-block-item").click(function(){
//        alert('add modal window');
//        return false;
//    });

    $(document).on('click', '.definition-level a', function(){
        var _def_lvl = $(this).parents('.definition-level').eq(0);
        _def_lvl.find('a').removeClass('done');
        $(this).toggleClass('done');
        var lvl = parseInt($(this).attr('rel'));
        if ($(this).hasClass('done') && lvl > 0){
            _.each(_.range(0, lvl+1), function(a){
                _def_lvl.find('a[rel="' + a + '"]').addClass('done');
            })
        }
        return false;
    });

//    $(document).on('click', '.canvas-element-item-del', function(){
//        $(this).parents('li').remove();
//        return false;
//    });
//
//    $(".segments .canvas-block-items li a.canvas-element-item-link").click(function(){
//        $("td:not(.segments) .canvas-block-items li").show();
//        $(".segments .canvas-block-items li a").removeClass('icon-play');
//        if (!$(this).parents('li').eq(0).hasClass('active')){
//            $(this).parents('li').eq(0).addClass('active');
//            $(this).parents('li').eq(0).find('a.canvas-element-item-link').addClass('icon-play');
//            $("td:not(.segments) .canvas-block-items li:not(." + $(this).attr('rel') + ")").hide();
//        }
//        else
//        {
//            $(".segments .canvas-block-items li").removeClass('active');
//        }
//        return false;
//    });

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