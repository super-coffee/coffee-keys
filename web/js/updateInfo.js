var opt_widget_id;  // 第一个
var optid;  // 第二个

var twoform = new Vue({
    el: "#twoform",
    data: {
        hiddenData: false,
        canShow: false,
        origin: {
            mail: null,
            password: null
        },
        updateInfo: {
            name: null,
            mail: null,
            pubkey: null
        },
        checkPassword: {
            password: "",
            repeat_password: ""
        }
    },
    computed: {
        hasPassword: function () {
            return this.checkPassword.password == "" ? false : true;
        },
        isPasswordEqual: function () {
            // `this` 指向 vm 实例
            return this.checkPassword.password == this.checkPassword.repeat_password;
        }
    }
});

function recaptchainVerifyPassword() {
    axios
        .get(`/api/recaptcha/getSiteKey`)
        .then(response => {
            opt_widget_id = grecaptcha.render(
                "recaptchainVerifyPassword",
                { "sitekey": response.data }
            );
            grecaptcha.reset(opt_widget_id);
        })
        .catch(error => {
            console.log(error);
            layui.use('layer', function () {
                var layer = layui.layer;
                layer.msg("发生了一个异常，请到 Console 查看");
            });
        });
}
// 监听第一表单提交事件
layui.use('form', function () {
    var form = layui.form;
    form.on('submit(verifyPassword)', function (data) {
        // 读取表单的信息
        var data = form.val("verifyPassword");
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
        if (doRecaptcha && hasRecaptcha) {
            canSubmit = true;
        };
        if (canSubmit) {
            layui.use('layer', function () {
                var layer = layui.layer;
                layer.load();
            });
            var u_mail = data["mail"];
            var u_password = data["password"];
            var g = data["g-recaptcha-response"];
            axios
                .get(`/api/verifyPassword?mail=${u_mail}&password=${u_password}&g-recaptcha-response=${g}`)
                .then(response => {
                    if (response.data.status) {
                        // 显示修改的信息框
                        searchKey(twoform.origin.mail);
                        twoform.canShow = true;
                        optid = grecaptcha();
                        bindUploadButton();
                    } else {
                        layui.use('layer', function () {
                            var layer = layui.layer;
                            layer.msg(response.data.data);
                        });
                    }
                    grecaptcha.reset(opt_widget_id);
                })
                .catch(error => {
                    console.log(error);
                    layui.use('layer', function () {
                        var layer = layui.layer;
                        layer.msg("发生了一个异常，请到 Console 查看");
                    });
                    grecaptcha.reset(opt_widget_id);
                });
            layer.closeAll('loading');
        }
        return false;  // true → 跳转；false → 不跳转
    });
});

// 监听第二表单提交事件
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
                layer.tips('请完成 reCAPTCHA 人机身份验证', '#submit2', {
                    tips: 3,  // 下
                    tipsMore: true
                });
            });
        };
        if (!twoform.isPasswordEqual) {
            layui.use('layer', function () {
                layer.tips('密码不一致', '#repeat-password', {
                    tips: 3,  // 下
                    tipsMore: true
                });
            });
        };
        if (doRecaptcha && twoform.isPasswordEqual && hasRecaptcha) {
            canSubmit = true;
        };
        console.log(doRecaptcha);
        console.log(hasRecaptcha);
        console.log(twoform.isPasswordEqual);
        return canSubmit;  // true → 跳转；false → 不跳转
    });
});

// searchKey
function searchKey(userMail) {
    layui.use('layer', function () {
        var layer = layui.layer;
        layer.load();
    });
    axios
        .get(`/api/searchKey?mail=${userMail}`)
        .then(response => {
            responseData = response.data;
            if (responseData.status) {
                twoform.updateInfo = responseData.data;
            } else {
                layer.msg(responseData.data);
            };
        })
        .catch(error => {
            console.log(error);
            layer.msg("发生了一个异常，请到 Console 查看");
        });
    layui.use('layer', function () {
        var layer = layui.layer;
        layer.closeAll('loading');
    });
};

function bindUploadButton() {
    layui.use('upload', function () {
        var upload = layui.upload;
        upload.render({
            elem: '#uploadpem' //绑定元素
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
};

function confirmDelete() {
    layui.use('form', function () {
        layui.use('layer', function () {
            var layer = layui.layer;
            layer.load();
            var form = layui.form;
            var data = form.val("form");
            var doRecaptcha = data["g-recaptcha-response"] == "" ? false : true;  // 三目
            var hasRecaptcha = "g-recaptcha-response" in data;
            var grecaptcharesponse = data["g-recaptcha-response"];
            var canSubmit = false;
            // 判断是否可提交
            if (!doRecaptcha || !hasRecaptcha) {
                layui.use('layer', function () {
                    layer.tips('请完成 reCAPTCHA 人机身份验证', '#submit2', {
                        tips: 3,  // 下
                        tipsMore: true
                    });
                });
            };
            if (doRecaptcha && hasRecaptcha) {
                canSubmit = true;
            };
            var userMail = twoform.origin.mail;
            var userPassword = twoform.origin.password;
            if (canSubmit) {
                if (confirm('真的要删除吗？你在删除后无法找回你的信息！') == true) {
                    axios
                        .delete(`/api/deleteInfo?mail=${userMail}&password=${userPassword}&g-recaptcha-response=${grecaptcharesponse}`)
                        .then(response => {
                            responseData = response.data;
                            if (responseData.status) {
                                layer.closeAll();
                                layer.msg("已删除");
                                window.location.href = "/newKey.html";
                            } else {
                                layer.msg(responseData.data);
                            };
                        })
                        .catch(error => {
                            console.log(error);
                            layer.msg("发生了一个异常，请到 Console 查看");
                        });
                    layer.msg('正在删除');
                } else {
                    layer.msg('已取消');
                };
            };
            grecaptcha.reset(optid);
            layer.closeAll("loading");
        });
        return false;
    });
};