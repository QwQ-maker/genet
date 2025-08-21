# 双维智能触发器的逻辑实现
# genet_project/engine/trigger_engine.py

import numpy as np


class DualDimensionSmartTrigger:
    """
    实现了“双维智能触发器”。
    该模块负责判断是否需要启动“学习式速率推断引擎”。
    它包含两个并行的检查引擎：
    1. 基于“自适应历史标杆”的相对表现检查。
    2. “性能高原”探测器。
    """

    def __init__(self, config):
        """
        初始化触发器所需的所有参数。
        """
        trigger_params = config.get('engine_params', {}).get('inference_engine', {}).get('trigger', {})
        self.benchmark_alpha = trigger_params.get('trigger_benchmark_alpha', 0.05)
        self.activation_k = trigger_params.get('trigger_activation_k', 0.85)
        self.stagnation_rates_std_dev = trigger_params.get('trigger_stagnation_rates_std_dev', 0.1)
        self.stagnation_throughput_ratio = trigger_params.get('trigger_stagnation_throughput_ratio', 0.7)

        # 初始化自适应历史标杆
        self.adaptive_benchmark = 1000.0  # 可以设置一个合理的初始值
        self.historical_max_throughput = 1.0  # 记录历史最高吞吐

    def should_infer(self, performance_report, all_rates):
        """
        主判断函数：决定是否应该触发推断。

        Args:
            performance_report (dict): 包含本轮各组件真实效用值的报告。
            all_rates (list): 包含本轮所有备选速率的列表 [r_cl, r_rl, r_prev]。

        Returns:
            bool: 如果需要推断则返回True，否则返回False。
        """
        # --- 首先，更新自适应历史标杆 ---
        utilities = [v[0] for v in performance_report.values()]
        U_max_current = max(utilities) if utilities else self.adaptive_benchmark
        self._update_adaptive_benchmark(U_max_current)

        # --- 引擎一：相对表现检查 ---
        is_underperforming = self._check_relative_performance(utilities)

        # --- 引擎二：“性能高原”探测 ---
        # 假设我们可以从network_env获取延迟梯度等信息
        is_stagnated = self._check_stagnation(all_rates)

        # --- 最终裁决 ---
        if is_underperforming or is_stagnated:
            print(f"[触发器] 触发推断! (表现不佳: {is_underperforming}, 陷入停滞: {is_stagnated})")
            return True

        return False

    def _update_adaptive_benchmark(self, U_max_current):
        """使用EWMA更新自适应历史标杆。"""
        self.adaptive_benchmark = (1 - self.benchmark_alpha) * self.adaptive_benchmark + \
                                  self.benchmark_alpha * U_max_current

    def _check_relative_performance(self, utilities):
        """检查所有组件的表现是否都低于自适应历史标杆。"""
        threshold = self.activation_k * self.adaptive_benchmark
        # 检查是否所有效用值都低于阈值
        return all(u < threshold for u in utilities)

    def _check_stagnation(self, all_rates):
        """检查系统是否陷入“性能高原”僵局。"""
        # --- 待实现 ---
        # 这个检查比较复杂，需要获取更多网络状态信息
        # 1. 检查意见趋同: rates_are_close = np.std(all_rates) < self.stagnation_rates_std_dev
        # 2. 检查表现稳定: gradients_are_stable = ... (所有延迟梯度都为0或负)
        # 3. 检查潜力巨大: throughput_is_low = current_max_throughput < self.stagnation_throughput_ratio * self.historical_max_throughput
        # return rates_are_close and gradients_are_stable and throughput_is_low
        return False  # 暂时返回False