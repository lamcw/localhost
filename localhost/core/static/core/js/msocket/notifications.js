function listen_notifications(csocket) {
  var notification_handler = function(data) {
    /* Removing the "None" placeholder from notifications */
    empty = $('#notification-none');
    if (empty.length) {
      $(empty).remove();
    }

    /* Appending notification */
    $('#notifications .dropdown-menu').append('<div class="d-flex flex-row"> <a class="dropdown-item" href="'
      + data.url + '">' + data.message + '</a> <button id="button-notification-'
      + data.id + '" class="notification-btn btn btn-primary" style="color:black !important;">clear</button> </div>'
    );
  }

  csocket.register_handler('notification', notification_handler);

  $('.notification-btn').click(function() {
    var notification = $(this).attr('id');
    var notification_id = notification.match(/\d+$/)[0];
    csocket.notification(notification_id, 'clear');
    $(this).parent().remove();
  });
}
