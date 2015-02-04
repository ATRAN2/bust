bust.util = {};

bust.util.getUserLocation = function() {
  navigator.geolocation.getCurrentPosition(
    function(position) {
      userCoord = {
       'lat' : position.coords.latitude,
       'lon' : position.coords.longitude,
      }
      bust.userPosition.set(userCoord);
      return userCoord;
    },
    function(error) {
      alert(error.message);
    },
    {
      enableHighAccuracy : true,
      timeout : 5100,
      maximumAge : 9000,
    }
  );
}


bust.util.BustApiUrlBuilder = {
  BUST_API_ROOT : 'http://bust.atran.net/api/',

  getAgenciesUrl : function() {
    apiEndpoint = 'agencies';
    url = this.BUST_API_ROOT + apiEndpoint;
    return url;
  },
  getAgencyRoutesUrl : function(agencyTag) {
    apiEndpoint = 'agency-routes';
    params = $.param({'atag' : agencyTag});
    url = this.BUST_API_ROOT + apiEndpoint + '?' + params;
    return url;
  },
  getRadiusSearchUrl : function(lat, lon, distance) {
    apiEndpoint = 'radius-search';
    if (distance) {
      params = $.param({'lat' : lat, 'lon' : lon, 'distance' : distance});
    } else {
      params = $.param({'lat' : lat, 'lon' : lon});
    }
    url = this.BUST_API_ROOT + apiEndpoint + '?' + params;
    return url;
  },
}

bust.util.NextBusUrlBuilder = {
  NEXTBUS_API_ROOT : 'http://webservices.nextbus.com/service/publicXMLFeed',
  
  getPredictionsWithStopIdUrl : function(agencyTag, stopId) {
    params = $.param({'command' : 'predictions', 'a' : agencyTag, 'stopId' : stopId});
    url = this.NEXTBUS_API_ROOT + '?' + params;
    return url;
  },
  getPredictionsWithStopTagUrl : function(agencyTag, routeTag, stopTag) {
    params = $.param({'command' : 'predictions', 'a' : agencyTag, 'r' : routeTag, 's' : stopTag});
    url = this.NEXTBUS_API_ROOT + '?' + params;
    return url;
  },
}

bust.util.PredictionsXMLParser = {
  parseNextBusPredictionsXML : function(xmlDoc) {
    predictionsParser = this;
    predictionData = [];
    busStopCounter = 0;
    $(xmlDoc).find('predictions').each( function() {
      predictionData.push({});
      currentStop = predictionData[busStopCounter];
      predictionsTags = {
        'agencyTitle' : 'agency_title',
        'routeTitle' : 'route',
        'routeTag' : 'route_tag',
        'stopTag' : 'stop_tag',
        'dirTitleBecauseNoPredictions' : 'direction',
      };
      predictionsParser.mapAttribsFromXMLFindToObj($(this), currentStop, predictionsTags);
  
      $(this).find('direction').each( function() {
        directionTags = {'title' : 'direction'};
        predictionsParser.mapAttribsFromXMLFindToObj($(this), currentStop, directionTags);
  
        predictionCounter = 0;
        predictionTimesInMinutes = [];
        $(this).find('prediction').each( function() {
          predictionTimesInMinutes.push($(this).attr('minutes'));
          currentStop['minutes'] = predictionTimesInMinutes;
        })
      })
  
      busStopCounter++;
    });
  return predictionData;
  },

  mapAttribsFromXMLFindToObj : function (fromXMLFind, toObj, attribMap) {
    for (attribute in attribMap) {
      toObj[attribMap[attribute]] = fromXMLFind.attr(attribute);
    }
  },
}

bust.util.AjaxRequest = {
  jsonRequestWithCallback : function(requestURL, callback) {
    $.ajax({
      url: requestURL,
      crossDomain: true,
      type: 'GET',
      data: 'json',
      success: function (result) {
        callback(result);
      }
    });
  },
  xmlRequestWithCallback : function(requestURL, callback) {
    $.ajax({
      url: requestURL,
      crossDomain: true,
      type: 'GET',
      data: 'xml',
      success: function (result) {
        callback(result);
      }
    });
  }
}
