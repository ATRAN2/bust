bust.view = {};

bust.view.StartScreenView = Backbone.View.extend({
  el: '#main-container',
  template: _.template($('#start-view-template').html()),
  userPositionAvailable: false,
  initialize: function(attributes, options) {
    this.userPosition = options.userPosition;
    this.listenToOnce(this.userPosition, 'change', this.allowSwitchView);
  },
  render: function() {
    this.$el.empty();
    this.$el.append(this.template);
    bust.view.bindFindStopsButton();
    bust.view.bindBrowseStopsButton();
    this.$el.fadeIn(200);
  },
  allowSwitchView: function() {
    bust.view.switchToStopsView();
    this.userPositionAvailable = true;
  },
})

bust.view.StopsListView = Backbone.View.extend({
  el: '#main-container',
  addingToLeftColumn : true,
  initialize: function() {
    _.bindAll(this, 'renderStop');
  },
  renderStop: function(model) {
    if (this.addingToLeftColumn) {
      $('#stops-container').append('<div class="row tail-row"></div>');
    }
    var stopView = new bust.view.StopView({model : model});
    stopView.render();
    $(this.el).find('.tail-row').append(stopView.$el);
    if (!this.addingToLeftColumn) {
      $(this.el).find('.tail-row').attr('class', 'row');
    }
    this.addingToLeftColumn = !this.addingToLeftColumn;
  },
  render: function() {
    this.$el.empty();
    this.$el.append('<h1 class="view-title">Stops Near You <span class="subtitle">(Select)</span></h1>');
    this.$el.append('<div id="stops-container"></div>');
    this.collection.each(this.renderStop);
    bust.view.addBottomPanel();
    this.$el.fadeIn(200);
  },
});

bust.view.StopView = Backbone.View.extend({
  template: _.template($('#stops-list-column-template').html()),
  events: {
    'click .button-primary' : 'clicked',
  },
  clicked : function(clickEvent) {
    clickEvent.preventDefault();
    bust.view.switchToPredictionsView(this.model);
  },
  render: function() {
    var html = this.template(this.model.toJSON());
    $(this.el).append(html);
  },
});

bust.view.PredictionsView = Backbone.View.extend({
  el: '#main-container',
  template: _.template($('#predictions-template').html()),
  initialize: function(attributes, options) {
    this.selectedBus = options.selectedBus;
    this.queryUrl = options.queryUrl;
    this.asyncUpdate();
    this.listenTo(this.collection, 'reset', this.render);
   },
  asyncUpdate: function() {
    this.intervId = setInterval(function(){
      bust.predictionsView.updateData(bust.predictionsView.queryUrl)}, 15000);
  },
  updateData: function(url) {
    if (bust.currentView != bust.predictionsView){
      clearInterval(bust.predictionsView.intervId);
    } else {
      bust.util.AjaxRequest.xmlRequestWithCallback(url, function(xmlDoc) {
        predictionsData = bust.util.PredictionsXMLParser
          .parseNextBusPredictionsXML(xmlDoc);
        newPredictions = new bust.model.BusPredictions(predictionsData);
        bust.predictionsView.collection.reset(newPredictions.models);
      });
    }
  },
  render: function() {
    mainBus = bust.model.findStopModelMatchInPredictionsData(
      this.selectedBus, this.collection.toArray());
    this.collection.remove(mainBus.cid, {silent : true});
    otherBuses = this.collection;

    mainBus.set('street_title', this.selectedBus.get('street_title'));
    mainBusView = new bust.view.PredictionsMainBusView({model : mainBus});
    mainBusView.render();

    // TODO Add "Other Buses Arrriving at This Stop"
    busViewTemplateRenders = {'main_bus' : mainBusView.el, 'other_bus' : ''};

    this.$el.empty();
    this.$el.append('<h1 class="view-title">Arrival Predictions For</h1>');
    this.$el.append(this.template(busViewTemplateRenders));
    
    var date = new Date();
    this.$el.append('<h6>Last updated ' + date.toString() + '</h6>');
    
    bust.view.addBottomPanel();
    this.$el.fadeIn(200);
  }
});

bust.view.PredictionsMainBusView = Backbone.View.extend({
  template: _.template($('#predictions-main-bus-template').html()),
  rewordMinutes: function(minutes) {
    text = ''
    if (minutes == 0) {
      text = 'Shortly';
    } else if (minutes == 1) {
      text = 'in ' + minutes + ' minute';
    } else {
      text = 'in ' + minutes + ' minutes';
    }
    return text
  },
  render: function() {
    var html = this.template(this.model.toJSON());
    minutes = this.model.attributes.minutes;
    for (ii = 0 ; ii < minutes.length ; ii++) {
      busString = (ii == 0) ? 'Next Bus Arriving ' : 'With Another Arriving ';
      busString = (ii >= 2 ) ? 'And Another Arriving ' : busString;
      html += '<h5> ' + busString + this.rewordMinutes(minutes[ii]) + '</h5>';
    }
    this.el = html;
  },
});

