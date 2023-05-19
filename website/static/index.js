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
function flat_unlike(likeID) {
  const fav_count = document.getElementById("like_count" + likeID.toString());
  fetch("/flat_unlike",{
    method: "POST",
    body: JSON.stringify({ likeID:likeID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["like_count"];
    document.getElementById("like_button_id" + likeID.toString()).innerHTML = '<i class="fa-regular fa-heart"></i>';
    document.getElementById("like_button" + likeID.toString()).setAttribute( 'onClick', ("flat_like(" + likeID.toString() + ")"));
  })
  .catch((e) => click_like_button());
}


// To like a flat
function flat_like(flatID) {
  const fav_count = document.getElementById("like_count" + flatID.toString());
  fetch("/flat_like",{
    method: "POST",
    body: JSON.stringify({ flatID:flatID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["like_count"];
    document.getElementById("like_button_id" + flatID.toString()).innerHTML = '<i class="fa-solid fa-heart"></i>';
    document.getElementById("like_button" + flatID.toString()).setAttribute( 'onClick', ("flat_unlike(" + flatID.toString() + ")"));
  })
  .catch((e) => click_like_button());
}

// To unlike a property
function property_unlike(likeID) {
  const fav_count = document.getElementById("like_count" + likeID.toString());
  fetch("/prop_unlike",{
    method: "POST",
    body: JSON.stringify({ likeID:likeID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["like_count"];
    document.getElementById("like_button_id" + likeID.toString()).innerHTML = '<i class="fa-regular fa-heart"></i>';
    document.getElementById("like_button" + likeID.toString()).setAttribute( 'onClick', ("property_like(" + likeID.toString() + ")"));
  })
  .catch((e) => click_like_button());
}


// To like a property
function property_like(propID) {
  const fav_count = document.getElementById("like_count" + propID.toString());
  fetch("/prop_like",{
    method: "POST",
    body: JSON.stringify({ propID:propID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["like_count"];
    document.getElementById("like_button_id" + propID.toString()).innerHTML = '<i class="fa-solid fa-heart"></i>';
    document.getElementById("like_button" + propID.toString()).setAttribute( 'onClick', ("property_unlike(" + propID.toString() + ")"));
  })
  .catch((e) => click_like_button());
}


// To get the like count of a flat
function like_count(flatID) {
  const fav_count = document.getElementById("like_count" + flatID.toString());
  fetch("/flat_like_count",{
    method: "POST",
    body: JSON.stringify({ flatID:flatID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["like_count"];
    console.log("onload print this");
  })
}

// To get the like count of a property
function property_like_count(propID) {
  const fav_count = document.getElementById("like_count" + propID.toString());
  fetch("/prop_like_count",{
    method: "POST",
    body: JSON.stringify({ propID:propID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["like_count"];
    console.log("onload print this");
  })
}

// To unlike a review
function review_unlike(reviewID) {
  document.getElementById("review_like_button_id" + reviewID.toString()).innerHTML = '<i class="fa-regular fa-heart"></i>';
  document.getElementById("review_like_button" + reviewID.toString()).setAttribute( 'onClick', ("review_like(" + reviewID.toString() + ")"));
  const fav_count = document.getElementById("review_like_count" + reviewID.toString());
  fetch("/review_unlike",{
    method: "POST",
    body: JSON.stringify({ reviewID:reviewID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["review_like_count"];
  })
  .catch((e) => alert("Unable to Unlike"));
}


// To like a review
function review_like(reviewID) {
  document.getElementById("review_like_button_id" + reviewID.toString()).innerHTML = '<i class="fa-solid fa-heart"></i>';
  document.getElementById("review_like_button" + reviewID.toString()).setAttribute( 'onClick', ("review_unlike(" + reviewID.toString() + ")"));
  const fav_count = document.getElementById("review_like_count" + reviewID.toString());
  fetch("/review_like",{
    method: "POST",
    body: JSON.stringify({ reviewID:reviewID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["review_like_count"];
  })
  .catch((e) => alert("Unable to like"));
}


// To get the like count of a review
function review_like_count(reviewID) {
  const fav_count = document.getElementById("review_like_count" + reviewID.toString());
  fetch("/review_like_count",{
    method: "POST",
    body: JSON.stringify({ reviewID:reviewID }) })
    .then((res) => res.json())
    .then((data) => { 
    fav_count.innerHTML = data["review_like_count"];
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
function click_like_button(){
  $("#createAccountModal").modal('show');
}

function sortCheck(){
    $('.form-check-input.sort-check').click(function() {
      $('.form-check-input.sort-check').not(this).prop('checked', false);
  });
  sleep(5).then(() => {
    updateFilterPlaceholder('sort');
});
}

function updateFilterPlaceholder(filter){
  if (filter == 'priceRange'){
    var checkboxes = document.getElementsByName('priceRange[]');
    var vals = [];
    for (var i=0, n=checkboxes.length;i<n;i++)
    {
        if (checkboxes[i].checked)
        {
            vals.push(checkboxes[i].value)
        }
    }
    console.log(vals)
    document.getElementById("priceRange").textContent = vals
    if (vals === undefined || vals.length == 0){
      document.getElementById("priceRange").textContent = "Select price range"
    }
  }
  else if (filter == 'flatType'){
    var checkboxes = document.getElementsByName('flatType[]');
    var vals = [];
    for (var i=0, n=checkboxes.length;i<n;i++)
    {
        if (checkboxes[i].checked)
        {
            vals.push(checkboxes[i].value)
        }
    }
    console.log(vals)
    document.getElementById("flatType").textContent = vals
    if (vals === undefined || vals.length == 0){
      document.getElementById("flatType").textContent = "Select flat type"
    }
  }
  
  else if (filter == 'town'){
    var checkboxes = document.getElementsByName('town[]');
    var vals = [];
    for (var i=0, n=checkboxes.length;i<n;i++)
    {
        if (checkboxes[i].checked)
        {
            vals.push(checkboxes[i].value)
        }
    }
    console.log(vals)
    document.getElementById("town").textContent = vals
    if (vals === undefined || vals.length == 0){
      document.getElementById("town").textContent = "Select town"
    }
  }

  else if (filter == 'sort'){
    var checkboxes = document.getElementsByName('sortingCriteria[]');
    var vals = [];
    for (var i=0, n=checkboxes.length;i<n;i++) 
    {
        if (checkboxes[i].checked) 
        { 
            vals.splice(0,0,checkboxes[i].value);
        }
    }
    console.log(vals)
    document.getElementById("sortingCriteria").textContent = vals[0]
    if (vals === undefined || vals.length == 0){
      document.getElementById("sortingCriteria").textContent = "Select sorting criteria"
    }
  }
}

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}