//global variable
var page = 0;
var p;

//once the window load the function run.
window.onload = function () {
  
  // get the user location 
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition, showError);
  } else {
    var x = document.getElementById("location");
    x.innerHTML = "Geolocation is not supported by this browser.";
  }

  // If the user denied or is a problem run showError
  function showError(error) {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        x.innerHTML = "User denied the request for Geolocation."
        break;
      case error.POSITION_UNAVAILABLE:
        x.innerHTML = "Location information is unavailable."
        break;
      case error.TIMEOUT:
        x.innerHTML = "The request to get user location timed out."
        break;
      case error.UNKNOWN_ERROR:
        x.innerHTML = "An unknown error occurred."
        break;
    }
  }

  
  function showPosition(position) {
    // stored cordinates 
    p = position.coords.latitude + "," + position.coords.longitude;

    // call getEvents function
    getEvents(page);
  }
  
  // get the value from the location form
  var locationForm = document.getElementById('location-form');
  if (locationForm) {
    locationForm.addEventListener('submit', geocode);
  }

  function geocode(e) {
    // Prevent actual submit
    e.preventDefault();
    
    var location = document.getElementById('location-input').value;

    axios.get('https://maps.googleapis.com/maps/api/geocode/json', {
        params: {
          address: location,
          key: google_api_key
        }
      })
      .then(function (response) {
        // Log full response
        console.log(response);
        // Geometry
        var lat = response.data.results[0].geometry.location.lat;
        var lng = response.data.results[0].geometry.location.lng;
        p = lat + "," + lng;
        console.log(p);
        getEvents(page);
        console.log(lat);
        console.log(lng);
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  // The function will get the eventes from ticket master 
  function getEvents(page) {

    $("#events-panel").show();
    $("#attraction-panel").hide();

    if (page < 0) {
      page = 0;
      return;
    }
    if (page > 0) {
      if (page > getEvents.json.page.totalPages - 1) {
        page = 0;
      }
    }
    
    $.ajax({
      type: "GET",
      url: "https://app.ticketmaster.com/discovery/v2/events.json?apikey="+ tm_api_key + "&size=4&page=" + page + "&latlong=" + p,
      async: true,
      dataType: "json",
      success: function (json) {
        getEvents.json = json;
        showEvents(json);
      },
      error: function (xhr, status, err) {
        console.log(err);
      }
    });
  }
  // Show Events 
  function showEvents(json) {
    var items = $("#events .list-group-item");
    items.hide();
    var events = json._embedded.events;
    //items.first will get the fist children 
    var item = items.first();

    for (var i = 0; i < events.length; i++) {
      item.children('.list-group-item-heading').text(events[i].name);
      item.children('.list-group-item-text').text(events[i].dates.start.localDate);
      try {
        item.children(".venue").text(events[i]._embedded.venues[0].name + " in " + events[i]._embedded.venues[0].city.name);
      } catch (err) {
        console.log(err);
      }
      item.show();
      item.off("dblclick");
      item.dblclick(events[i], function (eventObject) {
        console.log(eventObject.data);
        try {
          getAttraction(eventObject.data._embedded.attractions[0].id);
        } catch (err) {
          console.log(err);
        }
      });
      item = item.next();
    }
  }
  //event licening click to the previus page
  $("#prev").click(function () {
    getEvents(--page);
  });
  //event licening click to the next page
  $("#next").click(function () {
    getEvents(++page);
  });

  // Atraction will recived the attraction id and get the attraction json 
  function getAttraction(id) {
    $.ajax({
      type: "GET",
      url: "https://app.ticketmaster.com/discovery/v2/attractions/" + id + ".json?apikey=" + tm_api_key,
      async: true,
      dataType: "json",
      success: function (json) {
        showAttraction(json);
      },
      error: function (xhr, status, err) {
        console.log(err);
      }
    });
  }
  //Show the attraction info
  function showAttraction(json) {
    $("#events-panel").hide();
    $("#attraction-panel").show();

    $("#attraction-panel").click(function () {
      getEvents(page);
    });

    $("#attraction .list-group-item-heading").first().text(json.name);
    $("#attraction img").first().attr('src', json.images[0].url);
    $("#classification").text(json.classifications[0].segment.name + " - " + json.classifications[0].genre.name + " - " + json.classifications[0].subGenre.name);
  }

  //event licening for the save buttons
  document.getElementById('save1').onclick = function () {
    myFunction('save1')
  };
  document.getElementById('save2').onclick = function () {
    myFunction('save2')
  };
  document.getElementById('save3').onclick = function () {
    myFunction('save3')
  };
  document.getElementById('save4').onclick = function () {
    myFunction('save4')
  };

  
  function myFunction(id) {
    // check is the id save1 was click 
    if (id == 'save1') {
      //display an alert to the user to confirm
      var conf1 = confirm("Are you sure want to save it?");
      if (conf1) {
        // if user confirm save is call
        save('heading_1', 'text_1', 'venue_1');
      } else {
        getEvents(page);
      }
    }
    // check is the id save2 was click
    if (id == 'save2') {
      //display an alert to the user to confirm
      var conf2 = confirm("Are you sure want to save it?");
      if (conf2) {
        // if user confirm save is call
        save('heading_2', 'text_2', 'venue_2');
      } else {
        getEvents(page);
      }
    }
    // check is the id save3 was click
    if (id == 'save3') {
      //display an alert to the user to confirm
      var conf3 = confirm("Are you sure want to save it?");
      if (conf3) {
        // if user confirm save is call
        save('heading_3', 'text_3', 'venue_3');
      } else {
        getEvents(page);
      }
    }
    // check is the id save4 was click
    if (id == 'save4') {
      //display an alert to the user to confirm
      var conf4 = confirm("Are you sure want to save it?");
      if (conf4) {
        // if user confirm save is call
        save('heading_4', 'text_4', 'venue_4');
      } else {
        getEvents(page);
      }
    }

    //
    function save(heading, text, venue) {
      // storing the innerText for the event in varibles
      var event_name = document.getElementById(heading).innerText;
      var date = document.getElementById(text).innerText;
      var location = document.getElementById(venue).innerText;
      //creating a object 
      var parameters = {
        eventName: event_name,
        date: date,
        location: location
      };
      //fetch json object to flask python 
      fetch(`${window.location.origin}/events/save`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(parameters),
        headers: new Headers({
          "content-type": "application/json"
        })
      });
    }
  }

}