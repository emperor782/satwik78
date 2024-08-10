import pytz
from datetime import datetime
import zmq
import threading

context = zmq.Context()

message_socket = context.socket(zmq.PUSH)
message_socket.connect("tcp://10.128.0.4:3000")


grp_socket = context.socket(zmq.PULL)
grp_socket.bind("tcp://35.193.191.76:3000")

print("group Server is running...")

groups = {}

def register(group_name, group_addr):
    message_socket.send_string(f"{group_addr} REGISTER {group_name}")
    groups[group_name] = [[], []]
    response = grp_socket.recv_string()
    print(response)


def get_messages(ip,group_name, user_id, u_times):
    user_socket = context.socket(zmq.PUSH)
    user_socket.connect(ip)
    
    if (group_name in groups) and (user_id in groups[group_name][0]):
        if (u_times != "NA") and (len(u_times.split()) == 6):
            ts = u_times.split()
            messages = ""

            for grp_name in groups[group_name][1]:
                li = grp_name.split(":")
                tl = li[0].split()
                if datetime(int(tl[0]), int(tl[1]), int(tl[2]), int(tl[3]), int(tl[4]), int(tl[5])) >= datetime(
                        int(ts[0]), int(ts[1]), int(ts[2]), int(ts[3]), int(ts[4]), int(ts[5])):
                    messages += li[1]
                    messages += " "
            user_socket.send_string(messages)
            print(f"Message request from {user_id}")
        else:
            messages = ""
            for grp_name in groups[group_name][1]:
                li = grp_name.split(":")
                messages += li[1]
                messages += " "
            user_socket.send_string(messages)
            print(f"Message request from {user_id}")
    else:
        user_socket.send_string("Fail")


def handle_user_request():
    while True:
        message = grp_socket.recv_string().split()
        
        user_socket = context.socket(zmq.PUSH)
        user_socket.connect(message[0])
        
        if message[1] == "JOIN_GROUP":
            group_name, user_id = message[2], message[3]
            if (group_name in groups) and (user_id not in groups[group_name][0]):
                groups[group_name][0].append(user_id)  
                print(f"User {user_id} joined group {group_name}")
                user_socket.send_string("SUCCESS")
            else:
                user_socket.send_string("Group not found")

        elif message[1] == "LEAVE_GROUP":
            group_name, user_id = message[2], message[3]
            if group_name in groups and user_id in groups[group_name][0]:
                groups[group_name][0].remove(user_id)  
                print(f"User {user_id} left group {group_name}")
                user_socket.send_string("SUCCESS")
            else:
                user_socket.send_string("User or group not found")

        elif message[1] == "SEND_MESSAGE":
            if (message[2] in groups) and (message[3] in groups[message[2]][0]):
                utc_now = datetime.utcnow()
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_timezone)
                time = ist_now.strftime("%Y %m %d %H %M %S")
                groups[message[2]][1].append(time + ":" + message[4])
                print(f"Message sent from {message[3]}")
                user_socket.send_string("SUCCESS")
            else:
                user_socket.send_string("you can't send message")

        elif message[1] == "GET_MESSAGES":
            get_messages(message[0],message[2], message[3], message[4])


def start_user_handler():
    while True:
            print("hello group admin\n")
            print("press 1 if you want to reg or 2 otherwise\n")
            choice = input("Enter your choice : ")
            if choice == "1":
                grp_name = input("\nenter group name: ")
                register(grp_name, "tcp://10.128.0.2:3000")

            elif choice == "2":
                break
    user_thread = threading.Thread(target=handle_user_request)
    user_thread.start()


start_user_handler()
