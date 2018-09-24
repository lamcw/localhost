/**
 * @file msocket.js
 * @author Jasper Lowell / @jtalowell
 * @date 24 Sep 2018
 * @brief File containing library interface and implementation for cooperative
 *        multiplex sockets.
 *
 * As the name 'cooperative multiplex sockets' implies, this library requires
 * a cooperative server. The protocol used is simple:
 * 	{
 *    'type': 'identifier',
 *    'data': {
 *      ...
 *    }
 *  }
 *
 * To handle messages of different types, specific handlers must be written
 * and then assigned using the object method provided.
 *
 * Failures are handled gracefully.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
 */

class MSocket {
  /**
   * @brief MSocket constructor
   *        Initialises the state of the MSocket
   *
   * @param url The url that the socket is binded to
   * */
  constructor(url) {
    this.url = url;
    this.socket = undefined;
    this.handlers = {};
  }

  /**
   * @brief Opens the socket and connects
   *
   * @return On success, @c true
   * @return On failure, @c false when the socket is already open
   * */
  open() {
    if (this.socket)
      return false;

    this.socket = new WebSocket(this.url);

    this.socket.onopen = function() {
      console.log('MSocket: connected.');
    }

    this.socket.onclose = function() {
      console.log('MSocket: disconnected.');
    }

    var handlers = this.handlers;
    this.socket.onmessage = function(message) {
      var parsed = JSON.parse(message.data);

      var type = parsed.type;
      var data = parsed.data;
      if (!type || !data) {
        console.log('MSocket: server abandoned protocol.');
        return;
      }

      var handler = handlers[type];
      if (!handler) {
        console.log('MSocket: no handler for recieved type.');
        return;
      }

      handler(data);
    }

    return true;
  }

  /**
   * @brief Closes the socket and disconnects
   *
   * @return On success, @c true
   * @retern On failure, @c false when the socket is not yet open
   * */
  close() {
    if (!this.socket)
      return false;

    this.socket.close();
    this.socket = undefined;

    return true;
  }

  /**
   * @brief Registers a handler for a message type
   *
   * @param type    The type of message the handler should apply to
   * @param handler The handler to execute on message recieve
   *                Should take the data as an argument
   *                See JSON specification
   *
   * @return On success, @c true
   * @return On failure, @c false when a handler is already set for the type
   * */
  register_handler(type, handler) {
    if (this.handlers[type]) {
      return false;
    }

    this.handlers[type] = handler;
    return true;
  }

  /**
   * @brief Unregisters a handler for a message type
   *
   * @param type The type of message to clear the handler for
   *
   * @return On success, @c true
   * @return On failure, @c false when there is no handler for the type
   * */
  unregister_handler(type) {
    if (!this.handlers[type]) {
      return false;
    }

    delete this.handlers[type];
    return true;
  }
}
