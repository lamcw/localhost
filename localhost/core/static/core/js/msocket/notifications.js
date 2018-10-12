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
    $('#notifications').css('background-color', 'var(--accent)');
    check_empty_notifications();
  }

  notification_handler({
    'id': 1337,
    'message': 'sparta',
    'url': 'https://bitbucket.com/'
  });

  csocket.register_handler('notification', notification_handler);

  $('.notification-btn').click(function() {
    var notification = $(this).attr('id');
    var notification_id = notification.match(/\d+$/)[0];
    csocket.notification(notification_id, 'clear');
    $(this).parent().remove();
    check_empty_notifications();
  });
}

function check_empty_notifications() {
  var notif_dropdown = $('#notifications .dropdown-menu');
  if (notif_dropdown.children().length == 0) {
    $(notif_dropdown.append('<a id="notification-none" class="dropdown-item">None</a>'));
    $('#notifications').css('background-color', 'transparent');
  }
}
