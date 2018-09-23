/**
 * @brief Creates a multiplex socket
 *
 *        A multiplex socket contains a regular socket and a dictionary of
 *        registered handlers. The key is the response type to watch for
 *        and the value is the function to execute when that key is seen.
 *
 *        This requires an established protocol between the server and the
 *        client. The only constraint of using this library is that the lowest
 *        level must be a JSON object of the following form:
 *
 *        {
 *          "type": key,
 *          "data": {
 *            ...
 *          }
 *        }
 *
 * @param url The url the server is listening to
 *
 * @method msocket.send(type, data)
 * */
function msocket_create(url) {
  var msocket {
    var socket = new WebSocket(url)
    var handlers = {};
  };

  msocket.socket.onopen(function() {
    console.log('Connected to server.');
  });

  msocket.socket.onclose(function() {
    console.log('Disconnected from server.');
  });

  msocket.socket.onmessage(function(message) {
    var response = JSON.parse(message.data);

    if (response.type && response.data) {
      var type = response.type;
      var data = response.data;

      var handler = msocket.handlers[type];
      if (handler !== undefined) {
        console.log('Error: No response handler registered for this type.');
      } else {
        handler(data);
      }
    } else {
      console.log('Error: Server abandoned the msocket protocol.');
    }
  });

  msocket.send(function(type, data) {
    var message = {
      'type': type,
      'data': data
    };
    msocket.socket.send(JSON.stringify(message));
  });

  return msocket;
}

/**
 * @brief Closes a multiplex socket
 *
 * @param msocket
 * */
function msocket_close(msocket) {
  msocket.socket.close();
}

/**
 * @brief Registers a handler for the multiplex socket
 *
 * @param msocket The multiplex socket
 * @param type    The type to listen for
 * @param handler The handler to execute when @p type is recieved
 *
 * @return true  On success
 * @return false On failure, when the type already has a handler
 * */
function msocket_register_handler(msocket, type, handler) {
  if (msocket.handlers[type] !== undefined) {
    msocket.hanlders[type] = handler;
    return true;
  }
  return false;
}
