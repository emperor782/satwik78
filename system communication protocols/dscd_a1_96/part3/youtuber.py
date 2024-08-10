import sys
import pika
import json

class Youtuber:
    def __init__(self):
        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()

    def publishVideo(self, youtuber, videoName):
        if not hasattr(self, 'connection'):
            self.connect()
        
        message = {
            "youtuber": youtuber,
            "videoName": videoName
        }
        message_json = json.dumps(message)  # Convert message to JSON string
        self.channel.basic_publish(exchange='', routing_key='youtuber_requests', body=message_json)
        print("SUCCESS")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Youtuber.py [Youtuber's Name] [Video Name]")
        sys.exit(1)
    
    youtuber_name = sys.argv[1]
    video_name = sys.argv[2]
    
    youtuber = Youtuber()
    youtuber.publishVideo(youtuber_name, video_name)
