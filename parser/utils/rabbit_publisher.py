# coding=utf-8
# __author__ = 'Mio'
import json

import pika
from pika import adapters
from tornado.ioloop import IOLoop
from tornado.log import app_log
from tornado.escape import native_str

from parser.settings import RABBIT_URL, RABBIT_USER, RABBIT_PASSWORD, RABBIT_HOST, RABBIT_PORT, RABBIT_EXCHANGE, \
    RABBIT_EXCHANGE_TYPE, RABBIT_PARSED_QUEUE, RABBIT_PARSED_ROUTING_KEY


# EXCHANGE = 'direct_one_exchange'
# EXCHANGE_TYPE = 'direct'
# QUEUE = 'PUB_INIT_Q'
# ROUTING_KEY = 'PUB_INIT_Q'


# noinspection PyUnusedLocal
class Publisher(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """

    def __init__(self, amqp_url, exchange, exchange_type, queue, routing_key):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self._connection = None
        self._channel = None
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0
        self._stopping = False
        self._url = amqp_url
        self._closing = False

        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.routing_key = routing_key

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        app_log.info('Connecting to %s', self._url)
        return adapters.TornadoConnection(pika.URLParameters(self._url),
                                          self.on_connection_open,
                                          custom_ioloop=IOLoop.current())

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        app_log.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        app_log.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            app_log.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                            reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

        self._connection = self.connect()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.

        """
        app_log.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        app_log.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.exchange, self.exchange_type)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        app_log.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        app_log.warning('Channel %i was closed: (%s) %s',
                        channel, reply_code, reply_text)
        if not self._closing:
            self._connection.close()

    def setup_exchange(self, exchange_name, exchange_type):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param exchange_type:
        :param str|unicode exchange_name: The name of the exchange to declare

        """
        app_log.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok, exchange_name, exchange_type,
                                       durable=True)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        app_log.info('Exchange declared')
        self.setup_queue(self.queue)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        app_log.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name, durable=True)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        """
        self.bind_queue(queue=self.queue, exchange=self.exchange, routing_key=self.routing_key)

    def bind_queue(self, queue, exchange, routing_key):
        app_log.info('Binding %s to %s with %s',
                     self.exchange, self.queue, self.routing_key)
        self._channel.queue_bind(self.on_bindok, self.queue,
                                 self.exchange, self.routing_key)

    def switch_queue(self, queue_name, routing_key=None, exchange_name=None, exchange_type=None):
        kwargs = dict(queue=queue_name, routing_key=routing_key, exchange=exchange_name, exchange_type=exchange_type)

        changed = False
        for k, v in kwargs.items():
            if v and getattr(self, k) != v:
                changed = True
                setattr(self, k, v)

        if changed is True:
            self.setup_exchange(exchange_name=self.exchange, exchange_type=self.exchange_type)

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame

        """
        app_log.info('Queue bound')
        # self.publish_message({"type": "app online"})

    def start_publishing(self):
        """This method will enable delivery confirmations and schedule the
        first message to be sent to RabbitMQ

        """
        app_log.info('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()
        # self.first_msg_pub_rabbit()

    def enable_delivery_confirmations(self):
        """Send the Confirm.Select RPC method to RabbitMQ to enable delivery
        confirmations on the channel. The only way to turn this off is to close
        the channel and create a new one.

        When the message is confirmed from RabbitMQ, the
        on_delivery_confirmation method will be invoked passing in a Basic.Ack
        or Basic.Nack method from RabbitMQ that will indicate which messages it
        is confirming or rejecting.

        """
        app_log.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        """Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
        command, passing in either a Basic.Ack or Basic.Nack frame with
        the delivery tag of the message that was published. The delivery tag
        is an integer counter indicating the message number that was sent
        on the channel via Basic.Publish. Here we're just doing house keeping
        to keep track of stats and remove message numbers that we expect
        a delivery confirmation of from the list used to keep track of messages
        that are pending confirmation.

        :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

        """
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        app_log.info('Received %s for delivery tag: %i',
                     confirmation_type,
                     method_frame.method.delivery_tag)
        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1
        self._deliveries.remove(method_frame.method.delivery_tag)
        app_log.info('Published %i messages, %i have yet to be confirmed, '
                     '%i were acked and %i were nacked',
                     self._message_number, len(self._deliveries),
                     self._acked, self._nacked)

    # def first_msg_pub_rabbit(self):
    #     self.publish_message({"type": "app join"}, )

    def publish_message(self, msg, queue=None, **kwargs):
        """
        发布消息
        :param queue:
        :param msg:
        :param kwargs:
        :return:
        """
        if self._stopping:
            return
        # if switch queue
        if queue and queue != self.queue:
            self.switch_queue(queue, **kwargs)
        if isinstance(msg, bytes):
            msg = native_str(msg)
        elif isinstance(msg, dict):
            msg = json.dumps(msg, ensure_ascii=False)
        elif isinstance(msg, list):
            msg = json.dumps(msg, ensure_ascii=False)
        else:
            msg = msg

        properties = pika.BasicProperties(app_id="mysql-parser-publish",
                                          content_type='application/json')

        self._channel.basic_publish(self.exchange, self.routing_key, msg, properties)
        self._message_number += 1
        self._deliveries.append(self._message_number)
        app_log.info('Published message # {} to queue: {}'.format(self._message_number, self.queue))

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.

        """
        app_log.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.

        """
        self._connection = self.connect()
        return self
        # self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        app_log.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()
        self._connection.ioloop.start()
        app_log.info('Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        app_log.info('Closing connection')
        self._closing = True
        self._connection.close()


def publisher():
    _publisher = Publisher(RABBIT_URL.format(
        user=RABBIT_USER, password=RABBIT_PASSWORD, host=RABBIT_HOST, port=RABBIT_PORT),
        exchange=RABBIT_EXCHANGE, exchange_type=RABBIT_EXCHANGE_TYPE,
        queue=RABBIT_PARSED_QUEUE, routing_key=RABBIT_PARSED_ROUTING_KEY)

    try:
        return _publisher.run()
    except KeyboardInterrupt:
        _publisher.stop()


raw_data_pubber = publisher()

if __name__ == '__main__':
    publisher()
