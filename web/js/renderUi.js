// 导航依赖 element 模块
layui.use('element', function () {
    var element = layui.element;
});
var layer;
layui.use('layer', function () {
    layer = layui.layer;
    layer.load();

    var title = new Vue({
        el: '#title',
        data: {
            displyName: 'Loading'
        }
    });

    axios
        .get(`/api/Ui/common`)
        .then(response => {
            // 渲染
            title.displyName = response.data.displyName;
            layer.closeAll('loading');
        })
        .catch(error => {
            console.log(error);
            layer.msg("发生了一个异常，请到 Console 查看");
        });
});