import sys
import pika
import json

class User:
    def __init__(self, username):
        self.username = username
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='notification_queue')  # Queue for receiving notifications
        self.channel.queue_declare(queue='subscription_queue')

    def updateSubscription(self, youtuber, subscribe):
        message = {
            "user": self.username,
            "youtuber": youtuber,
            "subscribe": subscribe
        }
        message_json = json.dumps(message)  # Convert message to JSON string
        self.channel.basic_publish(exchange='', routing_key='subscription_queue', body=message_json)
        print("SUCCESS")

    def receiveNotifications(self):
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode())
                print("New Notification:", message)
            except json.decoder.JSONDecodeError:
                print("New ", body.decode())

        self.channel.basic_consume(queue='notification_queue', on_message_callback=callback, auto_ack=True)
        print("Waiting for notifications. To exit press CTRL+C")
        self.channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) not in [2, 4]:
        print("Usage: python User.py [Username] [s/u YouTuberName]")
        sys.exit(1)
    
    username = sys.argv[1]
    user = User(username)
    
    if len(sys.argv) == 4:
        action = sys.argv[2]
        youtuber = sys.argv[3]
        if action == "s":
            user.updateSubscription(youtuber, True)
        elif action == "u":
            user.updateSubscription(youtuber, False)
        else:
            print("Invalid action. Use 's' for subscribe or 'u' for unsubscribe.")
            sys.exit(1)

    user.receiveNotifications()
