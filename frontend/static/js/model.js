bust.model = {};

bust.model.Stop = Backbone.Model.extend({
  defaults: {
    agency_tag: '',
    agency_title: '',
    route_tag: '',
    stop_tag: '',
    stop_id: '',
    street_title: '',
    direction: '',
    direction_name: '',
    lat: '',
    lon: '',
    dist: '',
  },
  initialize: function(attributes, options) {
    this.set('id', this.cid);
    this.userPosition = options.userPosition;
    this.listenTo(this.userPosition, 'change', this.setDist);
    if (this.userPosition.get('lat')) {
      this.setDist(this);
    }
  },
  setDist: function (model) {
    stopLat = parseFloat(this.get('lat'));
    stopLon = parseFloat(this.get('lon'));
    userLat = parseFloat(this.userPosition.get('lat'));
    userLon = parseFloat(this.userPosition.get('lon'));
    distance = Math.sqrt(Math.pow((userLat - stopLat), 2) + Math.pow((userLon - stopLon), 2));
    distance_in_miles = (distance * 69).toFixed(3);
    this.set('dist', distance_in_miles);
  },
});

bust.model.Stops = Backbone.Collection.extend({
  model: bust.model.Stop
});

bust.model.Position = Backbone.Model.extend({
  defaults: {
    lat: '',
    lon: '',
  },
});

bust.model.BusPrediction = Backbone.Model.extend({
  defaults: {
    agency_title: '',
    route: '',
    direction: '',
    minutes: '',
  },
});

bust.model.BusPredictions = Backbone.Collection.extend({
  model: bust.model.BusPrediction
})

bust.model.sortStopsJSONArrayByDistance = function (stopsArray) {
  stopsComparator = function (a, b) {
    if (a['dist'] < b['dist']) {
      return -1;
    }
    if (a['dist'] > b['dist']) {
      return 1;
    }
      return 0;
  }
  stopsArray.sort(stopsComparator);
}

// Predictions using a stopId on the NextBus API returns prediction times of
// all buses for that stop in random order.  The user selected bus needs
// to be filtered out from the results.
bust.model.findStopModelMatchInPredictionsData = function (stop, predictions) {
  isSameStop = function(stop, prediction) {
    attributes = ['agency_title', 'route_tag', 'stop_tag', 'direction']
    sameStop = true;
    for (ii = 0 ; ii < attributes ; ii++) {
      if (stop.attributes[attribute[ii]] != prediction.attributes[attribute[ii]]) {
        sameStop = false;
        break;
      }
    }
    return isSameStop;
  }
  for (ii = 0 ; ii < predictions.length ; ii++) {
    prediction = predictions[ii]
    if (isSameStop(stop, prediction)) {
      return prediction;
    }
  }
  return '';
}

