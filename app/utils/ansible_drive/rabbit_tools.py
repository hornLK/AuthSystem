import pika
import sys


class RabbitTools():

    def __init__(self,server,port=5672):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=server,port=port
        ))
        self.channel = connection.channel()

    def publisher(self,message,exchange,routing_key,type="direct"):
        try:
            self.channel.exchange_declare(exchange=exchange,
                                        type=type)
            self.channel.basic_publish(exchange=exchange,
                                    routing_key=routing_key,
                                    body=message)
        except Exception as e:
            print(e)

        finally:
            self.connection.close()

    def subscriber(self,message,exchange,routing_key,type="direct"):
        pass
