var verifyPassword = new Vue({
    el: "#verifyPassword",
    data: {
        opt_widget_id: null
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

var twoform = new Vue({
    el: "#twoform",
    data: {
        canShow: false
    }
});

function recaptchainVerifyPassword() {
    axios
        .get(`/api/recaptcha/getSiteKey`)
        .then(response => {
            verifyPassword.opt_widget_id = grecaptcha.render(
                "recaptchainVerifyPassword",
                { "sitekey": response.data }
            );
            console.log(verifyPassword.opt_widget_id);
            grecaptcha.reset(verifyPassword.opt_widget_id);
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
            var u_mail = data["mail"];
            var u_password = data["password"];
            console.log(u_password);
            var g = data["g-recaptcha-response"];
            axios
                .get(`/api/verifyPassword?mail=${u_mail}&password=${u_password}&g-recaptcha-response=${g}`)
                .then(response => {
                    if (response.data.status) {
                        twoform.canShow = true;
                        grecaptcha();
                    } else {
                        layui.use('layer', function () {
                            var layer = layui.layer;
                            layer.msg(response.data.data);
                        });
                        grecaptcha.reset(verifyPassword.opt_widget_id);
                    }
                })
                .catch(error => {
                    console.log(error);
                    layui.use('layer', function () {
                        var layer = layui.layer;
                        layer.msg("发生了一个异常，请到 Console 查看");
                    });
                    grecaptcha.reset(verifyPassword.opt_widget_id);
                });
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
        if (doRecaptcha && checkPassword.isEqual) {
            canSubmit = true;
        };
        return canSubmit;  // true → 跳转；false → 不跳转
    });
});