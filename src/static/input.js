$('#imageproxy').click(function () { $('#image').click(); });
var dataurl;
var filename

function getFilename () {
   var fullPath = $('#image')[0].value;
    if (fullPath) {
        var startIndex = (fullPath.indexOf('\\') >= 0 ? fullPath.lastIndexOf('\\') : fullPath.lastIndexOf('/'));
        filename = fullPath.substring(startIndex);
        if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
            filename = filename.substring(1);
        }
        return filename;
    }
    return 'Nothing selected';
}
function updateFilename () {
    filename = getFilename();
    $('#filenameHolder').text(filename);
    if (filename !== 'Nothing selected'){
        $("label.imagelabel").css("display", "none");
        $("#filenameHolder").css("color", "black");
        $("#filenameHolder").css("font-size", "55px");
        resizeImage();
    }
}

function resizeImage() {
    // Resize file
    var files = $("#image")[0].files;
    var file = files[0];
    var img = document.createElement("img");
    // Create a file reader
    var reader = new FileReader();
    // Set the image once loaded into file reader
    img.onload = function() {
        console.log("We doin it! :D");
        var canvas = document.createElement("canvas");
        //var canvas = $("<canvas>", {"id":"testing"})[0];
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);

        var MAX_WIDTH = 600;
        var MAX_HEIGHT = 400;
        var width = img.width;
        var height = img.height;

        if (width > height) {
          if (width > MAX_WIDTH) {
            height *= MAX_WIDTH / width;
            width = MAX_WIDTH;
          }
        } else {
          if (height > MAX_HEIGHT) {
            width *= MAX_HEIGHT / height;
            height = MAX_HEIGHT;
          }
        }
        canvas.width = width;
        canvas.height = height;
        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);

        dataurl = canvas.toDataURL("image/png");
        $("#image")[0].src = dataurl;
        console.log("We done did it!");
    }
    reader.onload = function(e)
    {
        img.src = e.target.result;
    }
    // Load files into file reader
    reader.readAsDataURL(file);
}

function dataURItoBlob(dataURI) {
    var byteString = atob(dataURI.split(',')[1]);
    var ab = new ArrayBuffer(byteString.length);
    var ia = new Uint8Array(ab);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: 'image/jpeg' });
}

function submitForm(){
    var form = new FormData(document.forms[0]);
    form.set("image", dataURItoBlob(dataurl), filename);
    var post = new XMLHttpRequest();
    post.open("POST", "/api/v1/item/", true);
    //post.setRequestHeader("Content-type", "multipart/form-data");
    post.onreadystatechange = function() {//Call a function when the state changes.
        if(post.readyState == XMLHttpRequest.DONE && post.status >= 200 && post.status < 300) {
            console.log("Success!");
            window.location.reload();
            //window.location.replace("/gear/"+qr_id);
        }
    }
    post.send(form)
    $("#submitbutton").css("display", "none");
    $("#imageform").append('<img src="/static/fire-animation.gif" width=118 height=208>');
}

$('#image').change(updateFilename);
updateFilename();

