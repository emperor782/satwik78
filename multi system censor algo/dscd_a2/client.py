import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://127.0.0.1:*")

#ip_addr = {"1": "127.0.0.1:1" , "2":"127.0.0.1:2", "3":"127.0.0.1:3", "4":"127.0.0.1:4", "5":"127.0.0.1:5"  }

message = socket.recv_json()

def get(k):
    leader.send_json({"type": "ClientRequest", "operation": "GET", "key": k})
    message = leader.recv_json()
    print(f"{message["status"]}\n")
    print(f"{message["message"]}")
    
def set(k,v):
    leader.send_json({"type": "ClientRequest", "operation": "SET", "key": k, "value": v})
    message = leader.recv_json()
    print(f"{message["status"]}\n")
    print(f"{message["message"]}")
    
if __name__ == "__main__":
    while(True):
        leader_addr = message["addr"]
        leader = context.socket(zmq.REQ)
        leader.bind(f"{leader_addr}")
        
        print("choose operation\n1)get\n2)set\n3)exit")
        choice = input("Enter your choice : ")
        if(choice == "1"):
            k = input("enter key whose value to be displayed: ")
            get(k)
        elif(choice=="2"):
            k = input("enter key: ")
            v= input("enter value: ")
            set(k,v)
        else:
            print("exited!")
            break
