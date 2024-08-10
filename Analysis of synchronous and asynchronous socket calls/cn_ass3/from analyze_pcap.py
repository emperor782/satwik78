import pyshark
import matplotlib.pyplot as plt

def compute_metrics(pcap_file):
    capture = pyshark.FileCapture(pcap_file)
    tcp_flows = {}

    for packet in capture:
        if 'TCP' in packet:
            src_ip = packet.ip.src
            dst_ip = packet.ip.dst
            src_port = packet.tcp.srcport
            dst_port = packet.tcp.dstport
            flow_key = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}"

            if flow_key not in tcp_flows:
                tcp_flows[flow_key] = {
                    'packets': 0,
                    'bytes': 0,
                    'start_time': float(packet.sniff_timestamp),
                    'end_time': float(packet.sniff_timestamp)
                }

            tcp_flows[flow_key]['packets'] += 1
            tcp_flows[flow_key]['bytes'] += int(packet.length)
            tcp_flows[flow_key]['end_time'] = float(packet.sniff_timestamp)

    for flow_key, flow_data in tcp_flows.items():
        flow_duration = flow_data['end_time'] - flow_data['start_time']
        flow_bytes = flow_data['bytes']
        flow_packets = flow_data['packets']

        throughput = (flow_bytes * 8) / flow_duration  # bits per second
        latency = (flow_duration * 1000) / flow_packets  # milliseconds

        tcp_flows[flow_key]['throughput'] = throughput
        tcp_flows[flow_key]['latency'] = latency

    capture.close()
    return tcp_flows

def plot_metrics(tcp_flows):
    throughput_values = []
    latency_values = []

    for flow_data in tcp_flows.values():
        throughput_values.append(flow_data['throughput'])
        latency_values.append(flow_data['latency'])

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.bar(range(len(throughput_values)), throughput_values)
    plt.xlabel('Flow')
    plt.ylabel('Throughput (bps)')
    plt.title('Average Throughput for TCP Flows')

    plt.subplot(1, 2, 2)
    plt.bar(range(len(latency_values)), latency_values)
    plt.xlabel('Flow')
    plt.ylabel('Latency (ms)')
    plt.title('Average Latency for TCP Flows')

    plt.tight_layout()
    plt.show()

# Specify the path to your pcap file
pcap_file = 'Home/Desktop/cn_ass3/capture.pcap'

# Compute metrics
tcp_flows = compute_metrics(pcap_file)

# Plot metrics
plot_metrics(tcp_flows)