import pandas as pd
import matplotlib.pyplot as plt
from scapy.all import rdpcap
import numpy as np

# Define the full path to your PCAP file with the correct case
pcap_file_path = '/home/satwik/Desktop/cn_ass3/f500.pcap'

# Function to compute average throughput
def compute_average_throughput(pcap_file):
    # Load the PCAP file
    pcap = rdpcap(pcap_file)

    # Create an empty DataFrame to store packet data
    packet_data = []

    # Iterate through the packets and extract relevant information
    for packet in pcap:
        # Extract packet size and timestamp as needed
        size = len(packet)
        timestamp = packet.time
        packet_data.append((timestamp, size))

    # Create a DataFrame from the collected packet data
    df = pd.DataFrame(packet_data, columns=["Timestamp", "Size"])

    # Calculate throughput (bits per second)
    total_bytes = df['Size'].sum()
    total_time = df['Timestamp'].max() - df['Timestamp'].min()
    average_throughput_bps = (total_bytes * 8) / total_time

    return average_throughput_bps

# Function to compute average latency
def compute_average_latency(pcap_file):
    # Load the PCAP file
    pcap = rdpcap(pcap_file)

    # Extract timestamps for packets (assuming packets contain latency information)
    timestamps = [packet.time for packet in pcap]

    # Calculate average latency (in milliseconds)
    average_latency_ms = np.mean(np.diff(timestamps)) * 1000

    return average_latency_ms

# Compute metrics
average_throughput = compute_average_throughput(pcap_file_path)
average_latency = compute_average_latency(pcap_file_path)

# Print the metrics
print(f"Average Throughput: {average_throughput:.2f} bps")
print(f"Average Latency: {average_latency:.2f} ms")

# Plot the results
plt.figure(figsize=(8, 6))
plt.bar(["Throughput", "Latency"], [average_throughput, average_latency])
plt.title("Network Metrics")
plt.ylabel("Value")
plt.show()
