import matplotlib.pyplot as plt
from scapy.all import *

def extration_of_tcp_fields(packet):
    if TCP in packet and packet.haslayer(TCP):
        return packet[TCP].seq, packet[TCP].ack, packet[TCP].window
    return None

def plot_congestion_window(pcap_file):
    packets = rdpcap(pcap_file)

    timestamps = []
    congestion_window = []

    start_time = 0
    interval = 0.00005 

    for packet in packets:
        tcp_fields = extration_of_tcp_fields(packet)
        if tcp_fields:
            seq, ack, window = tcp_fields
            timestamps.append(start_time)
            congestion_window.append(window)
            start_time += interval

    plt.plot(timestamps, congestion_window, label='Congestion Window')
    plt.xlabel('Time (s)')
    plt.ylabel('Congestion Window Size')
    plt.title('TCP Congestion Window Evolution')
    plt.legend()
    plt.show()


plot_congestion_window('/home/satwik/mininet/custom/2C.pcap')

