## 图表制作
# genet_project/scripts/plot_results.py

import sys
import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 项目路径设置 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from utils.parser import parse_iperf_output
from utils.logger import setup_logger


def plot_throughput_over_time(results_df, output_path):
    """
    绘制吞吐量随时间变化的曲线图。

    Args:
        results_df (pd.DataFrame): 包含多个算法实验结果的DataFrame。
                                   需要有 'Algorithm', 'Time', 'Throughput' 列。
        output_path (str): 图片保存路径。
    """
    log = setup_logger(name='Plotter')
    log.info(f"Plotting throughput over time to {output_path}...")

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=results_df, x='Time', y='Throughput', hue='Algorithm', errorbar='sd')

    plt.title('Throughput Comparison Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Throughput (Mbits/s)')
    plt.grid(True)
    plt.legend(title='Algorithm')
    plt.tight_layout()

    plt.savefig(output_path)
    plt.close()
    log.info("Plot saved successfully.")


def plot_throughput_delay_scatter(results_df, output_path):
    """
    绘制吞- 吐量-延迟散点图。

    Args:
        results_df (pd.DataFrame): 包含多个算法实验结果的DataFrame。
                                   需要有 'Algorithm', 'Avg_Throughput', 'Avg_Delay' 列。
        output_path (str): 图片保存路径。
    """
    log = setup_logger(name='Plotter')
    log.info(f"Plotting throughput-delay scatter to {output_path}...")

    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=results_df, x='Avg_Delay', y='Avg_Throughput', hue='Algorithm', s=100, alpha=0.7)

    plt.title('Throughput vs. Delay Trade-off')
    plt.xlabel('95th Percentile Delay (ms)')
    plt.ylabel('Average Throughput (Mbits/s)')
    plt.grid(True)
    plt.legend(title='Algorithm')
    plt.tight_layout()

    plt.savefig(output_path)
    plt.close()
    log.info("Plot saved successfully.")


def main(results_directory):
    """
    主函数，负责读取所有实验结果，并调用绘图函数。
    """
    log = setup_logger(name='Plotter')
    log.info(f"Reading experiment results from: {results_directory}")

    all_results = []

    # --- 待实现：读取和解析真实的实验日志 ---
    # 这里的逻辑需要您根据run_experiment.py的输出格式来定制
    # 假设每个算法的运行结果都保存在一个单独的日志文件中
    # for log_file in os.listdir(results_directory):
    #     if log_file.endswith(".log"):
    #         algorithm_name = log_file.split('_')[0]
    #         with open(os.path.join(results_directory, log_file), 'r') as f:
    #             content = f.read()
    #             timeseries_df, summary_dict = parse_iperf_output(content)
    #             # ... 在这里您还需要解析出延迟数据 ...
    #             # ... 然后将所有数据合并到一个大的DataFrame中 ...

    # --- 使用模拟数据进行演示 ---
    # 假设我们已经解析好了数据
    mock_data = {
        'Algorithm': ['Genet', 'Genet', 'Anole', 'Anole', 'CUBIC', 'CUBIC'],
        'Avg_Throughput': [95, 98, 85, 88, 70, 72],
        'Avg_Delay': [45, 48, 55, 52, 80, 85]
    }
    summary_df = pd.DataFrame(mock_data)

    # --- 调用绘图函数 ---
    output_dir = os.path.join(project_root, 'results', 'plots')
    os.makedirs(output_dir, exist_ok=True)

    # 绘制散点图
    scatter_plot_path = os.path.join(output_dir, 'throughput_delay_scatter.png')
    plot_throughput_delay_scatter(summary_df, scatter_plot_path)


if __name__ == '__main__':
    # 假设实验结果保存在 'results/raw_logs' 文件夹下
    results_dir = os.path.join(project_root, 'results', 'raw_logs')
    main(results_dir)