/**
 * @brief Used to listen to notifications and update the notifications dropdown
 *
 * @param csocket The socket that notifications are listened to on
 * */
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
    $('#button-notification-' + data.id).click(notification_clear_handler);
    $('#notifications').css('background-color', 'var(--accent)');
  }

  csocket.register_handler('notification', notification_handler);
  $('.notification-btn').click(notification_clear_handler);
}

/**
 * @brief Handler used to clear a notification.
 * */
function notification_clear_handler() {
  var notification = $(this).attr('id');
  var notification_id = notification.match(/\d+$/)[0];
  csocket.notification(notification_id, 'clear');
  $(this).parent().remove();
  check_empty_notifications();
}

/**
 * @brief Check if there are any empty notifictions and update dropdown accordingly.
 * */
function check_empty_notifications() {
  var notif_dropdown = $('#notifications .dropdown-menu');
  if (notif_dropdown.children().length == 0) {
    $(notif_dropdown.append('<a id="notification-none" class="dropdown-item">None</a>'));
    $('#notifications').css('background-color', 'transparent');
  }
}
