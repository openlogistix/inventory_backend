// $.fn.editable.defaults.mode = 'inline';
// $.fn.editable.defaults.ajaxOptions = {type: "PUT"};
// $(document).ready(function() {
//     $('#name').editable();
// });

/*
 * onclick, replace element with form, with mdl classes
 * on onfocus, replace with original element
 * on submit, send PUT xhr with appropriate form data
 *
 */
var formtemplate = '' +
'<form action="/api/v1/item/%id" method="put">' +
'  <div class="mdl-textfield mdl-js-textfield">' +
'    <input class="mdl-textfield__input" type="text" name="%name">' +
'    <label class="mdl-textfield__label" for="%name">%value</label>' +
'  </div>' +
'</form>';

function makeform(e) {
    var elem = $(e);
    var html = formtemplate.replace(/%id/, elem.data('id'));
    html = html.replace(/%name/g, elem.data('name'));
    html = html.replace(/%value/, elem.data('value'));
    return html;
}

function initializeeditable(e) {
    var previouscontents = e.innerHTML;
    var inputform = makeform(e);
    $(inputform).focusout(function(){
        this.innerHTML = previouscontents;
    });
    $(e).click(function() {
        this.innerHTML = inputform;
    });
}

$(document).ready(function() {
    initializeeditable($('#name')[0]);
    $('#name').click(makeform);
});


function clearObject(){
    var del = new XMLHttpRequest();
    del.open("DELETE", "/api/v1/item/"+primarykey, true);
    del.onreadystatechange = function() {//Call a function when the state changes.
        if(del.readyState == XMLHttpRequest.DONE && del.status >= 200 && del.status < 300) {
            console.log("Success!");
            window.location.reload();
            //window.location.replace("/gear/"+qr_id);
        }
    }
    del.send()
    $("#clearbutton").css("display", "none");
    $("#cleardiv").append('<img src="/static/fire-animation.gif" width=118 height=208>');
}
