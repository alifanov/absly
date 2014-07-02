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
        angular.forEach($scope.activeBlock.levels, function(q, index){
            q.log = "";
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
            levels: [
                {'name': 'Гипотеза', 'log': ''},
                {'name': 'Проверено фактами', 'log': ''},
                {'name': 'Проверено действиями', 'log': ''},
                {'name': 'Проверено деньгами', 'log': ''}
            ],
            name: ''
        };
    });
    $scope.updateBlock = function(block){
        if(block == $scope.partners){
            $http({method: "GET", url: '/partners/json/'}).success(function(data, status, header, config){
                $scope.partners = data;
                $scope.initSegments($scope.partners.items);
            });
        }
        if(block == $scope.values){
            $http({method: "GET", url: '/values/json/'}).success(function(data, status, header, config){
                $scope.propositions = data;
                $scope.initSegments($scope.propositions.items);
            });
        }
        if(block == $scope.activities){
            $http({method: "GET", url: '/activities/json/'}).success(function(data, status, header, config){
                $scope.activities = data;
                $scope.initSegments($scope.activities.items);
            });
        }
        if(block == $scope.costs){
            $http({method: "GET", url: '/costs/json/'}).success(function(data, status, header, config){
                $scope.costs = data;
                $scope.initSegments($scope.costs.items);
            });
        }
        if(block == $scope.resources){
            $http({method: "GET", url: '/resources/json/'}).success(function(data, status, header, config){
                $scope.resources = data;
                $scope.initSegments($scope.resources.items);
            });
        }
        if(block == $scope.channels){
            $http({method: "GET", url: '/channels/json/'}).success(function(data, status, header, config){
                $scope.channels = data;
                $scope.initSegments($scope.channels.items);
            });
        }
        if(block == $scope.relationship){
            $http({method: "GET", url: '/relations/json/'}).success(function(data, status, header, config){
                $scope.relationship = data;
                $scope.initSegments($scope.relationship.items);
            });
        }
        if(block == $scope.revenuestreams){
            $http({method: "GET", url: '/revenue/json/'}).success(function(data, status, header, config){
                $scope.revenuestreams = data;
                $scope.initSegments($scope.revenuestreams.items);
            });
        }
    };
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
