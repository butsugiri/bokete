var getDatasetName = function() {
    var self = this;
    $.ajax({
            type: 'GET',
            url: 'http://0.0.0.0:5000/data-stats',
            contentType: 'application/json',
            dataType: 'json'
        })
        .done(function(data) {
            self.datasetName = data.data_name;
        })
}

var generateBoke = function() {
    var self = this;
    if (self.useTrainData) {
        var datatype = "train"
    } else {
        var datatype = "dev"
    }
    var data = {
        datatype: datatype,
        count: self.count,
        crossDomain: true
    }
    $.ajax({
            type: 'POST',
            url: 'http://0.0.0.0:5000/from-dataset',
            contentType: 'text/plain',
            data: JSON.stringify(data),
            dataType: 'json'
        })
        .done(function(data) {
            $.each(data, function(i, value) {
                self.bokes.push(value);
                console.log(value);
            })
            self.count += 1;
        })
}

var app = new Vue({
    el: "#content",
    data: {
        datasetName: "",
        useTrainData: true,
        bokes: [],
        count: 0
    },
    created: function() {
        this.getDatasetName()
    },
    computed: {
      hasGeneratedBoke: function () {
        return this.bokes.length > 0 ? true : false;
      }
    },
    methods: {
        getDatasetName: getDatasetName,
        generateBoke: generateBoke

    }
})

var table = new Vue({
  el: "#DataStats",
  data: {
    stats: {},
    datasetName: ""
  },
  created: function() {
    this.getStats();
    this.getDatasetName();
  },
  methods: {
    getStats: function () {
      var self = this;
      $.ajax({
            type: 'GET',
            url: 'http://0.0.0.0:5000/data-stats',
            contentType: 'application/json',
            dataType: 'json'
      })
      .done(function(data) {
        self.stats = data;
      })
    },
    getDatasetName: getDatasetName
  }
})
