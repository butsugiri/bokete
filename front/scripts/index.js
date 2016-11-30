var app = new Vue({
    el: "#box",
    data: {
        modelLoaded: false,
        isModelLoading: false
    },
    created: function() {
        this.checkModel()
    },
    computed: {
        model: function() {
            return this.modelLoaded
        }
    },
    methods: {
        checkModel: function() {
            //取得処理
            var self = this;
            $.ajax({
                    type: 'GET',
                    url: 'http://0.0.0.0:5000/is-model-loaded',
                    contentType: 'application/json',
                    dataType: 'json'
                })
                .done(function(data) {
                    self.modelLoaded = data;
                })
        },

        loadModel: function() {
            var self = this;
            self.isModelLoading = true;
            $.ajax({
              type: 'GET',
              url: 'http://0.0.0.0:5000/reload-model',
              contentType: 'application/json',
              dataType: 'json'
            })
            .done(function(data) {
              console.log(data);
              if (data == 'success') {
                self.modelLoaded = true;
                self.isModelLoading = false;
              }
            })
        }
    }
})
