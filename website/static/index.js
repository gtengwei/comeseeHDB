function deleteReview(reviewId,flatId) {
  fetch("/delete-review", {
    method: "POST",
    body: JSON.stringify({ reviewId: reviewId }, { flatId: flatId }),
  }).then((_res) => {
    window.location.href = "/flat-details/" + flatId;
  });
}

function unfavourite(favouriteID) {
  fetch("/unfavourite",{
    method: "POST",
    body: JSON.stringify({ favouriteID:favouriteID }),
  }).then((_res) => {
    window.location.hreft = "/";
  });
}

function favourite(flatID) {
  fetch("/favourite",{
    method: "POST",
    body: JSON.stringify({ flatID:flatID }),
  }).then((_res) => {
    window.location.hreft = "/";
  });
}