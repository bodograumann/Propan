# Create Custom **Propan** Broker

If you want to help me with the development of the project and develop **PropanBroker** for a not yet supported message broker from the [plan](../../#supported-mq-brokers) or you just want to expand the functionality of **Propan** for internal usage, this instruction can be very helphfull for you.

In this section, we will deal with the details of the implementation of brokers using examples already existing in **Propan**.

## Parent class

All brokers **Propan** are inherited from the parent class `propan.brokers.model.BrokerUsecase`.

In order to create a broker, it is necessary to inherit from this class and implement all its abstract methods.

```python linenums='1'
{!> docs_src/contributing/adapter/parent.py !}
```

Let's deal with everything in order.

## Connecting to a message broker

There are two key methods are responsible for your broker connection lifespan: `_connect` and `close`. After their implementation, the application with your adapter should start correctly and connect to a message broker (but not process messages).

### _connect

The `_connect` method initializes the connection to your message broker and returns the object of this connection, which will later be available as `self._connection`.

!!! tip
    If your broker requires additional objects initialization, you should also initialize them here.

```python linenums='1' hl_lines="8 17-19 24"
{!> docs_src/contributing/adapter/rabbit_connect.py !}
```

!!! note
    `args` and `kwargs` will be passed to your method from the  `__init__` or `connect` methods arguments. The logic of resolving these arguments is implemented in the parent class and you don't need to worry about.

Pay attention to the following lines: this place we initialize the `_channel` object specific to **RabbitBroker**.

```python linenums='8' hl_lines="3 14-15"
{!> docs_src/contributing/adapter/rabbit_connect.py [ln:7-24]!}
```

### close

Now we need to shut down our broker correctly. To do this, we implement the `close` method.

```python linenums='8' hl_lines="6-7 10-11"
{!> docs_src/contributing/adapter/rabbit_close.py !}
```

!!! note
    In the parent `connect` method, the implementation of the `_connect` method is called under the condition `self._connection is not None`, so it is important to set it to `None` after connection stopping.

After implementing these methods, an application with your broker should be runnable.

## Register handlers

In order for your broker to start processing messages, it is necessary to implement the handler registration method itself (`handle`) and the broker launch method (`start`).

Also, your broker must store information about all registered handlers, so you will need to implement a `Handler` class specific to each broker.

### handle

```python linenums='1' hl_lines="10-13 17 29-30"
{!> docs_src/contributing/adapter/rabbit_handle.py !}
```

In the selected fragments, we store information about registered handlers inside our broker.

Also, a very important point is to call the parent method `_wrap_handler` - it sets all decorators in right order that turns an original function into a **Propan** handler.

```python linenums='27' hl_lines="2"
{!> docs_src/contributing/adapter/rabbit_handle.py [ln:27-32] !}
```

### start

In the `start` method, we establish a connection to our message broker and perform all the necessary operations to launch our handlers.

Here is a somewhat simplified code for registering the `handlers`, however, it demonstrates the concept in full.

```python linenums='1' hl_lines="4 9"
{!> docs_src/contributing/adapter/rabbit_start.py !}
```

There are two possible options here:

* the library we use to work with the broker supports the `callbacks` mechanism (like *aio-pika* used for *RabbitMQ*)
* the library supports message iteration only

In the second case, we were less lucky and we need to convert a loop into a `callback`. This can be done, for example, using `asyncio.Task`, as in the *Redis* example. However, in this case, you should not forget to correctly cancel these tasks in the `close` method.

```python linenums='1' hl_lines="15 25-26 44 54"
{!> docs_src/contributing/adapter/redis_start.py !}
```

After that, your broker should send a received messages to the functions decorated with `handle`. However, while these functions will fall with an error.

## Processing incoming messages

In order for incoming messages to be processed correctly, two more methods must be implemented: `_parse_message` and `_process_message`.

### _parse_message

This method converts an incoming message to the **Propan** message type.

```python linenums='1' hl_lines="10-12"
{!> docs_src/contributing/adapter/rabbit_parse.py !}
```

In this case, only `body: bytes` and `raw_message: Any` are required fields. The remaining fields can be obtained both from an incoming message headers and from its body, if the message broker used does not have built-in mechanisms for transmitting the corresponding parameters. It all depends on your implementation of the `publish` method.

### _process_message

Everything is relatively simple here: if the message broker used supports the `ack`, `nack` mechanisms, then we should process them here. Also in this place, response publishing should be implemented to support **RPC over MQ**. If the broker does not support confirmation of message processing, then we simply execute our `handler`.

Here, for example, is an option with message status processing:

```python linenums='1' hl_lines="30"
{!> docs_src/contributing/adapter/rabbit_process.py !}
```

And without processing:

```python linenums='1' hl_lines="19"
{!> docs_src/contributing/adapter/redis_process.py !}
```

P.S: the following code is correct too, but without state processing and **RPC** supporting

```python
def _process_message(
    self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher]
) -> Callable[[PropanMessage], T]:
    @wraps(func)
    async def wrapper(message: PropanMessage) -> T:
        return await func(message)

    return wrapper
```

## Publishing messages

The last step we need to implement a sending messages method. This can be either the simplest stage (if we don't want or can't implement **RPC** right now) or the most complex and creative.

In the example below, I will omit the implementation of **RPC**, since each broker needs its own implementation. We will just send messages here.

```python linenums='1' hl_lines="21 23"
{!> docs_src/contributing/adapter/redis_publish.py !}
```

Congratulations, after implementing all these methods, you will have a broker capable of correctly sending and receiving messages.

## Logging

In order to log incoming messages in a broker specific format, you also need to override several methods.

First you need to reset the standard logging method by overriding the `__init__` method.

```python linenums='1' hl_lines="10"
{!> docs_src/contributing/adapter/rabbit_init.py !}
```

Then, you should define a logging format

```python linenums='1' hl_lines="17"
{!> docs_src/contributing/adapter/rabbit_fmt.py !}
```

The next step is to implement the `_get_log_context` method, which will add broker specific fields to log message.

```python linenums='1' hl_lines="17"
{!> docs_src/contributing/adapter/rabbit_get_log_context.py !}
```

This method always takes `message` as the first argument. You must pass other arguments there by yourself.

Where? - Right in the `handle` method

```python linenums='1' hl_lines="11 13-14"
    ...
    def handle(
        self,
        queue: RabbitQueue,
        exchange: Union[RabbitExchange, None] = None,
        *,
        retry: Union[bool, int] = False,
    ) -> HandlerWrapper:

        def wrapper(func: HandlerCallable) -> HandlerCallable:
            func = self._wrap_handler(
                func,
                queue=queue,
                exchange=exchange,
                retry=retry,
            )
            ....
```

All custom arguments passed to the `_wrap_handler` function will be further passed to your `_get_log_context` method.

Now your broker not only sends and receives messages, but also logs incoming messages in its own format. Congratulations, you are breathtaken!

!!! success
    If you have implemented a broker for your source I am waiting for your **PR**! I am ready to help you with testing, implementation of specific parts, documentation and everything else. Your work will definitely become a part of **Propan**.
