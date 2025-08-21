## 解析功能

# genet_project/utils/parser.py

import re
import pandas as pd
def parse_iperf_output(iperf_log_content):
    """
    解析iperf客户端输出的日志内容，提取吞吐量和延迟等关键指标。

    Args:
        iperf_log_content (str): iperf命令执行后产生的完整字符串输出。

    Returns:
        pd.DataFrame: 一个包含时间序列数据的DataFrame，
                      列如 ['Interval', 'Transfer', 'Bitrate_Mbits_s']。
        dict: 一个包含总结性数据的字典，如 {'avg_bitrate': ...}
    """
    # iperf输出通常包含多行，我们逐行解析
    lines = iperf_log_content.strip().split('\n')

    data_rows = []
    summary = {}

    # 正则表达式，用于匹配iperf的数据行
    # 例: [  5]   0.00-1.00   sec  11.5 MBytes  96.5 Mbits/sec
    data_pattern = re.compile(
        r'\[\s*\d+\]\s*([\d\.-]+)\s*-\s*([\d\.-]+)\s*sec\s*([\d\.-]+)\s*MBytes\s*([\d\.-]+)\s*Mbits/sec'
    )

    # 正则表达式，用于匹配iperf的总结行
    summary_pattern = re.compile(
        r'\[\s*\d+\]\s*([\d\.-]+)\s*-\s*([\d\.-]+)\s*sec\s*([\d\.-]+)\s*MBytes\s*([\d\.-]+)\s*Mbits/sec'
    )

    for line in lines:
        data_match = data_pattern.search(line)
        if data_match:
            start_time, end_time, transfer, bitrate = data_match.groups()
            data_rows.append({
                'Interval_Start_s': float(start_time),
                'Interval_End_s': float(end_time),
                'Transfer_MBytes': float(transfer),
                'Bitrate_Mbits_s': float(bitrate)
            })
            continue  # 匹配到数据行后，跳过对总结行的匹配

        summary_match = summary_pattern.search(line)
        if summary_match and "sender" in line:  # 确保是sender的总结
            start_time, end_time, transfer, bitrate = summary_match.groups()
            summary = {
                'total_duration_s': float(end_time),
                'total_transfer_MBytes': float(transfer),
                'avg_bitrate_Mbits_s': float(bitrate)
            }

    # 将数据行转换为pandas DataFrame，便于后续处理和绘图
    df = pd.DataFrame(data_rows)

    return df, summary


def parse_tcpdump_for_latency(tcpdump_log_path):
    """
    解析tcpdump生成的pcap文件或文本日志，来计算端到端延迟。
    这是一个非常复杂的任务，通常需要专业的库（如Scapy）或工具。

    Args:
        tcpdump_log_path (str): tcpdump日志文件的路径。

    Returns:
        pd.DataFrame: 一个包含每个数据包延迟信息的DataFrame。
    """
    print(f"--- [Parser] Parsing tcpdump log at {tcpdump_log_path} for latency... ---")
    # --- 待实现 ---
    # 实际的延迟计算需要：
    # 1. 识别TCP数据包的序列号(SEQ)和确认号(ACK)。
    # 2. 匹配一个发出的数据包和它对应的确认包。
    # 3. 计算两者的时间戳之差，得到该数据包的RTT。
    # 这是一个非常专业且复杂的过程，通常会使用 Scapy 库来完成。
    # 在这里，我们只提供一个框架。

    # 简化模拟：返回一个空的DataFrame
    latency_df = pd.DataFrame(columns=['timestamp', 'rtt_ms'])
    return latency_df