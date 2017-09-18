var URL_GET_TEMPLATE = "/tms-api/admin/get_express_template";
var URL_SET_TEMPLATE = "/tms-api/admin/set_express_template";
var URL_DEL_TEMPLATE = "/tms-api/admin/del_express_template";
var DEFAULT_SETTING = {
    "id": 0,
    "name": "新模板" + new Date().toLocaleDateString(),
    //"vendor": 0,
    "type": 0,
    //"shapeImg": 0,
    "template": {
        "width": 640,
        "height": 400,
        "padding": 0,
        "html": '',
        "idSeed": 1,
        "background": {"id": 0, "img": ""}  //url(/static/images/tmpl/sf.jpg)
    }
};
//TODO: may cause infinite clone loop, be cautious
function clone(obj){
    var newObj;
    if(!obj || typeof obj == 'string' || typeof obj == 'number' || typeof obj == 'boolean'){
        newObj = obj;
    }else if(obj instanceof Array){
        newObj = [];
        for(var i in obj){
            newObj[i] = clone(obj[i]);
        }
    }else if(obj instanceof Object){
        newObj = {};
        for(var p in obj){
            newObj[p] = clone(obj[p]);
        }
    }else{
        newObj = obj;
    }
    return newObj;
}

var Template = function (root, editable) {
    return {
        "rootElement": $(root),
        "editable": editable ? true : false,
        "currentItem": null,
        "data": DEFAULT_SETTING,
        "_initLabel": function(label){
            if (!this.editable){
                return;  // ignore if not editable
            }
            var me = this;
            label.children("img.imgClose").click(function(e){
                me.removeItem($(this).parent());
                e.stopPropagation();
            });
            label.click(function (e) {
                    //highlight the latest clicked one
                    me.markCurrentItem(this);
                })
                .draggable({"containment": "parent"})  //
                .resizable({"handles": "e,s,w,n,se", "helper": "ui-resizable-helper"});
        },
        //创建新标签
        "createLabel": function (field, text) {
            var me = this;
            var seed = me.data.template.idSeed;
            while (me.rootElement.find("#tmplLabel" + seed).length > 0) { //get a unique label id
                seed++;
            }
            me.data.template.idSeed = seed;
            var label = $("<div id='tmplLabel" + seed + "' class='fieldHolder' field='" +
                            field + "'>" + text + "<img class='imgClose' src='/static/images/no.png'></div>");
            this.addItem(label);
            this.editable && this._initLabel(label);
            return label;
        },
        "addItem": function (element) {
            element.appendTo(this.rootElement);
            this.editable && this.markCurrentItem(element);
        },
        "removeItem": function (element) {
            if (this.currentItem == element) {
                this.currentItem = null;
            }
            if (element) {
                element.remove();
            }
        },
        "markCurrentItem": function (item) {
            if (this.currentItem) {
                this.currentItem.removeClass("highlight");
            }
            this.currentItem = $(item).addClass("highlight");
            this.editable && $("#currentItem").text($(item).text());
        },
        "zoomOut": function () {
            if (this.currentItem) {
                this.currentItem.css("font-size", (parseInt(this.currentItem.css("font-size"), 10) - 1) + "px");
            }
        },
        "zoomIn": function () {
            if (this.currentItem) {
                this.currentItem.css("font-size", (parseInt(this.currentItem.css("font-size"), 10) + 1) + "px");
            }
        },
        "switchFont": function (type, value) {
            if (this.currentItem) {
                if (this.currentItem.css(type) == value) {
                    this.currentItem.css(type, "inherit");
                } else {
                    this.currentItem.css(type, value);
                }
            }
        },
        "setBackground": function(imgId, imgUrl){
            imgUrl = imgUrl ? imgUrl : DEFAULT_SETTING.template.background.img;
            if(imgId == "0"){
                this.rootElement.css("background", imgUrl);
            }else{
                this.rootElement.css("background", imgUrl);
            }
            this.data.template.background = {"id": imgId, "img": imgUrl};
        },
        "setWidth": function(width){
            var width = parseInt(width, 10);
            if(width < 100){
                alert("对不起，宽度设置无效！");
            }else{
                this.data.template.width = width;
                this.rootElement.css("width", width+"pt");
            }
        },
        "setHeight": function(height){
            var height = parseInt(height, 10);
            if(height < 100){
                alert("对不起，高度设置无效！");
            }else{
                this.data.template.height = height;
                this.rootElement.css("height", height+"pt");
            }
        },
        "getSetting": function () {
            if (this.editable) {
                //this.data.id = $("#tmplList").children("option:selected").val();
                this.data.name = $("#tmplName").val();
                this.data.type = $("#tmplIsPublic").is(":checked") ? "1" : "0";
                var labels = this.rootElement.children(".fieldHolder");
                //temporarily remove all special functionality
                var resizableOptions = labels.resizable("option");
                var draggableOptions = labels.draggable("option");
                labels.resizable("destroy").draggable("destroy");
                if (this.currentItem) {
                    this.currentItem.removeClass("highlight");
                }
                this.data.template.html = this.rootElement.html();
                this.markCurrentItem(this.currentItem);
                //get previous special functionality back
                labels.resizable(resizableOptions).draggable(draggableOptions);
            }
            return this.data;
        },
        "preview": function () {
            this.rootElement.printArea();
        },
        "copy": function(){
            this.data.id = "0";
            this.save();
        },
        "save": function () {
            var me = this;
            //var content = me.getSetting();
            var content = {"data": JSON.stringify(me.getSetting())};
            content['csrfmiddlewaretoken'] = csrf;
            $.post(
                URL_SET_TEMPLATE,
                content,
                function(data, error){
                    if(data.error){
                        alert(data.error);
                    }else{
                        alert("模板【" + data.name + "】保存成功！");
                        if(me.editable && me.data.id == '0') {  //it's create a new template
                            me.data.id = data.id;
                            var opt = $("<option value=" + data.id + "></option>");
                            opt.attr("tmplName", data.name);
                            opt.text(data.name);
                            $("#tmplList").append(opt);
                            opt.attr("selected", "selected");
                        }
                    }
                },
                "json"
            );
        },
        "delete": function () {
            //submit delete request to backend
            var me = this;
            if(parseInt(me.data.id, 10) == 0){
                alert("该模板尚未保存，不必删除！");
                return
            }
            if (confirm("确认要删除该模板吗？\n注意：该操作无法还原！")) {
                //var content = me.getSetting();
                $.get(
                    URL_DEL_TEMPLATE,
                    {'id': me.data.id},
                    function(data, error){
                        if(data.error){
                            alert(data.error);
                        }else{
                            me.editable && $("#tmplList option[value=" + me.data.id + "]").remove();
                            me.reset();
                            alert("模板【" + me.data.name + "】删除成功！");
                        }
                    },
                    "json"
                );
            }
        },
        "loadById": function(id) {
            var id = parseInt(id, 10);
            if (id < 1){
                alert("模板参数id无效！");
                return;
            }
            var me = this;
            $.get(URL_GET_TEMPLATE,
                    {"id": id},
                    function (data) {
                        if (!data || data.error || data.length == 0){
                            //TODO: no data found
                        } else {
                            var setting = data[0];
                            setting['template'] = JSON.parse(setting['template']);
                            me.load(setting);
                        }
                    },
                    "json"
            );
        },
        "load": function (setting) {
            if (!setting || !setting.template)
                return;
            var me = this;
            me.data = setting;
            var bg = setting.template.background ? setting.template.background : DEFAULT_SETTING.template.background;
            me.setBackground(bg.id, bg.img);
            me.rootElement.html(setting.template.html ? setting.template.html : DEFAULT_SETTING.template.html);
            var width = setting.template.width ? setting.template.width : DEFAULT_SETTING.template.width;
            var height = setting.template.height ? setting.template.height : DEFAULT_SETTING.template.height;
            me.rootElement.css("width", width + "pt");
            me.rootElement.css("height", height + "pt");
            if(me.editable) {
                $("#tmplName").val(setting.name ? setting.name : DEFAULT_SETTING.name);
                if (setting.type == "1") {
                    $("#tmplIsPublic").attr("checked", "checked");
                } else {
                    $("#tmplIsPublic").removeAttr("checked");
                }
                $("#tmplShapeImage").children("option[value=" + bg.id + "]").attr("selected", "selected");
                $("#tmplWidth").val(width);
                $("#tmplHeight").val(height);
                $("#tmplPadding").val(setting.template.padding ? setting.template.padding : DEFAULT_SETTING.template.padding);
                var labels = me.rootElement.children(".fieldHolder");
                this._initLabel(labels);
            }
        },
        "clear": function () {
            if (confirm("确认要清除模板上已有布局吗？\n注意：该操作无法还原！")) {
                this.rootElement.empty();
            }
        },
        "reset": function () {
            this.rootElement.empty();
            this.currentItem = null;
            this.load(clone(DEFAULT_SETTING));  //do not use DEFAULT_SETTING straightly
        }

    }
};
