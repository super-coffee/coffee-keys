function grecaptcha() {
    axios
        .get(`/api/recaptcha/getSiteKey`)
        .then(response => {
            var opt_widget_id = grecaptcha.render(
                'recaptcha',
                { "sitekey": response.data }
            )
            return opt_widget_id;
        })
        .catch(error => {
            console.log(error);
            layui.use('layer', function () {
                var layer = layui.layer;
                layer.msg("发生了一个异常，请到 Console 查看");
            });
        });
};