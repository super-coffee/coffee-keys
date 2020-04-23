// urlParams
const urlParams = new URLSearchParams(window.location.search);
let msg = urlParams.get('msg');
if (msg != null) {
    layui.use('layer', function () {
        var layermsg = layui.layer;
        layermsg.msg(msg);
    });
};
// vue.js
var pem2text = new Vue({
    el: '#pem2text',
    data: {
        content: null
    }
});
var checkPassword = new Vue({
    el: '#checkPassword',
    data: {
        password: "",
        repeat_password: ""
    },
    computed: {
        // 计算属性的 getter
        isEqual: function () {
            // `this` 指向 vm 实例
            return this.password == this.repeat_password;
        }
    }
});

// 读取 PEM
layui.use('upload', function () {
    var upload = layui.upload;
    upload.render({
        elem: '#pem' //绑定元素
        , accept: 'file'
        , url: 'https://httpbin.org/post'  // fake api
        , exts: 'txt|pem|rsa'
        , auto: false
        , choose: function (obj) {
            //预读本地文件示例，不支持ie8
            obj.preview(function (_index, _file, result) {
                base64edContent = result.replace("data:application/octet-stream;base64,", "");
                content = window.atob(base64edContent);
                pem2text.content = content;
            });
        }
    });
});

// 监听表单提交事件
layui.use('form', function () {
    var form = layui.form;
    form.on('submit(form)', function (data) {
        // 读取表单的信息
        var data = form.val("form");
        var doRecaptcha = data["g-recaptcha-response"] == "" ? false : true;  // 三目
        var hasRecaptcha = "g-recaptcha-response" in data;
        var canSubmit = false;
        // 判断是否可提交
        if (!doRecaptcha || !hasRecaptcha) {
            layui.use('layer', function () {
                layer.tips('请完成 reCAPTCHA 人机身份验证', '#submit', {
                    tips: 3,  // 下
                    tipsMore: true
                });
            });
        };
        if (!checkPassword.isEqual) {
            layui.use('layer', function () {
                layer.tips('密码不一致', '#repeat-password', {
                    tips: 3,  // 下
                    tipsMore: true
                });
            });
        };
        if (doRecaptcha && checkPassword.isEqual && hasRecaptcha) {
            canSubmit = true;
        };
        return canSubmit;  // true → 跳转；false → 不跳转
    });
});