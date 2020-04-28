const urlParams = new URLSearchParams(window.location.search);
let msg = urlParams.get('msg');
if (msg != null) {
    layui.use('layer', function () {
        var layermsg = layui.layer;
        layermsg.msg(msg);
    });
};
