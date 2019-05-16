function Photo(data) {
    this.id = ko.observable(data.id);
    this.postedby = ko.observable(data.postedby);
    this.description = ko.observable(data.description);
    this.postedtime = ko.observable(data.postedtime);
    this.tag1 = ko.observable(data.tag1);
    this.tag2 = ko.observable(data.tag2);
    this.tag3 = ko.observable(data.tag3);
    this.url = ko.observable(data.url);
}

function PhotoListViewModel() {
    var self = this;
    self.photos_list = ko.observableArray([]);
    self.postedby = ko.observable();
    self.postedtime = ko.observable();
    self.description = ko.observable();
    self.tag1 = ko.observable();
    self.tag2 = ko.observable();
    self.tag3 = ko.observable();

    self.addPhoto = function() {
      self.save();
	self.postedby("");
	self.postedtime("");
	self.description("");
	self.url("");
	self.tag1("");
	self.tag2("");
	self.tag3("");
    };

    $.getJSON('/photos', function(photoModels) {
	var t = $.map(photoModels.photos_list, function(item) {
	    return new Photo(item);
	});
	self.photos_list(t);
    });

    self.save = function() {
	return $.ajax({
	    url: '/photos',
	    contentType: 'application/json',
	    type: 'POST',
	    data: JSON.stringify({
		'postedby': session['username'],
    'description': self.description(),
    'postedtime' : strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()),
    'url' : {{url_for('send', filename=image_name)}},
    'tag1' : self.description(),
    'tag2' : self.description(),
    'tag3' :self.description()
	    }),
	    success: function(data) {
          alert("success")
		      console.log("Pushing to users array");
		      self.push(new Photo({ username: data.username, description: data.description, postedtime: data.postedtime, url: data.url, tag1: data.tag1, tag2: data.tag2, tag3: data.tag3}));
		      return;
	    },
	    error: function() {
		return console.log("Failed");
	    }
	});
    };
}

ko.applyBindings(new PhotoListViewModel());
