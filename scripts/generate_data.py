## 训练数据生成
# genet_project/scripts/generate_data.py

import sys
import os
import yaml
import pandas as pd
from itertools import product
import numpy as np

# --- 项目路径设置 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from env.network_env import NetworkEnvironment
from core.components import CubicComponent, SageComponent
from utils.logger import setup_logger


def find_optimal_rate_via_micro_experiment(network_env, candidate_rates):
    """
    通过“事后诸葛亮”的微型实验，找到当前网络状态下的最优速率。

    Args:
        network_env (NetworkEnvironment): 网络环境实例。
        candidate_rates (list): 一组候选速率。

    Returns:
        float: 在这次微型实验中，获得了最高真实效用值的那个速率。
    """
    best_rate = None
    max_utility = -float('inf')

    for rate in candidate_rates:
        # 极其短暂地、真实地运行每个候选速率
        feedback = network_env.run_rate_for_short_period(rate, duration_sec=0.2)
        utility = network_env.calculate_utility_from_feedback(feedback)

        if utility > max_utility:
            max_utility = utility
            best_rate = rate

    return best_rate


def generate_training_data(config):
    """
    在受控环境中，通过主动实验生成用于训练GBDT模型的数据集。
    """
    log = setup_logger(name='DataGenerator', log_file='data_generation.log')
    log.info("Starting data generation process with self-sufficient method...")

    # 1. 定义网络环境的参数空间
    bandwidths = [20, 50, 100, 150]
    delays = [20, 50, 100]
    loss_rates = [0, 0.001, 0.01]
    background_traffic_ratios = [0.1, 0.3, 0.5]  # 背景流量占总带宽的比例

    network_scenarios = list(product(bandwidths, delays, loss_rates, background_traffic_ratios))
    log.info(f"Generated {len(network_scenarios)} network scenarios to run.")

    all_training_samples = []

    # 2. 遍历每一个“参数已知的宇宙”
    for bw, delay, loss, r_ratio in network_scenarios:

        # --- “上帝”知道这个宇宙的物理常数 ---
        ground_truth_C = bw
        ground_truth_R = bw * r_ratio

        log.info(
            f"Running in new universe: C={ground_truth_C}Mbps, R={ground_truth_R}Mbps, Delay={delay}ms, Loss={loss * 100}%")

        # a. 创建这个宇宙
        env_config = {
            'mahimahi_params': {'bandwidth': bw, 'delay': delay, 'loss': loss, 'background_traffic': ground_truth_R}}
        network_env = NetworkEnvironment(env_config)
        cubic = CubicComponent()
        sage = SageComponent()

        # b. 记录“问题 (X)” 和 “答案 (Y)”
        # 在这个环境中运行一段时间，收集多个决策点的数据
        for _ in range(config.get('samples_per_scenario', 10)):
            # i. 记录问题：获取CUBIC和Sage的建议及其反馈
            feedback_cl = network_env.run_and_get_feedback(cubic)
            feedback_rl = network_env.run_and_get_feedback(sage)
            feedback_prev = network_env.get_last_feedback()  # 假设可以获取上一轮的反馈

            # 构建9维输入向量X (这里需要您根据feedback字典填充)
            input_X = [
                feedback_cl['sending_rate'], feedback_cl['utility'], feedback_cl['rtt_gradient'],
                feedback_rl['sending_rate'], feedback_rl['utility'], feedback_rl['rtt_gradient'],
                feedback_prev['sending_rate'], feedback_prev['utility'], feedback_prev['rtt_gradient'],
            ]

            # ii. 寻找答案：进行微型实验
            candidate_rates = [
                feedback_cl['sending_rate'],
                feedback_rl['sending_rate'],
                np.mean([feedback_cl['sending_rate'], feedback_rl['sending_rate']]),
                max(feedback_cl['sending_rate'], feedback_rl['sending_rate']) * 1.2
            ]
            r_opt_label = find_optimal_rate_via_micro_experiment(network_env, candidate_rates)

            # iii. 组装一条完整的训练样本
            training_sample = input_X + [r_opt_label, ground_truth_C, ground_truth_R]
            all_training_samples.append(training_sample)

    # 3. 将所有收集到的数据保存到CSV文件中
    if all_training_samples:
        feature_columns = [
            'r_cl', 'U_cl', 'dD_cl', 'r_rl', 'U_rl', 'dD_rl', 'r_prev', 'U_prev', 'dD_prev'
        ]
        label_columns = ['r_opt_label', 'C_label', 'R_label']
        df = pd.DataFrame(all_training_samples, columns=feature_columns + label_columns)

        output_path = os.path.join(project_root, 'data', 'training_data.csv')
        df.to_csv(output_path, index=False)
        log.info(f"Successfully saved {len(df)} training samples to {output_path}")
    else:
        log.warning("No training samples were collected.")


if __name__ == '__main__':
    # ... (加载配置文件的代码保持不变) ...
    config_path = os.path.join(project_root, 'config.yml')
    # ...
    generate_training_data(config)