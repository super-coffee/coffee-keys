var opt_widget_id;

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
                        grecaptcha();
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
};