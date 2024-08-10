import os
import time
import json
import zmq
import threading
import random

class RaftNode:
    def __init__(self, node_id, total_nodes):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.state = "Follower"
        self.current_leader = None
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {i: len(self.log) + 1 for i in range(1, self.total_nodes + 1)}
        self.match_index = {i: 0 for i in range(1, self.total_nodes + 1)}
        self.leader_lease_timeout = None
        self.token = False
        self.lease_duration = 5  # in seconds
        self.leader_lease_duration = 10  # in seconds

        self.db = {}
        self.logs_directory = f"logs_node_{self.node_id}"
        self.logs_file = f"{self.logs_directory}/logs.txt"
        self.metadata_file = f"{self.logs_directory}/metadata.json"
        self.dump_file = f"{self.logs_directory}/dump.txt"
        self.load_logs_and_metadata()

        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://0.0.0.0:{self.node_id}")

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
            message = self.socket.recv_json()
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

        print(f"Received RequestVote RPC from candidate {candidate_id} for term {term}")

        if term < self.current_term:
            self.socket.send_json({"type": "RequestVoteResponse", "term": self.current_term, "vote_granted": False})
            print(f"Voted against candidate {candidate_id} for term {term}: Vote granted: False")
            return

        if self.voted_for is None or self.voted_for == candidate_id:
            if last_log_term > self.log[-1]["term"] or (last_log_term == self.log[-1]["term"] and last_log_index >= len(self.log)):
                self.voted_for = candidate_id
                self.save_logs_and_metadata()
                self.socket.send_json({"type": "RequestVoteResponse", "term": self.current_term, "vote_granted": True})
                print(f"Voted for candidate {candidate_id} for term {term}: Vote granted: True")
                return

        self.socket.send_json({"type": "RequestVoteResponse", "term": self.current_term, "vote_granted": False})
        print(f"Voted against candidate {candidate_id} for term {term}: Vote granted: False")

    def handle_append_entries(self, message):
        term = message["term"]
        leader_id = message["leader_id"]
        prev_log_index = message["prev_log_index"]
        prev_log_term = message["prev_log_term"]
        entries = message["entries"]
        leader_commit = message["leader_commit"]

        print(f"Received AppendEntries RPC from leader {leader_id} for term {term}")

        if term < self.current_term:
            self.socket.send_json({"type": "AppendEntriesResponse", "term": self.current_term, "success": False, "last_index": len(self.log)})
            print(f"Rejected AppendEntries RPC from leader { leader_id} for term {term}: Current term is higher")
            return

        if prev_log_index > 0 and (prev_log_index >= len(self.log) or self.log[prev_log_index - 1]["term"] != prev_log_term):
            self.socket.send_json({"type": "AppendEntriesResponse", "term": self.current_term, "success": False, "last_index": len(self.log)})
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

        self.socket.send_json({"type": "AppendEntriesResponse", "term": self.current_term, "success": True, "last_index": len(self.log)})
        print(f"Accepted AppendEntries RPC from leader {leader_id} for term {term}")

    def handle_client_request(self, message):
        # Logic for handling client requests
        operation = message.get("operation")
        key = message.get("key")
        value = message.get("value")

        print(f"Received ClientRequest: Operation - {operation}, Key - {key}, Value - {value}")

        if operation == "SET":
            self.db[key] = value
            log_entry = {"term": self.current_term, "operation": f"SET {key} {value}"}
            self.log.append(log_entry)
            self.save_logs_and_metadata()
            self.socket.send_json({"status": "SUCCESS", "message": "Key-value pair set successfully"})
        elif operation == "GET":
            value = self.db.get(key, "")
            self.socket.send_json({"status": "SUCCESS", "value": value})
        else:
            self.socket.send_json({"status": "ERROR", "message": "Invalid operation"})

    def leader_lease(self):
        while True:
            if self.state == "Leader":
                self.leader_lease_timeout = time.time() + self.leader_lease_duration
                time.sleep(self.leader_lease_duration / 2)
            else:
                time.sleep(1)

    def start_election(self):
        if self.election_timer is not None:
            self.election_timer.cancel()
        random_timeout = random.uniform(5, 10)
        self.election_timer = threading.Timer(random_timeout, self.start_election)
        self.election_timer.start()
        self.current_term += 1
        self.voted_for = self.node_id
        self.save_logs_and_metadata()
        self.send_request_vote()

    def send_request_vote(self):
        for node_id in range(1, self.total_nodes + 1):
            if node_id != self.node_id:
                message = {
                    "type": "RequestVote",
                    "term": self.current_term,
                    "candidate_id": self.node_id,
                    "last_log_index": len(self.log),
                    "last_log_term": self.log[-1]["term"] if self.log else 0
                }
                print(f"Sending RequestVote RPC to node {node_id} for term {self.current_term}")
                # Send RequestVote RPC to other nodes
                pass

    def send_append_entries(self):
        for node_id in range(1, self.total_nodes + 1):
            if node_id != self.node_id:
                message = {
                    "type": "AppendEntries",
                    "term": self.current_term,
                    "leader_id": self.node_id,
                    "prev_log_index": self.next_index[node_id] - 1,
                    "prev_log_term": self.log[self.next_index[node_id] - 2]["term"] if self.next_index[node_id] > 1 else 0,
                    "entries": self.log[self.next_index[node_id] - 1:],
                    "leader_commit": self.commit_index
                }
                print(f"Sending AppendEntries RPC to node {node_id} for term {self.current_term}")
                # Send AppendEntries RPC to other nodes
                pass

    def handle_votes(self, message):
        if self.state != "Candidate":
            return

        term = message["term"]
        vote_granted = message["vote_granted"]

        if term > self.current_term:
            self.state = "Follower"
            self.current_term = term
            self.voted_for = None
            self.save_logs_and_metadata()
            return

        if vote_granted:
            # Increment vote count
            self.votes_received += 1
            if self.votes_received > self.total_nodes // 2:
                self.state = "Leader"
                self.leader_id = self.node_id
                self.start_heartbeats()
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
    node_id = 3
    node = RaftNode(node_id, total_nodes)
    node.start()

