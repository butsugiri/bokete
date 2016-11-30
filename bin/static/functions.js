var generateFromDataSet = function(i) {
    if ($('#data-type').prop('checked')) {
        var datatype = "train";
    } else {
        var datatype = "dev";
    }
    var data = {
        datatype: datatype,
        count: i
    }
    $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/from-dataset',
            contentType: 'application/json',
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(data) {
            $.each(data, function(i, value) {
                var boke = $("<div></div>").text(value.boke).addClass("balloon");
                var img_src = $("<img>").attr("src", value.img_src);
                var card = $("<div></div>")
                    .append(img_src)
                    .append(boke)
                    .addClass("card mdl-color--white mdl-shadow--2dp generated");
                $("#gen").append(card);
            });
            var is_button = $("#gen").next().length;
            if (!is_button) {
                $(".content")
                    .append($("<button></button>")
                        .addClass("mdl-button mdl-js-button mdl-button--raised mdl-button--primary mdl-js-ripple-effect")
                        .text("more")
                        .attr('id', 'btn'));
            };
            console.log(is_button);
        })
}

var generateFromImage = function() {
    var image_path = $("#uploaded").prop('src');
    var data = {
        image_path: image_path
    }
    console.log(data);
    $.ajax({
            type: 'POST',
            url: $SCRIPT_ROOT + '/fromimage',
            contentType: 'application/json',
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(data) {
            var boke = $("<div></div>").text(data.boke).addClass("balloon");
            $(".card").append(boke)
        })
}

var isModelLoaded = function() {
    var out = null;
    $.ajax({
            type: 'GET',
            url: $SCRIPT_ROOT + '/is-model-loaded',
            contentType: 'application/json',
            dataType: 'json',
            async: false
        })
        .done(function(data) {
            out = data;
        })
    return out;
}

var loadModel = function() {
    $("#load-model").hide();
    $(".mdl-spinner").addClass("is-active");

    $.ajax({
            type: 'GET',
            url: $SCRIPT_ROOT + '/reload-model',
            contentType: 'application/json',
            dataType: 'json'
        })
        .done(function(data) {
            if (data === 'success') {
                $(".require-model").each(function() {
                    $(this).show();
                    $(".mdl-spinner").hide();
                });
                $(".no-model").each(function() {
                    $(this).hide();
                    $(".mdl-spinner").hide();
                });
            }
        })
}

$(document).ready(function() {
    if ($("#uploaded").length) {
        generateFromImage();
    }
})
