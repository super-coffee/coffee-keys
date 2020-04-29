// urlParams
const urlParams = new URLSearchParams(window.location.search);
let userMail = urlParams.get('mail');
if (userMail != null) {
    searchKey(userMail);
};

// vue
var datas = new Vue({
    el: '#datas',
    data: {
        datas: {}
    }
});

// searchKey
function searchKey(userMail) {
    axios
        .get(`/api/searchKey?mail=${userMail}`)
        .then(response => {
            responseData = response.data
            if (responseData.status) {
                datas.datas = responseData.data;
            } else {
                showMsg(responseData.data);
            };
        })
        .catch(error => {
            console.log(error);
            showMsg("发生了一个异常，请到 Console 查看");
        });
};

// clipboard.js
var clipboard = new ClipboardJS('.pubkey');
clipboard.on('success', function (e) {
    e.clearSelection();
    layer.tips('已复制', '#pubkey', {
        tips: 3
    });
});
clipboard.on('error', function (e) {
    console.error('Action:', e.action);
    console.error('Trigger:', e.trigger);
    layer.tips('复制失败，请手动复制', '#pubkey', {
        tips: 3
    });
});

layui.use('form', function () {
    var form = layui.form;
});

function showMsg(msg) {
    layui.use('layer', function () {
        var layermsg = layui.layer;
        layermsg.msg(msg);
    });
}