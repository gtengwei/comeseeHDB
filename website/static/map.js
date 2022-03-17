function initMap() {
    // Create the map.
    const flatCoord = GetLatlong()
    const map = new google.maps.Map(document.getElementById("map"), {
      center: flatCoord,
      zoom: 17,
      mapId: "8d193001f940fde3", // mapstyle
    });
    // Create the places service.
    const service = new google.maps.places.PlacesService(map);
    let getNextPage;
    const moreButton = document.getElementById("more");

    moreButton.onclick = function () {
      moreButton.disabled = true;
      if (getNextPage) {
        getNextPage();
      }
    };
    // Perform a nearby search.
    service.nearbySearch(
      { location: flatCoord, radius: 500, type: "school" },
      (results, status, pagination) => {
        if (status !== "OK" || !results) return;

        addPlaces(results, map);
        moreButton.disabled = !pagination || !pagination.hasNextPage;
        if (pagination && pagination.hasNextPage) {
          getNextPage = () => {
            // Note: nextPage will call the same handler function as the initial call
            pagination.nextPage();
          };
        }
      }
    );
  }

  function GetLatlong(){
    var address = '{{ flat.block }}'+ "+" +'{{ flat.street_name }}';

    var axios = require('axios');

    var config = {
      method: 'get',
      url: 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&fields=geometry&key=AIzaSyBuAJYgULaIj-T8j4-HXP8mTR9iHf3rOKY&input='+ address,
      headers: { }
    };

    axios(config)
    .then(function (response) {
      return response.data.candidates[0].geometry.location
    })
    .catch(function (error) {
      console.log(error);
    });
  }
  function addPlaces(places, map) {
    const placesList = document.getElementById("places");

    for (const place of places) {
      if (place.geometry && place.geometry.location) {
        const image = {
          url: 'https://cdn-icons-png.flaticon.com/512/179/179386.png',
          size: new google.maps.Size(71, 71),
          origin: new google.maps.Point(0, 0),
          anchor: new google.maps.Point(17, 34),
          scaledSize: new google.maps.Size(25, 25),
        };

        new google.maps.Marker({
          map,
          icon: image,
          title: place.name,
          position: place.geometry.location,
        });

        const li = document.createElement("li");

        li.textContent = place.name;
        placesList.appendChild(li);
        li.addEventListener("click", () => {
          map.setCenter(place.geometry.location);
        });
      }
    }
  }