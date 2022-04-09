function deleteReview(reviewId,flatId) {
  fetch("/delete-review", {
    method: "POST",
    body: JSON.stringify({ reviewId: reviewId }, { flatId: flatId }),
  }).then((_res) => {
    window.location.href = "/flat-details/" + flatId;
  });
}

function unfavourite(favouriteID) {
  document.getElementById("favourite_button_id" + favouriteID.toString()).innerHTML = '<i class="fa-regular fa-heart"></i>';
  document.getElementById("favourite_button" + favouriteID.toString()).setAttribute( 'onClick', ("favourite(" + favouriteID.toString() + ")"));
  const fav_count = document.getElementById("favourite_count" + favouriteID.toString());
  fetch("/unfavourite",{
    method: "POST",
    body: JSON.stringify({ favouriteID:favouriteID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["favourite_count"];
  })
  .catch((e) => alert("Unable to Favourite"));
}

function favourite(flatID) {
  document.getElementById("favourite_button_id" + flatID.toString()).innerHTML = '<i class="fa-solid fa-heart"></i>';
  document.getElementById("favourite_button" + flatID.toString()).setAttribute( 'onClick', ("unfavourite(" + flatID.toString() + ")"));
  const fav_count = document.getElementById("favourite_count" + flatID.toString());
  fetch("/favourite",{
    method: "POST",
    body: JSON.stringify({ flatID:flatID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["favourite_count"];
  })
  .catch((e) => alert("Unable to Favourite"));
}

function favourite_count(flatID) {
  const fav_count = document.getElementById("favourite_count" + flatID.toString());
  fetch("/favourite_count",{
    method: "POST",
    body: JSON.stringify({ flatID:flatID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["favourite_count"];
    console.log("onload print this");
  })
}

function initialize() {
  var latitude = parseFloat(getElementById('latitude').value);
  var longitude = parseFloat(getElementById('longitude').value);
  console.log(latitude);
  console.log(longitude);
  const fenway = { lat: latitude, lng: longitude };
  const map = new google.maps.Map(document.getElementById("map"), {
    center: fenway,
    zoom: 14,
  });
  const panorama = new google.maps.StreetViewPanorama(
    document.getElementById("pano"),
    {
      position: fenway,
      pov: {
        heading: 34,
        pitch: 10,
      },
    }
  );

  map.setStreetView(panorama);
}