var menuList = new Vue({
    el: '#menuList',
    data: {
        menuList: []
    }
});

// axios 请求后端
axios
    .get(`/api/Ui/index`)
    .then(response => {
        // 渲染
        menuList.menuList = response.data;
    })
    .catch(error => {
        console.log(error);
        layui.use('layer', function () {
            var layer = layui.layer;
            layer.msg("发生了一个异常，请到 Console 查看");
        });
    });