import pika
import ansibleApi_test

class AnsibleRabbitmqRpcServer():

    def __init__(self,host,vhost,queue,port=5672):
        self.queue = queue
        conn = pika.BlockingConnection(pika.ConnectionParameters(
                                                                host=host,
                                                                virtual_host=vhost,
                                                                port=port
                                                                ))
        self.channel = conn.channel()

    def start_ansible_rpcserver(self):
        self.channel.queue_declare(queue=self.queue)
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(self.on_ansible_request, queue=self.queue)
        print("启动Ansible RPC Server")
        self.channel.start_consuming()

    def on_ansible_request(self,ch, method, props, body):
        response = ansibleApi_test.main()
        ch.basic_publish(exchange='',
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(correlation_id = \
                                                    props.correlation_id),
                                                    body=str(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__ == "__main__":
    rpcServer = AnsibleRabbitmqRpcServer("127.0.0.1","ansible","rpc_queue")
    rpcServer.start_ansible_rpcserver()
