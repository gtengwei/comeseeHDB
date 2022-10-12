// To delete reviews
function deleteReview(reviewId,flatId) {
  fetch("/delete-review", {
    method: "POST",
    body: JSON.stringify({ reviewId: reviewId }, { flatId: flatId }),
  }).then((_res) => {
    window.location.href = "/flat-details/" + flatId;
  });
}


// To unlike a flat
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
  .catch((e) => click_favourite_button());
}


// To like a flat
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
  .catch((e) => click_favourite_button());
}


// To get the like count of a flat
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


// To unlike a review
function review_unfavourite(reviewID) {
  document.getElementById("review_favourite_button_id" + reviewID.toString()).innerHTML = '<i class="fa-regular fa-heart"></i>';
  document.getElementById("review_favourite_button" + reviewID.toString()).setAttribute( 'onClick', ("review_favourite(" + reviewID.toString() + ")"));
  const fav_count = document.getElementById("review_favourite_count" + reviewID.toString());
  fetch("/review_unfavourite",{
    method: "POST",
    body: JSON.stringify({ reviewID:reviewID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["review_favourite_count"];
  })
  .catch((e) => alert("Unable to UnFavourite"));
}


// To like a review
function review_favourite(reviewID) {
  document.getElementById("review_favourite_button_id" + reviewID.toString()).innerHTML = '<i class="fa-solid fa-heart"></i>';
  document.getElementById("review_favourite_button" + reviewID.toString()).setAttribute( 'onClick', ("review_unfavourite(" + reviewID.toString() + ")"));
  const fav_count = document.getElementById("review_favourite_count" + reviewID.toString());
  fetch("/review_favourite",{
    method: "POST",
    body: JSON.stringify({ reviewID:reviewID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["review_favourite_count"];
  })
  .catch((e) => alert("Unable to Favourite"));
}


// To get the like count of a review
function review_favourite_count(reviewID) {
  const fav_count = document.getElementById("review_favourite_count" + reviewID.toString());
  fetch("/review_favourite_count",{
    method: "POST",
    body: JSON.stringify({ reviewID:reviewID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["review_favourite_count"];
    console.log("onload print this");
  })
}


// Google Street View
window.onload = function initialize() {
  console.log(parseFloat(document.getElementById("latitude").innerHTML));
  var latitude = parseFloat(document.getElementById("latitude").innerHTML);
  var longitude = parseFloat(document.getElementById("longitude").innerHTML);
  console.log(latitude);
  const fenway = { lat:latitude, lng:longitude };
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


// To display reply form
function reply(reviewId){
  var x = document.getElementById(`reply-${reviewId}`);
  var y = document.getElementById(`reply_submit_button-${reviewId}`);
  //console.log(review)
  //console.log(x);
  if (x.style.display === "none") {
    x.style.display = "block";
    y.style.display = "block";
  } else {
    x.style.display = "none";
    y.style.display = "none";
  }
}


// To display create account modal for guests
function click_favourite_button(){
  $('.favourite_button').click(function(){
    $("#createAccountModal").modal('show');
  });
}
