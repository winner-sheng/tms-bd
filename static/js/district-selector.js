/**
* Created by winsom on 2016/6/29.
*/
//depends on css
(function($) {
    var tmpl = [
//'<span class="city-picker-span open focus">',
//'<span class="placeholder" style="display: inline;">请选择省份</span>',
//'<div class="arrow"></div> ',
//'</span>',
'<div id="distpicker" class="city-picker-dropdown">',
'<input type="hidden" id="selectedAreas" name="selectedAreas"/> ',
'<div class="city-select-wrap">',
'<!--<div class="city-select-tab">',
'<a class="active" data-count="province">省份</a> ',
'<a data-count="city">城市</a> ',
'<a data-count="district">区县</a>',
'</div>-->',
'<div class="city-select-content">',
'<div class="city-select province" data-count="province" style="display: block;">',
'<dl class="clearfix">',
'<dt> ',
'A-G',
'</dt>',
'<dd> ',
'<a title="安徽">安徽</a>',
'<a title="北京">北京</a>',
'<a title="重庆">重庆</a>',
'<a title="福建">福建</a>',
'<a title="甘肃">甘肃</a>',
'<a title="广东">广东</a>',
'<a title="广西">广西</a>',
'<a title="贵州">贵州</a>',
'</dd>',
'</dl>',
'<dl class="clearfix">',
'<dt> ',
'H-K',
'</dt>',
'<dd> ',
'<a title="海南">海南</a>',
'<a title="河北">河北</a>',
'<a title="黑龙江">黑龙江</a>',
'<a title="河南">河南</a>',
'<a title="湖北">湖北</a>',
'<a title="湖南">湖南</a>',
'<a title="江苏">江苏</a>',
'<a title="江西">江西</a>',
'<a title="吉林">吉林</a>',
'</dd>',
'</dl>',
'<dl class="clearfix">',
'<dt> ',
'L-S',
'</dt>',
'<dd> ',
'<a title="辽宁">辽宁</a>',
'<a title="内蒙古">内蒙古</a>',
'<a title="宁夏">宁夏</a>',
'<a title="青海">青海</a>',
'<a title="山东">山东</a>',
'<a title="上海">上海</a>',
'<a title="山西">山西</a>',
'<a title="陕西">陕西</a>',
'<a title="四川">四川</a>',
'</dd>',
'</dl>',
'<dl class="clearfix">',
'<dt> ',
'T-Z',
'</dt>',
'<dd> ',
'<a title="天津">天津</a>',
'<a title="新疆">新疆</a>',
'<a title="西藏">西藏</a>',
'<a title="云南">云南</a>',
'<a title="浙江">浙江</a>',
'</dd ',
'</dl>',
'</div> ',
'<!-- ',
'<div class="city-select city" data-count="city" style="display: none;"> ',
'<dl class="clearfix">',
'<dd></dd>',
'</dl>',
'</div> ',
'<div class="city-select district" data-count="district" style="display: none;">',
'<dl class="clearfix">',
'<dd></dd>',
'</dl>',
'</div>-->',
'<div class="form-group action">',
'<button class="btn btn-warning" id="reset" type="button">重置</button>',
'<button class="btn btn-danger" id="confirm" type="button">确定</button> ',
'</div>',
'</div>',
'</div>',
'</div>'].join('');
    function Selector(){
        var $selector = this;
        this.elem = null;
        this.selector = $("#distpicker");
        this.set = function (selectedAreas) {
            if (['INPUT', 'SELECT', 'TEXTAREA'].indexOf(this.elem[0].tagName) != -1) {
                this.elem.val(selectedAreas);
            } else {
                this.elem.text(selectedAreas || '请选择省份');
            }
        };
        if (this.selector.length == 0) {
            //initialize
            $(tmpl).appendTo($('body'));
            this.selector = $("#distpicker");
            $(".city-select").on('click', 'a', function () {
                $(this).toggleClass('active');
            });
            $("#confirm").click(function () {
                var selected = $(".city-select a.active");
                var areas = [];
                for (var i = 0; i < selected.length; i++) {
                    areas.push($(selected[i]).text());
                }
                var selectedAreas = areas.join(',');
                $selector.set(selectedAreas);
                $(".city-picker-dropdown").hide();
            });
            $("#reset").click(function () {
                $selector.set('');
                $(".city-select a.active").removeClass('active');
            });
            $(document).click(function(e){
                if ($("#distpicker").is(":visible") && $(e.target).parents("#distpicker").length == 0){
                    $("#distpicker").hide();
                }
            });
        }
        this.bindSelector = function(elem) {
            $(elem).click(function (e) {
                if($selector.elem && $selector.elem[0] != this && $("#distpicker").is(":visible")){
                    $("#distpicker").hide();
                }
                $selector.elem = $(this);
                $(this).toggleClass('open');
                var pos = $(this).offset();
                if ($("#distpicker").not(":visible")) {
                    $(".city-select a.active").removeClass('active');
                    var text = '';
                    if (['INPUT', 'SELECT', 'TEXTAREA'].indexOf(this.tagName) != -1){
                        text = $(this).val();
                    }else{
                        text = $(this).text();
                    }
                    if (text) {
                        var areas = text.split(',');
                        for (var i = 0; i < areas.length; i++) {
                            $(".city-select a[title=" + areas[i] + "]").toggleClass('active', true);
                        }
                    }
                }
                $("#distpicker").toggle().css({"left": pos.left, "top": pos.top + 4 + $(this).innerHeight()});
                e.stopPropagation();
            });
        }
    }
    var selector = null;
    $.fn.extend({"district_select": function(){
        selector = selector || new Selector();
        selector.bindSelector($(this));
    }});
}(jQuery || django.jQuery));