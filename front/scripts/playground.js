var app = new Vue({
    el: "#content",
    data: {
        isImageUploaded: false,
        image_src: "",
        boke: "",
        file: ""
    },
    computed: {
      disableButton: function () {
        return this.file.length > 0
      }
    },
    watch: {
        image_src: function(val, oldval) {
          var self = this;
            if (val) {
              var data = {
                src: val
              }
                $.ajax({
                        type: 'POST',
                        url: 'http://0.0.0.0:5000/fromimage',
                        contentType: 'text/plain',
                        dataType: 'json',
                        data: JSON.stringify(data)
                    })
                    .done(function (data) {
                      self.boke = data.boke;
                    })
            }
        }
    },
    methods: {
        onSubmit: function() {
            var self = this;
            var form = $('#myForm').get()[0];
            var formData = new FormData(form);
            $.ajax({
                url: 'http://0.0.0.0:5000/playground',
                type: 'POST',
                dataType: 'json',
                // dataに FormDataを指定
                data: formData,
                // Ajaxがdataを整形しない指定
                processData: false,
                // contentTypeもfalseに指定
                contentType: false
            }).done(function(res) {
                // 送信せいこう！
                console.log("SUCCESS!")
                self.isImageUploaded = true;
                self.image_src = res.file_path;
            }).fail(function(jqXHR, textStatus, errorThrown) {
                // しっぱい！
                console.log('ERROR', jqXHR, textStatus, errorThrown);
            });
        }
    }
})
