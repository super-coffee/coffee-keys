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
                .post(`/api/`)
                .then(response => {
                    if (response.data.status) {
                        twoform.canShow = true;
                        grecaptcha();
                    } else {
                        layui.use('layer', function () {
                            var layer = layui.layer;
                            layer.msg(response.data.data);
                        });
                    }
                    grecaptcha.reset(verifyPassword.opt_widget_id);
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
