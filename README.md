# Bust

**This app was created as a response to the [Uber Coding Challenge](https://github.com/uber/coding-challenge-tools/blob/master/coding_challenge.md)**

The goal of Bust is to have a quick and efficient way to get bus arrival predictions.  When searching through a site like www.nextbus.com, a user needs to dig through a list of agencies, a list of routes, then find the specific stop they're looking for.  Much of that information is extraneous for the user.  Most of the time a user is nearby wondering if they should start walking to the stop or not.  Rather than having to search through huge dropdown lists to find a stop, Bust serves to reduce the hassle by asking for the user's location then returning just the nearby stops.

Implementation
---
##### Backend
The data source for the bus stop data was taken from the [NextBus API](http://api-portal.anypoint.mulesoft.com/nextbus/api/nextbus-api).  Unfortunately the NextBus API does not have a means to search for stops based on location.  Because of that there was a need to extract the relevant agency, route, and stop data and create a new API.  To do that a lightweight Flask application was used to scour the nextBus API, parse the information, build a datastore and subsequently serve the data as an API.

Since the Bust user interface needs to make a 2D query to find entries around a (lat, lon) coordiniate, a datastore with spatial indexing was essential.  For that Bust uses [Rtree] (http://toblerity.org/rtree/) which makes returning queries from (lat, lon) quite fast (On average of about 3 ms).  As the scale of data stored wasn't that large, there wasn't a real need for a full sized SQLesque database. Bust just leaves all the data in memory which also serves to keep things fast. For data persistence, Bust can serialize the datastore then deserialize it on load.

##### Frontend
The Bust frontend is made using [Backbone.js](http://backbonejs.org/) for models and views and Underscore for templating.  As the goal of the app is to be quick and lightweight, Backbone is at a good medium by adding some structure to the javascript without the excess baggage of other heavier javascript frameworks. Since mobile users are a main target for this app, having a responsive interface with a light footprint is a concern.  For that, styling was done with [Skeleton CSS](getskeleton.com) which greatly simplifies the task of making a responsive UI.

As it stands the Bust frontend currently has a very basic user interface.  There is one button that can be pressed and when it does, it uses HTML 5 Geolocation to try and get the user's current location.  When the user's location is received the app will send send a request to the Bust backend API.  From that data a view with lists of the nearby stops is shown.  The user can then select one of the stops to view that bus' arrival predictions which are taken at intervals from the NextBus API.
 
Installation
---
The Rtree module used in Bust depends on [libspatialindex](http://libspatialindex.github.io/).  Make sure it's installed first.
After that the Python backend built on Flask can be quickly installed from the provided setup.py in /backend. Setup and source a virtualenv then execute setup.py with install (or develop if you want to make changes)

```sh
$ python ./setup.py install
```

It should install all the dependencies required.  Now move to the bust directory and send bust-build to grab data from the NextBus API and generate nextbus.data which the app needs to run:

```sh
$ cd bust
$ bust-build
```

It should take a little while as the NextBus API has a data limit of 4MB / 20 seconds.  After it's done querying and saving the datastore to disk, just send bust-start to run the server locally:

```sh
$ bust-start
```

Configuring
---
The following configuration methods are available for Bust:

##### Limiting the Agency Region
In config.py changing the value of AGENCY_REGION will filter the agency query to only get data on agencies with that string in the regionTitle field.  The agency list can be viewed from the [NextBus agencyList](http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList).

The default is set to 'California' to only get agencies in California.  Leaving this as an empty string '' will download all data from all agencies.  Note that the NextBus API has bandwidth caps.

##### Changing the nextbus.data Save File Path
By default bust-build will gather data and place the saved datastore at the directory it is run with the filename 'nextbus.data'.  It's advisable to make this an absolute path so the datastore can saved and found in the same place.  Do this by editing the NEXTBUS_FILE_PATH variable in config.py.  Be sure to do this and build a new datastore before running unit tests.  The unit tests load from a nextbus.data file and will search for it in the current directory.  This can be resolved with an absolute path.

##### Configuring Search Radius
In constants.py there are the variables MAX_SEARCH_DISTANCE and MIN_SEARCH_DISTANCE.  These dictate the minimum and maximum distances searched when trying to find buses near a user location.

Backend API
---
The Bust API has the following endpoints:
```sh
$ /api
```
Returns these api links and descriptions in JSON format.

```sh
$ /api/agencies
```
Returns a list of all agencies in the NextBus feed with their agency_tags and agency_titles.

```sh
$ /api/agency-routes?atag=<agency_tag>
```
Returns agency routes' route_tags given the agency_tag in \<agency_tag\>.

```sh
$ /api/route-stops?atag=<agency_tag>&rtag=<route_tag>
```
Returns the stops data which includes stop_tags (object key), direction, lat, lon, stop_id (if available), and street_title.  Takes \<agency_tag\> and \<route_tag\> as required parameters.

```sh
$ /api/radius-search?lat=<latitude>&lon=<longitude>&distance=<distance_in_miles>
```
Searches and returns information about bus stops around \<latitude\> and \<longitude\>.  \<distance_in_miles\> is an optional parameter that will set the search distance (in miles).  Leaving distance out will do gradually increasing radial searches until at least one stop entry is returned.

Features to Add
---
Given time constraints there were quite a few features that I wanted to add but was not able to.

##### Favorite Stops
The option to favorite stops and save tags locally using Backbone.localStorage would be very useful.  Since a user may tend to use the same bus stop repeatedly if it's part of their routine commute, a means to favorite stops would likely improve their user experience.

##### Stop Searching
One very key feature is the option to manually select a stop through the standard means of agency-route-stop, or better, with some sort of search.  It's a fallback in case the user cannot give their geolocation.

##### A Map
Another feature is an implementation of a map. If a user is searching for a bus, it would help to have a map visible that highlights selected stops. Also, NextBus has on their API lists of lat lon coordinates that follow along each route. This can be used to [draw a path on the map](https://developers.google.com/maps/documentation/javascript/examples/polyline-simple) to illustrate the bus route. The API also gives bus GPS locations which can be implemented on the map as well.  Together these can give a user a "progress bar" as they can look on the map to see the bus approach them along the path.

##### A Second Datastore
Transit 511 also has an API to get bus times and arrivals.  It might be useful to include their data as a fallback or alternative to NextBus.

Experience With the Stack
---
I've only dabbled a bit with Flask in the past, and have no experience at all with Backbone.js.  I also have very little experience with javascript.  I've done a project with Django however, and that experience transferred laterally a bit.  It made URL routing and setting up a server with uwsgi/nginx a bit easier. It also made me a bit familiar with the MV* paradigm of Backbone.js.  Even so it was mostly uncharted waters and I found myself reading docs quite often.  It was still exciting to work with unfamiliar technologies though and I learned an unbelievable working on this project.  I will most likely keep working on improving it as well as my skills.

## Track
The track I'll choose for the coding challenge will be for the **Backend**.  I feel more confident in my skills with Python and backend design.  That isn't to say I wouldn't be interested in also working on the frontend.  I had a great time working with Backbone.js during this project, but as I have less experience on that side of development, I feel like I'll have more to offer on the backend.

## Links
##### Resume
http://www.atran.net/static/resume.pdf

##### Hosted Application w/ API
http://bust.atran.net

