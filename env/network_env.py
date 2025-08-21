## 封装与mahimahi仿真环境交互的代码
# genet_project/env/network_env.py

import subprocess
import time
import re
import pandas as pd
import numpy as np
# --- 导入我们自己的模块 ---
from core.utility import calculate_utility

class NetworkEnvironment:
    """
    [总体流程位置]: 连接所有上层算法逻辑与底层Mahimahi仿真的“驱动层”

    职责:
    1.  根据配置构建并启动Mahimahi链路。
    2.  执行上层算法指定的发送速率 (通过iperf)。
    3.  采集并解析仿真结果 (iperf日志, tcpdump等)。
    4.  向上层返回结构化的网络反馈。
    """

    def __init__(self, config):
        """
        [总体流程位置]: 实验初始化阶段

        职责:
        1.  保存配置。
        2.  准备iperf服务器等仿真前置条件。
        """
        self.config = config
        self.utility_params = config.get('utility_params', {})
        self.last_feedback = {}  # 用于记录上一个周期的反馈
        print("NetworkEnvironment initialized.")

    def run_and_get_feedback(self, component, duration_sec=0.5):
        """
        在评估阶段的核心函数：真实地运行一个组件并返回其性能反馈。

        Args:
            component (BaseComponent): 要运行的组件 (CubicComponent或SageComponent)。
            duration_sec (float): 运行的持续时间（秒）。

        Returns:
            dict: 包含网络测量值的反馈字典。
        """
        # 1. 从组件获取建议速率
        #    注意：get_current_state()是一个需要您自己实现的辅助函数
        current_network_state = self._get_current_state()
        rate_to_test = component.get_suggested_rate(current_network_state)

        # 2. 构建并执行Mahimahi命令来运行这个速率
        #    这是一个简化的示例，您需要根据Mahimahi的实际用法来构建命令
        print(f"  [Network Env] Running {component.name} at {rate_to_test:.2f} Mbps for {duration_sec}s...")

        # --- 待实现：调用Mahimahi和iperf的shell命令 ---
        # command = f"mm-delay 20 mm-loss 0.1 -- iperf -c <server_ip> -b {rate_to_test}M -t {duration_sec}"
        # process = subprocess.run(command, shell=True, capture_output=True, text=True)
        # iperf_output = process.stdout

        # 3. 收集并解析网络反馈 (例如，从iperf输出或tcpdump日志)
        # --- 待实现：解析iperf_output或tcpdump日志 ---
        # 这是一个复杂的过程，需要您编写专门的解析器
        # 我们在这里用随机生成的模拟数据代替
        feedback = self._generate_mock_feedback(rate_to_test)

        return feedback

    def execute_rate_for_one_rtt(self, rate, primary_component):
        """
        在执行阶段的核心函数：以指定速率运行一个RTT。
        """
        print(f"  [Network Env] Executing at {rate:.2f} Mbps for one RTT...")
        # 这里的逻辑与run_and_get_feedback类似，只是运行时长是一个RTT
        feedback = self._generate_mock_feedback(rate)

        # 在这里我们直接计算并返回效用值，供危机监测使用
        utility = calculate_utility(feedback, self.config['utility_params'])
        return utility

    def _get_current_state(self):
        """
        获取当前的网络状态，用于喂给组件进行决策。
        这是一个需要您实现的辅助函数。
        """
        # --- 待实现 ---
        # 需要从内核或之前的反馈中获取最新的RTT, 吞吐量等信息
        # 暂时返回一个空的mock状态
        return {'current_rate': 50.0, 'rtt': 40.0}

    def _generate_mock_feedback(self, sending_rate):
        """
        生成模拟的网络反馈数据，用于快速测试。
        在您完成真实的数据采集和解析前，这个函数非常有用。
        """
        # 模拟一个简单的网络行为
        # 假设真实带宽是100Mbps
        real_bandwidth = 100
        rtt_min = 40

        if sending_rate <= real_bandwidth:
            # 未拥塞
            throughput = sending_rate
            rtt_current = rtt_min + np.random.uniform(0, 5)  # 正常抖动
            rtt_gradient = np.random.uniform(-10, 10)
        else:
            # 拥塞
            throughput = real_bandwidth
            queue_delay = (sending_rate - real_bandwidth) * 2
            rtt_current = rtt_min + queue_delay + np.random.uniform(0, 5)
            rtt_gradient = (rtt_current - (rtt_min + queue_delay / 2)) / 0.1  # 简化的梯度计算

        return {
            'sending_rate': throughput,
            'rtt_gradient': rtt_gradient,
            'rtt_current': rtt_current,
            'rtt_min': rtt_min
        }