/**
 * @brief Initialises a client socket
 *
 * @return The client socket
 * */
function init_realtime() {
  var uri = window.location.protocol === "https:" ? "wss" : "ws";
  var csocket = new ClientSocket(uri + '://' + window.location.host + '/ws/realtime/');
  csocket.open();
  return csocket;
}