bust.view.switchToStopsView = function() {
  var validateStopsDataCallback = function(ajaxRequestResult) {
    var distanceKey = Object.keys(ajaxRequestResult)[0];
    bust.searchDistance = parseFloat(distanceKey);
    var nearbyStops = ajaxRequestResult[distanceKey];
    if (nearbyStops) {
      $('#main-container').filter(':visible').fadeOut(200, function () {
        createAndRenderStopsView(nearbyStops);
      });
    }
  }

  var createAndRenderStopsView = function(nearbyStops) {
    bust.stops = new bust.model.Stops(nearbyStops, {'userPosition' : bust.userPosition});
    if (!bust.stopsView) {
      bust.stopsView = new bust.view.StopsListView();
    }
    bust.previousViews.push(bust.currentView);
    bust.currentView = bust.stopsView;
    bust.stopsView.collection = bust.stops;
    bust.stopsView.render();
  }
  
  var lat = bust.userPosition.get('lat');
  var lon = bust.userPosition.get('lon');
  var bustQueryUrl = bust.util.BustApiUrlBuilder
    .getRadiusSearchUrl(lat, lon, undefined);
  bust.util.AjaxRequest.jsonRequestWithCallback(bustQueryUrl, validateStopsDataCallback);
}

bust.view.switchToPredictionsView = function(model) {
  var nextBusQueryUrl;
  var nextBusPredictionData;
  var selectedBus;

  getPredictionsViewUrlFromStop = function(stopModel) {
    selectedBus = stopModel;
    agency_tag = stopModel.attributes['agency_tag'];
    stop_id = stopModel.attributes['stop_id'];
    if (stop_id) {
      nextBusQueryUrl = bust.util.NextBusUrlBuilder
        .getPredictionsWithStopIdUrl(agency_tag, stop_id);
    } else {
      route_tag = stopModel.attributes['route_tag'];
      stop_tag = stopModel.attributes['stop_tag'];
      nextBusQueryUrl = bust.util.NextBusUrlBuilder
        .getPredictionsWithStopTagUrl(agency_tag, route_tag, stop_tag);
    }
  }

  getPredictionsXmlFromUrl = function(queryUrl) {
    bust.util.AjaxRequest.xmlRequestWithCallback(queryUrl, function(xmlDoc) {
      nextBusPredictionsData = bust.util.PredictionsXMLParser
        .parseNextBusPredictionsXML(xmlDoc);
      bust.predictionsCollection = new bust.model.BusPredictions(nextBusPredictionsData);
      createPredictionsViewFromCollection(bust.predictionsCollection);
    });
  }

  createPredictionsViewFromCollection = function(predictionData) {
    $('#main-container').filter(':visible').fadeOut(200, function() {
        bust.predictionsView = new bust.view.PredictionsView({collection : predictionData},
          {'selectedBus' : selectedBus, 'queryUrl' : nextBusQueryUrl});
        bust.predictionsView.render();
        bust.previousViews.push(bust.currentView);
        bust.currentView = bust.predictionsView;
    });
  }

  getPredictionsViewUrlFromStop(model);
  getPredictionsXmlFromUrl(nextBusQueryUrl) // Continues on to create the predictionsView
}

bust.view.bindFindStopsButton = function() {
  $('.find-stops').click( function() {
   if (bust.userPosition.get('lat')) {
     bust.view.switchToStopsView();
   } else {
     currentLocation = bust.util.getUserLocation();
   }
  });
}

bust.view.bindBrowseStopsButton = function() {
  $('.browse-stops').click( function() {
    alert('Feature not implemented yet');
  });
}

bust.view.addBottomPanel = function() {
  $('#main-container').append('<div class="bottom-panel"></br><button id="back-button" class="button">Back</button>  <button id="home-button" class="button">Home</button></div>');
  bust.view.bindBackButton();
  bust.view.bindHomeButton();
}

bust.view.bindBackButton = function() {
  $('#back-button').click( function() {
    $('#main-container').filter(':visible').fadeOut(200, function() {
      bust.currentView = bust.previousViews.pop();
      bust.currentView.render();
    });
  });
}

bust.view.bindHomeButton = function() {
  $('#home-button').click( function() {
    if (bust.currentView.cid  != bust.startView.cid) {
      $('#main-container').filter(':visible').fadeOut(200, function() {
        bust.previousViews.push(bust.currentView);
        bust.currentView = bust.startView;
        bust.currentView.render();
      });
    }
  });
}

