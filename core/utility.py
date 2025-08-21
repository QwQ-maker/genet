## 效用函数的定义和计算
# genet_project/core/utility.py

import numpy as np


def calculate_utility(feedback, config):
    """
    根据真实的网络反馈，计算一个发送速率的最终效用值。

    Args:
        feedback (dict): 包含网络测量值的字典。
                         例如: {'sending_rate': 80.0, 'rtt_gradient': 50.0,
                               'rtt_current': 35.0, 'rtt_min': 20.0}
        config (dict): 包含效用函数超参数的字典。

    Returns:
        float: 计算出的最终效用值。
    """
    # 从字典中安全地获取参数
    x = feedback.get('sending_rate', 0)
    rtt_gradient = feedback.get('rtt_gradient', 0)
    rtt_current = feedback.get('rtt_current', 0)
    rtt_min = feedback.get('rtt_min', 1)  # 避免除以零

    alpha = config.get('alpha', 1.0)
    tau = config.get('tau', 0.9)
    beta = config.get('beta', 900)
    lambda_ = config.get('lambda', 11)
    mu = config.get('mu', 0.2)

    # 1. 计算收益项：吞吐量项
    throughput_benefit = alpha * (x ** tau)

    # 2. 计算成本项一：延迟增长惩罚
    latency_growth_penalty = beta * x * max(rtt_gradient, 0)

    # 3. 计算成本项二：排队长度惩罚
    queuing_length_penalty = 0
    rtt_ratio = rtt_current / rtt_min if rtt_min > 0 else 1

    # 判断“惩罚开关” I_Q 是否开启
    if rtt_ratio > (1 + mu):
        queuing_length_penalty = lambda_ * x * rtt_ratio

    # 4. 计算最终效用值：收益 - 成本
    utility_score = throughput_benefit - latency_growth_penalty - queuing_length_penalty

    return utility_score