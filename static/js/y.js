var y = {};

function getCookie(name) {
    var r = document.cookie.match(new RegExp("\\b" + name + "=([^;]*)\\b", "g"));
    return r ? r[r.length - 1].substring(name.length + 1) : undefined;
}
function clearCookie(name, domain, path){
    var domain = domain || document.domain;
    var path = path || "/";
    document.cookie = name + "=; expires=" + +new Date + "; domain=" + domain + "; path=" + path;
};

y.ajax = function(url, type, args, callback){
    return $.ajax({
        'type': type,
        'timeout': 1200000,
        'url': url,
        'data': args,
        'dataType': 'json'
    }).done(function (data) {
        if ('error_msg' in data){
            alert(data['error_msg']);
        }
        else if (callback){
            callback.call(this, data);
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        if (jqXHR.readyState == 0 || jqXHR.status == 0){
            return;
        }
        alert('Oops. I encountered something unexpected. \r\nDetail: ' + textStatus + " " + errorThrown);
    });
};

y.post = function(url, args, callback){
    args._xsrf = getCookie('_xsrf');
    return y.ajax(url, 'post', args, callback);
};

y.get = function(url, args, callback){
    return y.ajax(url, 'get', args, callback)
};

y.gui_ajax = function(url, type, args, callback, ctrls){
    var old_status = [];
    for (var i = 0; i < ctrls.length; ++i){
        var ctrl = ctrls[i];
        old_status.push($(ctrl).prop('disabled'));
        old_status.push($(ctrl).text());
        $(ctrl).prop('disabled', true);
        $(ctrl).text('Processing...');
    }
    return y.ajax(url, type, args, callback).always(function(){
        for (var i = 0; i < ctrls.length; ++i){
            var ctrl = ctrls[i];
            $(ctrl).prop('disabled', old_status[i*2]);
            $(ctrl).text(old_status[i*2+1]);
        }
    });
};

y.gui_get = function(url, args, callback, ctrls){
    return y.gui_ajax(url, 'get', args, callback, ctrls);
};

y.gui_post = function(url, args, callback, ctrls){
    return y.gui_ajax(url, 'post', args, callback, ctrls);
};

y.clone = function(obj){
    return $.extend(true, {}, obj);
};

y.escape_html = (function(){
    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': '&quot;',
        "'": '&#39;',
        "/": '&#x2F;'
    };

    return function (string) {
        return String(string).replace(/[&<>"'\/]/g, function (s) {
            return entityMap[s];
        });
    };
})();

y.unescape_html = (function(){
    var entityMap = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        '&quot;': '"',
        '&#39;': "'",
        '&#x2F;': "/"
    };

    return function (string) {
        return String(string).replace(/(&amp;|&lt;|&gt;|&quot;|&#39;|&#x2F)/g, function (s) {
            return entityMap[s];
        });
    };
})();