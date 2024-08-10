import os
import time
import json
import zmq
import threading
import random

context = zmq.Context()
client = context.socket(zmq.REP)
client.bind("tcp://127.0.0.1:555")

sock = context.socket(zmq.PULL)
sock.bind("tcp://0.0.0.0")

node2 = context.socket(zmq.PUSH)
node2.connect("tcp://127.0.0.1:2")

node3 = context.socket(zmq.PUSH)
node3.connect("tcp://127.0.0.1:3")

node4 = context.socket(zmq.PUSH)
node4.connect("tcp://127.0.0.1:4")

node5 = context.socket(zmq.PUSH)
node5.connect("tcp://127.0.0.1:5")

class RaftNode:
    def __init__(self, node_id, total_nodes):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.state = "Follower"
        self.current_leader = None
        self.current_term = 0
        self.votes = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {i: len(self.log) + 1 for i in range(1, self.total_nodes + 1)}
        self.match_index = {i: 0 for i in range(1, self.total_nodes + 1)}
        self.leader_lease_timeout = None
        self.token = False
        self.heartbeat_interval = 1
        self.lease_duration = 5  # in seconds
        self.leader_lease_duration = 10  # in seconds
        self.timeout = random.uniform(5, 10)
        self.max_old_leader_lease = 0

        self.db = {}
        self.logs_directory = f"logs_node_{self.node_id}"
        self.logs_file = f"{self.logs_directory}/logs.txt"
        self.metadata_file = f"{self.logs_directory}/metadata.json"
        self.dump_file = f"{self.logs_directory}/dump.txt"
        self.load_logs_and_metadata()

        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)

        self.election_timer = None
        self.leader_lease_thread = threading.Thread(target=self.leader_lease)
        self.leader_lease_thread.daemon = True
        self.leader_lease_thread.start()

    def load_logs_and_metadata(self):
        if os.path.exists(self.logs_file):
            with open(self.logs_file, "r") as f:
                for line in f.readlines():
                    entry = line.strip()
                    if entry.startswith("NO-OP"):
                        parts = entry.split(" ")
                        term = int(parts[1])
                        self.log.append({"term": term, "operation": "NO-OP"})
                    elif entry.startswith("SET"):
                        parts = entry.split(" ")
                        term = int(parts[-1])
                        operation = " ".join(parts[:-1])
                        self.log.append({"term": term, "operation": operation})

        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                metadata = json.load(f)
                self.current_term = metadata["current_term"]
                self.voted_for = metadata["voted_for"]

    def save_logs_and_metadata(self):
        with open(self.logs_file, "w") as f:
            for entry in self.log:
                f.write(f"{entry['operation']} {entry['term']}\n")
        print("Logs and metadata saved.")

        metadata = {
            "current_term": self.current_term,
            "voted_for": self.voted_for
        }
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f)
        print("Metadata saved.")

    def start(self):
        while True:
            message = sock.recv_json()
            print(f"Received message: {message}")
            if message["type"] == "RequestVote":
                self.handle_request_vote(message)
            elif message["type"] == "AppendEntries":
                self.handle_append_entries(message)
            elif message["type"] == "ClientRequest":
                self.handle_client_request(message)

    def handle_request_vote(self, message):
        term = message["term"]
        candidate_id = message["candidate_id"]
        last_log_index = message["last_log_index"]
        last_log_term = message["last_log_term"]
        lease_duration = message["lease_duration"]
        
        print(f"Received RequestVote RPC from candidate {candidate_id} for term {term}")

        if term < self.current_term:
            sock.send_json({"type": "RequestVoteResponse", "term": self.current_term, "vote_granted": False})
            print(f"Voted against candidate {candidate_id} for term {term}: Vote granted: False")
            return

        if self.voted_for is None or self.voted_for == candidate_id:
            if last_log_term > self.log[-1]["term"] or (last_log_term == self.log[-1]["term"] and last_log_index >= len(self.log)):
                self.voted_for = candidate_id
                self.save_logs_and_metadata()
                sock.send_json({"type": "RequestVoteResponse", "term": self.current_term, "vote_granted": True, "max_old_leader_lease": self.max_old_leader_lease})
                print(f"Voted for candidate {candidate_id} for term {term}: Vote granted: True")
                return

        sock.send_json({"type": "RequestVoteResponse", "term": self.current_term, "vote_granted": False})
        print(f"Voted against candidate {candidate_id} for term {term}: Vote granted: False")

    def handle_append_entries(self, message):
        term = message["term"]
        leader_id = message["leader_id"]
        prev_log_index = message["prev_log_index"]
        prev_log_term = message["prev_log_term"]
        entries = message["entries"]
        leader_commit = message["leader_commit"]
        lease_duration = message["lease_duration"]

        print(f"Received AppendEntries RPC from leader {leader_id} for term {term}")

        if term < self.current_term:
            sock.send_json({"type": "AppendEntriesResponse", "term": self.current_term, "success": False, "last_index": len(self.log)})
            print(f"Rejected AppendEntries RPC from leader { leader_id} for term {term}: Current term is higher")
            return

        if prev_log_index > 0 and (prev_log_index >= len(self.log) or self.log[prev_log_index - 1]["term"] != prev_log_term):
            sock.send_json({"type": "AppendEntriesResponse", "term": self.current_term, "success": False, "last_index": len(self.log)})
            print(f"Rejected AppendEntries RPC from leader {leader_id} for term {term}: Previous log entry mismatch")
            return

        if len(entries) > 0:
            # Conflict resolution
            for entry in entries:
                index = entry["index"]
                if index <= len(self.log):
                    if self.log[index - 1]["term"] != entry["term"]:
                        self.log = self.log[:index - 1]
                        self.save_logs_and_metadata()
                        self.log.append(entry)
                else:
                    self.log.append(entry)

            self.save_logs_and_metadata()

        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log))

        sock.send_json({"type": "AppendEntriesResponse", "term": self.current_term, "success": True,"last_index": len(self.log)})
        print(f"Accepted AppendEntries RPC from leader {leader_id} for term {term}")

    def handle_client_request(self, message):
        operation = message.get("operation")
        key = message.get("key")
        value = message.get("value")

        print(f"Received ClientRequest: Operation - {operation}, Key - {key}, Value - {value}")

        if operation == "SET":
            self.db[key] = value
            log_entry = {"term": self.current_term, "operation": f"SET {key} {value}"}
            self.log.append(log_entry)
            self.save_logs_and_metadata()
            client.send_json({"status": "SUCCESS", "message": "Key-value pair set successfully"})
        elif operation == "GET":
            value = self.db.get(key, "")
            client.send_json({"status": "SUCCESS", "message": value})
        else:
            client.send_json({"status": "ERROR", "message": "Invalid operation"})

    def leader_lease(self):
        while True:
            if self.state == "Leader":
                if time.time() >= self.leader_lease_timeout:
                    self.start_election()
                else:
                    time.sleep(1)
            else:
                time.sleep(1)

    def start_election(self):
        while True:
            start_time = time.time()
            if (time.time() - start_time > self.timeout):
                if self.state == "leader":
                    break
                else: #follower
                    self.send_heartbeats()
                    self.become_candidate()
                    continue
            if self.state == "leader":
                continue
        
    def become_candidate(self):
        self.state = "candidate"
        self.current_term += 1
        self.votes += 1
        self.leader_id = None
        self.logger.write(f"Became candidate for term {self.current_term}\n")
        
    def send_heartbeats(self):
        while True:
            if self.state == "leader":
                message = {
                    'type': 'heartbeat',
                    'term': self.current_term,
                    'leader_id': self.node_id,
                    'commit_index': self.commit_index
                }
                node2.send_json(message)
                node3.send_json(message)
                node4.send_json(message)
                node5.send_json(message)
                time.sleep(self.heartbeat_interval)
            else:
                time.sleep(0.1)
                

    def handle_heartbeats(self):
        while True:
            if self.state == "follower":
                message = self.heartbeat_socket.recv_pyobj()
                if message['type'] == 'heartbeat':
                    # Update current term and leader ID if necessary
                    if message['term'] > self.current_term:
                        self.current_term = message['term']
                        self.leader_id = message['leader_id']
                        self.state = "follower"  # Resetting state to follower
                    # Reply to the leader's heartbeat with acknowledgment
                    ack_message = {
                        'type': 'heartbeat_ack',
                        'term': self.current_term,
                        'follower_id': self.node_id,
                        'commit_index': self.commit_index,
                        'status': 'Success'
                    }
                    nodel = context.socket(zmq.PUSH)
                    nodel.connect(f"tcp://127.0.0.1:{message['leader_id']}")   
                    nodel.send_json(ack_message)
            else:
                msg = sock.recv_json()
                print(f'{msg['status']}')
        
    def send_request_vote(self):
                message = {
                    "type": "RequestVote",
                    "term": self.current_term,
                    "candidate_id": self.node_id,
                    "last_log_index": len(self.log),
                    "last_log_term": self.log[-1]["term"] if self.log else 0,
                    "lease_duration": self.lease_duration
                }
                node2.send_json(message)
                node3.send_json(message)
                node4.send_json(message)
                node5.send_json(message)
                # print(f"Sending RequestVote RPC to node {node_id} for term {self.current_term}")
                # Send RequestVote RPC to other nodes
                pass

    def send_append_entries(self):
        message = {
            "type": "AppendEntries",
            "term": self.current_term,
            "leader_id": self.node_id,
            "prev_log_index": self.next_index[node_id] - 1,
            "prev_log_term": self.log[self.next_index[node_id] - 2]["term"] if self.next_index[node_id] > 1 else 0,
            "entries": self.log[self.next_index[node_id] - 1:],
            "leader_commit": self.commit_index,
            "lease_duration": self.lease_duration
        }
        node2.send_json(message) 
        node3.send_json(message)
        node4.send_json(message)
        node5.send_json(message)
         
        # Send AppendEntries RPC to other nodes
        pass

    def handle_votes(self, message):
        if self.state != "Candidate":
            return

        term = message["term"]
        vote_granted = message["vote_granted"]
        max_old_leader_lease = message.get("max_old_leader_lease", 0)

        if max_old_leader_lease > self.max_old_leader_lease:
            self.max_old_leader_lease = max_old_leader_lease

        if term > self.current_term:
            self.state = "Follower"
            self.current_term = term
            self.voted_for = None
            self.save_logs_and_metadata()
            return

        if vote_granted:
            # Increment vote count
            self.votes += 1
            if self.votes > self.total_nodes // 2:
                self.state = "Leader"
                self.leader_id = self.node_id
                self.client.send_json({"addr": "tcp://127.0.0.1:1"})
                self.send_heartbeats()
        else:
            # Reset the election timer and start a new election
            self.reset_election_timer()
            print("Received vote denial")

    def handle_append_entries_response(self, message):
        if self.state != "Leader":
            return

        term = message["term"]
        success = message["success"]
        last_index = message["last_index"]
        node_id = message["node_id"]

        if term > self.current_term:
            self.state = "Follower"
            self.current_term = term
            self.voted_for = None
            self.save_logs_and_metadata()
            return

        if success:
            # Update next_index and match_index for the follower
            self.next_index[node_id] = last_index + 1
            self.match_index[node_id] = last_index
            # Check if commit_index can be updated based on match_index of majority
            self.update_commit_index()
        else:
            # If AppendEntries fails, decrement next_index for the follower and retry
            self.next_index[node_id] -= 1
            self.send_append_entries(node_id)
            print(f"Failed AppendEntries RPC response from node {node_id}")

if __name__ == "__main__":
    total_nodes = 5  # Total number of nodes in the cluster
    node_id = 1
    node = RaftNode(node_id, total_nodes)
    node.start()

