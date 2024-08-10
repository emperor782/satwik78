import zmq

context = zmq.Context()
msg_socket = context.socket(zmq.PULL)
msg_socket.bind("tcp://34.42.19.80:3000")


groups = {}  
print("Message Server is running...")

while True:
    
    message = msg_socket.recv_string().split()
    
    socket = context.socket(zmq.PUSH)
    socket.connect(message[0])
    
    if message[1] == "REGISTER":
        group_name, group_address = message[2], message[0]
        groups[group_name] = [group_address]  
        print(f"JOIN REQUEST FROM {message[2]} addr - {message[0]}")
        socket.send_string("SUCCESS")

    elif message[1] == "GROUP_LIST_REQUEST":
        group_list = ""
        for grp_name in groups.keys():
            group_list += grp_name
            group_list += " "
        socket.send_string(group_list)
        print(f"{message[1]} from {message[2]}\n")

    else:
        print("Invalid request")

