
import zmq
import uuid

context = zmq.Context()
message_socket = context.socket(zmq.PUSH)
message_socket.connect("tcp://34.42.19.80:3000")

group_socket = context.socket(zmq.PUSH)
group_socket.connect("tcp://35.193.191.76:3000")

user2_socket = context.socket(zmq.PULL)
user2_socket.bind("tcp://127.0.0.1:3000")

print("user'2' is running...")

def join_group(ip,group_name, user_id):
    group_socket.send_string(f"{ip} JOIN_GROUP {group_name} {user_id}")
    response = user2_socket.recv_string()
    print(response)

def leave_group(ip,group_name, user_id):
    group_socket.send_string(f"{ip} LEAVE_GROUP {group_name} {user_id}")
    resp = user2_socket.recv_string()
    print(resp)
    
def get_group_list(ip,uuid):
    message_socket.send_string(f"{ip} GROUP_LIST_REQUEST {uuid}")
    group_list = user2_socket.recv_string()
    list = group_list.split()
    print("printing groups list...")
    print(group_list)
    
def send_message(ip,group_name, user_id, message):
    group_socket.send_string(f"{ip} SEND_MESSAGE {group_name} {user_id} {message}")
    resp = user2_socket.recv_string()
    print(resp)

def get_messages(ip,group_name, user_id, times):
    group_socket.send_string(f"{ip} GET_MESSAGES {group_name} {user_id} {times}")
    resp = user2_socket.recv_string()
    msgs = resp.split()
    print(msgs)

if __name__ == "__main__":
    ip = "tcp://127.0.0.1:3000"
    f = True
    user_id = str(uuid.uuid1())
    while f:
        print(f"hi user2 {user_id} !")
        print("\nChoose an action:")
        print("\n1. Get list of groups")
        print("\n2. join group")
        print("\n3. Send a message")
        print("\n4. Get messages")
        print("\n5. Leave the group")
        print("\n6. exit")
        choice = input("Enter your choice : ")

        if choice == "1":
            get_group_list(ip,user_id)
        
        elif choice == "2": #join
            group_name = input("Enter the name of the group you want to join: ")
            #u_id = str(uuid.uuid1())
            join_group(ip,group_name, user_id)
        
        elif choice == "3": #send
            group_name = input("enter group name you want to message: ")
            message = input("Enter your message: ")
            send_message(ip,group_name, user_id, message)
        
        elif choice == "4": #getmessage
            group_name = input("enter group name: ")
            times = input("Enter the timestamp(Y M D H Min Sec) (optional, type NA for all messages): ")
            get_messages(ip,group_name, user_id, times)
            
        elif choice == "5": #leave
            grp_name = input("enter group name you want to leave: ")
            leave_group(ip,grp_name, user_id)
            
        else:
            print("exited")
            f= False

