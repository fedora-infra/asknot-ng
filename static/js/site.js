// Setup our own endsWith definition since midori doesn't know about it.
String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

$(document).ready(function() {
    // First thing.. hide the warning about javascript being required.
    $("#js-warning").addClass('hidden');

    var first = question_tree['children'][0]['id'];

    var found = false;
    $.each(all_ids, function(i, idx) {
        if (location.href.endsWith(SEP + idx)) {
            $("#" + idx).removeClass('hidden');
            found = true;
        }
    });
    if (! found) {
        $("#" + first).removeClass('hidden');
        var original = location.href.replace(/\/$/, "")
        history.pushState({}, '', original + SEP + first);
    }


    // Wire up the "yes" links
    $("a.yes").click(function(event) {
        $(this).parent().parent().addClass('hidden');
        var next = $(this).attr('data-next');
        $('#' + next).removeClass('hidden');
        var original = location.href.replace(/\/$/, "")
        history.pushState({}, '', original + SEP + next);
    });

    // Wire up the "nope" links
    $("a.nope").click(function(event) {
        $(this).parent().parent().addClass('hidden');
        var next = $(this).attr('data-next');
        $('#' + next).removeClass('hidden');
        var tokens = location.href.replace(/\/$/, "").split(SEP).slice(0, -1);
        tokens.push(next);
        history.replaceState({}, '', tokens.join(SEP));
    });

    // Wire up the "back" links
    $("a.back").click(function(event) {
        $(this).parent().parent().addClass('hidden');
        var tokens = location.href.replace(/\/$/, "").split(SEP).slice(0, -1);
        var next = tokens.slice(-1).pop();
        history.go(-1);
        $('#' + next).removeClass('hidden');
    });

});
