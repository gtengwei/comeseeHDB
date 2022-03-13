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
  fetch("/unfavourite",{
    method: "POST",
    body: JSON.stringify({ favouriteID:favouriteID }),
  }).then((_res) => {
    window.location.hreft = "/";
  });
}

function favourite(flatID) {
  document.getElementById("favourite_button_id" + flatID.toString()).innerHTML = '<i class="fa-solid fa-heart"></i>';
  document.getElementById("favourite_button" + flatID.toString()).setAttribute( 'onClick', ("unfavourite(" + flatID.toString() + ")"));
  fetch("/favourite",{
    method: "POST",
    body: JSON.stringify({ flatID:flatID }),
  }).then((_res) => {
    window.location.hreft = "/";
  });
}