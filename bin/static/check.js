var getDatasetStats = function () {
    $.ajax({
            type: 'GET',
            url: $SCRIPT_ROOT + '/data-stats',
            contentType: 'application/json',
            dataType: 'json'
        })
        .done(function(data) {
          $("#n_vocab").next().text(data.n_vocab);
          $("#train_boke").next().text(data.train.total_boke);
          $("#train_img").next().text(data.train.unique_images);
          $("#dev_boke").next().text(data.dev.total_boke);
          $("#dev_img").next().text(data.dev.unique_images);
          $("h4").each(function () {
            $(this).append('"' + data.data_name + '"')
          });
        })
}

$(document).ready(function() {
    // 生成(Generate)ボタンの処理
    var i = 0 //何回生成ボタンを押したか？
    $('.mdl-cell').on('click', '#btn', function() {
        generateFromDataSet(i);
        i += 1;
        console.log(i);
    })
    getDatasetStats();
})
