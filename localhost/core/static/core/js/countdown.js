/**
 * @brief Injects a countdown onto the page
 *
 * @param inject_class  The class of the element to inject the countdown in
 * @param datetime      The date and time to countdown to
 * @param finish_string The string to write once finished
 *
 * @note Updates the countdown every second
 * @note Once the time is reached, writes CLOSED
 * */
function register_countdown(inject_class, datetime, finish_string) {
  var interval = setInterval(function() {
    var current_datetime = new Date().getTime();
    if (datetime < current_datetime) {
      $('#' + inject_class).html(finish_string);
      return;
    }

    var distance = datetime - current_datetime;
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    $('.' + inject_class).html(days + "d " + hours + "h " + minutes + "m " + seconds + " seconds ");

  }, 1000);
}
