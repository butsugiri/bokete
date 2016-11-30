$(document).ready(function() {
    if (!isModelLoaded()) {
        $(".require-model").each(function() {
            $(this).hide();
        });
        $(".no-model").each(function() {
            $(this).show();
        });
    } else {
        $(".require-model").each(function() {
            $(this).show();
        });
        $(".no-model").each(function() {
            $(this).hide();
        });
    };
    $('#load-model').on('click', loadModel);
})
