/**
 * @brief Binds a hide to the exit click for the modal
 * */
$(".view-item").on("click", function() {
  var targetID = $(this).data("target");
  if ($(window).width() < 992) {
    $(targetID).modal({backdrop: 'static'});
    $(targetID).on("hide.bs.modal", function() {$(".modal-close").hide()});
    $(".modal-close").show();
    $(".modal-close").one("click", function() {
      $(targetID).modal('hide');
      $(this).hide();
    });
  }
});
