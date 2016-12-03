space = function(len) {
    var t = [], i;
    for (i = 0; i < len; i++) {
        t.push(' ')
    }
    return t.join('')
}
format = function(edit) {
    var text = edit.text().replace(/\n/g, ' ').replace(/\r/g, ' ');
    //text = decodeURIComponent(escape(text));
    var t = [];
    var tab = 0;
    var inString = false;
    for (var i = 0, len = text.length; i < len; i++) {
        var c = text.charAt(i);
        if (inString && c === inString) {
            if (text.charAt(i - 1) !== '\\') {
                inString = false
            }
        } else if (!inString && (c === '"' || c === "'")) {
            inString = c
        } else if (!inString && (c === ' ' || c === "\t")) {
            c = ''
        } else if (!inString && c === ':') {
            c += ' '
        } else if (!inString && c === ',') {
            c += "\n" + space(tab * 4)
        } else if (!inString && (c === '[' || c === '{')) {
            tab++;
            c += "\n" + space(tab * 4)
        } else if (!inString && (c === ']' || c === '}')) {
            tab--;
            c = "\n" + space(tab * 4) + c
        }
        t.push(c)
    }
    edit.text(t.join(''))
}
$(function (){
    var qtype = $('#qtypes a.active').text();
    $('#qtype').text(qtype);

    $('.result').each(function() {
        format($(this));
    });
});
