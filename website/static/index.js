function deleteReview(reviewId) {
  fetch("/delete-review", {
    method: "POST",
    body: JSON.stringify({ reviewId: reviewId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

