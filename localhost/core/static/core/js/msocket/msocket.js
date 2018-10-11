/**
 * @file msocket.js
 * @author Jasper Lowell / @jtalowell
 * @date 24 Sep 2018
 * @brief File containing library interface and implementation for cooperative
 *        multiplex sockets. An additional client-server protocol helper class
 *        is also provided to manage general tasks such as placing a bid and
 *        subscribing to new groups.
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
    this.queue = [];
  }

  /**
   * @brief Opens the socket and connects
   *
   * @return On success, @c true
   * @return On failure, @c false when the socket is already open
   *
   * @note Sends any queued messages
   * */
  open() {
    if (this.socket)
      return false;

    this.socket = new WebSocket(this.url);

    var queue = this.queue;
    this.socket.onopen = function() {
      console.log('MSocket: connected.');
      while (queue.length > 0) {
        this.send(queue.shift());
      }
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
        console.log(parsed)
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

  /**
   * @brief Sends data through msocket
   *
   * @param type The identifier for the message
   * @param data The data of the message
   *
   * @note Messages are queued if the socket is not yet ready
   * @note It is up to the caller to obey any conventions for data structure
   * */
  send(type, data) {
    var message = JSON.stringify({
      'type': type,
      'data': data
    });

    if (this.socket.readyState !== 1) {
      this.queue.push(message);
    } else {
      this.socket.send(message);
    }
  }
}


class ClientSocket extends MSocket {
  /**
   * @brief Subscribes to a group
   *        Further messages to the group will be sent to the client socket
   *
   * @param group_class ['property_item', 'conversation']
   * @param id          The ID that together with the class identifies a unique group
   * */
  subscribe(group_class, id) {
    var payload = {
      'group': group_class + '_' + id
    };
    this.send('subscribe', payload);
  }

  /**
   * @brief Unsubscribes from a group
   *
   * @param group_class ['property_item', 'conversation']
   * @param id          The ID that together with the class identifies a
   *                    unique group
   * */
  unsubscribe(group_class, id) {
    var payload = {
      'group': group_class + '_' + id
    };
    this.send('unsubscribe', payload);
  }

  /**
   * @brief Bids on a property specified by its id
   *
   * @param property_item_id The id of the property item the bid is for
   * @param amount           The bid amount
   * */
  bid(property_item_id, amount) {
    var payload = {
      'property_item_id': property_item_id,
      'amount': amount
    };
    this.send('bid', payload);
  }

  /**
   * @brief Sends a message to a conversation
   *
   * @param conversation_id The id of the conversation the message should be
   *                        sent to
   * @param message         The message to be sent
   * */
  message(recipient_id, message) {
    var payload = {
      'recipient_id': recipient_id,
      'message': message
    };
    this.send('message', payload);
  }

  /**
   * @brief Sends a notification instruction
   *
   * @param notification_id The id of the notification the instruction
   *                        will operate on
   * @param instruction     The instruction to be executed
   * */
  notification(notification_id, instruction) {
    var payload = {
      'notification_id': notification_id,
      'instruction': instruction
    };
    this.send('notification', payload);
  }

  buyout(property_item_id) {
    var payload = {
      'property_item_id': property_item_id,
    };
    this.send('buyout', payload);
  }
}
