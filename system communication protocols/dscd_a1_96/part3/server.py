import pika
import threading
import json

subscriptions = {}

def consume_user_requests():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='subscription_queue')
        
        def callback(ch, method, properties, body):
            try:
                message_data = json.loads(body.decode())
                if 'user' in message_data and 'youtuber' in message_data and 'subscribe' in message_data:
                    username = message_data['user']
                    action = "s" if message_data['subscribe'] else "u"
                    youtuber = message_data['youtuber']
                    if action == "s":
                        print(f"{username} subscribed to {youtuber}")
                        update_subscription(username, youtuber, True)
                    elif action == "u":
                        print(f"{username} unsubscribed from {youtuber}")
                        update_subscription(username, youtuber, False)
                    else:
                        print("Invalid action. Use 's' for subscribe or 'u' for unsubscribe.")
                else:
                    print("Received malformed message:", message_data)
            except Exception as e:
                print(f"Error processing message: {str(e)}")
        
        channel.basic_consume(queue='subscription_queue', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumption...")
        connection.close()

def consume_youtuber_requests():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='youtuber_requests')
        
        def callback(ch, method, properties, body):
            try:
                message_data = json.loads(body.decode())
                if 'youtuber' in message_data and 'videoName' in message_data:
                    youtuber = message_data['youtuber']
                    video_name = message_data['videoName']
                    print(f"{youtuber} uploaded {video_name}")
                    notify_users(youtuber, video_name)
                else:
                    print("Received malformed message:", message_data)
            except Exception as e:
                print(f"Error processing message: {str(e)}")
        
        channel.basic_consume(queue='youtuber_requests', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumption...")
        connection.close()



def notify_users(youtuber, video_name):
    try:
        if youtuber in subscriptions:
            for user in subscriptions[youtuber]:
                connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                channel = connection.channel()
                channel.queue_declare(queue='notification_queue')
                message = f"Notification: {youtuber} uploaded {video_name}"
                channel.basic_publish(exchange='', routing_key='notification_queue', body=message)
                print(f"Notification sent to {user}: {youtuber} uploaded {video_name}")
                connection.close()
    except Exception as e:
        print(f"Error notifying users: {str(e)}")



def update_subscription(username, youtuber, subscribed):
    if subscribed:
        if youtuber not in subscriptions:
            subscriptions[youtuber] = []
        subscriptions[youtuber].append(username)
    else:
        if youtuber in subscriptions and username in subscriptions[youtuber]:
            subscriptions[youtuber].remove(username)

if __name__ == '__main__':
    # Start two threads to handle user requests and youtuber requests simultaneously
    user_thread = threading.Thread(target=consume_user_requests)
    youtuber_thread = threading.Thread(target=consume_youtuber_requests)
    
    user_thread.start()
    youtuber_thread.start()
    
    # Wait for both threads to finish
    user_thread.join()
    youtuber_thread.join()
