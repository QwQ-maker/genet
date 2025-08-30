## 模型核心
# genet_project/core/genet.py
import numpy as np

from .components import CubicComponent, SageComponent
from .utility import calculate_utility
# --- 导入我们真正的智能引擎模块 ---
from engine.recovery_engine import DynamicSupportProtocol
from engine.inference_engine import LearnedInferenceEngine
from engine.trigger_engine import DualDimensionSmartTrigger

class Genet:
    """
    Genet算法的核心实现，包含主循环、三大阶段等。
    """

    def __init__(self, config, network_env):
        print("Initializing Genet Framework...")

        # 1. 保存配置和网络环境的引用
        self.config = config
        self.network_env = network_env

        # 2. 初始化两个备选算法组件 (永远活跃)
        self.cubic = CubicComponent() #暂用cubic
        self.sage = SageComponent() #暂用sage
        self.components = [self.cubic, self.sage]

        # 3. 初始化置信度分数 (eta) - 每个组件的“历史绩效档案”
        self.eta_initial = self.config['genet_params']['eta_initial']
        for component in self.components:
            component.eta = self.eta_initial

        # 4. 初始化自适应任期参数
        self.N_min = self.config['genet_params']['n_min']
        self.N_max = self.config['genet_params']['n_max']

        # 5. 初始化置信度更新参数
        self.alpha_ewma = self.config['genet_params']['eta_update_alpha']

        # 6. --- 实例化三大智能引擎模块 ---
        self.support_protocol = DynamicSupportProtocol(self.config)
        self.inference_engine = LearnedInferenceEngine(self.config, self.network_env)
        self.trigger_engine = DualDimensionSmartTrigger(self.config)

    def run(self):
        """
        这是Genet的宏观主循环，它会周而复始地运行。
        """
        print("Genet main loop started.")
        while True:
            # --- 阶段一：评估 ---
            performance_report, all_rates_info = self._evaluation_stage()

            # --- 阶段二：决策 ---
            primary_component, execution_rate, execution_duration = self._decision_stage(performance_report,
                                                                                         all_rates_info)

            # --- 阶段三：执行 ---
            self._execution_stage(primary_component, execution_rate, execution_duration)

    def _evaluation_stage(self):
        """
        在2个RTT内，真实地、交替地运行每个活跃算法，并计算其真实效用值。
        """
        print("\n--- [评估阶段] 开始 ---")
        performance_report = {}
        # 触发器
        all_rates_info = {}
        for component in self.components:
            # 假设 network_env.run_and_get_feedback() 返回了包含测量值的字典
            feedback = self.network_env.run_and_get_feedback(component)

            # 调用utility函数时，传入超参数配置
            utility = calculate_utility(feedback, self.config['utility_params'])
            performance_report[component.name] = (utility, component)
            # 收集速率和梯度信息，用于后续的“高原探测”
            all_rates_info[component.name] = {
                'rate': feedback.get('sending_rate'),
                'gradient': feedback.get('rtt_gradient')
            }
        print(f"评估报告: { {k: v[0] for k, v in performance_report.items()} }")
        return performance_report, all_rates_info

    def _decision_stage(self, performance_report, all_rates_info):
        print("--- [决策阶段] 开始 ---")

        # a. 全局诊断：调用“双维智能触发器”
        needs_inference = self.trigger_engine.should_infer(performance_report, all_rates_info)

        if needs_inference:
            # e.1 如果需要推断，则调用推断引擎 (含推断后验证)
            execution_rate = self.inference_engine.infer_and_confirm(performance_report)
            primary_component = self._select_primary_component(performance_report)
        else:
            # b. 主组件加冕：选出本轮表现最好的组件
            primary_component = self._select_primary_component(performance_report)
            execution_rate = primary_component.get_suggested_rate({})  # 简化

        # c. 绩效考核：更新所有组件的置信度
        secondary_components = [c for c in self.components if c != primary_component]
        self._update_secondary_confidence_scores(performance_report, secondary_components)

        # d. 授权任期：根据胜出者的最新置信度，计算其任期
        execution_duration = self._calculate_adaptive_tenure(primary_component)

        return primary_component, execution_rate, execution_duration

    def _execution_stage(self, primary_component, execution_rate, execution_duration):
        print(f"--- [执行阶段] 开始，主组件: {primary_component.name}, 任期: {execution_duration} RTTs ---")

        tenure_utilities = [] # <--- 新增：用于记录整个任期的表现

        for rtt_count in range(execution_duration):
            current_utility = self.network_env.execute_rate_for_one_rtt(execution_rate, primary_component)
            tenure_utilities.append(current_utility) # <--- 新增：记录每个RTT的表现

            is_in_crisis = self.support_protocol.check_crisis(primary_component, current_utility)

            if is_in_crisis:
                secondary_components = [c for c in self.components if c != primary_component]
                # 注意：将推断引擎作为参数传入，以支持虚拟评估
                self.support_protocol.apply_support(primary_component, secondary_components, self.inference_engine)
        self._post_tenure_review(primary_component, tenure_utilities)
        print(f"执行阶段完成。")


    # --- 辅助函数 ---
    def _select_primary_component(self, performance_report):
        primary_component_name = max(performance_report, key=lambda k: performance_report[k][0])
        return performance_report[primary_component_name][1]

    def _update_all_confidence_scores(self, performance_report):
        utilities = [v[0] for v in performance_report.values()]
        U_max = max(utilities) if utilities else 1

        for name, (utility, component) in performance_report.items():
            score = utility / U_max if U_max > 0 else (1.0 if utility > 0 else 0.0)
            score = max(0, score)
            component.eta = (1 - self.alpha_ewma) * component.eta + self.alpha_ewma * score

        print(f"置信度更新: CUBIC η={self.cubic.eta:.3f}, Sage η={self.sage.eta:.3f}")

    def _calculate_adaptive_tenure(self, primary_component):
        eta_primary = primary_component.eta
        duration_N = self.N_min + (eta_primary ** 2) * (self.N_max - self.N_min)
        print(f"主组件信誉为 {eta_primary:.3f}, 获得任期: {int(duration_N)} RTTs")
        return int(duration_N)

    def _update_secondary_confidence_scores(self, performance_report, secondary_components):
        """
        [新功能] 只根据“评估阶段”的表现，更新次组件的置信度。
        """
        U_max = max(v[0] for v in performance_report.values()) if performance_report else 1

        for component in secondary_components:
            utility = performance_report[component.name][0]
            score = utility / U_max if U_max > 0 else 0.0
            score = max(0, score)

            # 使用EWMA公式更新
            component.eta = (1 - self.alpha_ewma) * component.eta + self.alpha_ewma * score
            print(f"  [绩效考核-次组件] {component.name} η 更新为: {component.eta:.3f}")


    def _post_tenure_review(self, component, tenure_utilities):
        """
        [新功能] 对刚刚完成任期的主组件，进行一次基于其整个任期表现的绩效评估。
        """
        if not tenure_utilities:
            return # 如果任期为0，不进行评估

        # 1. 计算“任期总评”：整个任期内的平均效用值
        avg_tenure_utility = np.mean(tenure_utilities)
        print(f"--- [任期后评估] {component.name} 的任期平均效用为: {avg_tenure_utility:.2f} ---")

        # 2. 计算归一化的表现分 (与自适应历史标杆比较)
        #    这里的 trigger_engine.adaptive_benchmark 就是我们需要的 U_adaptive_benchmark
        benchmark = self.trigger_engine.adaptive_benchmark
        score = avg_tenure_utility / benchmark if benchmark > 0 else 0.0
        score = max(0, score)

        # 3. 更新该组件的置信度分数
        component.eta = (1 - self.alpha_ewma) * component.eta + self.alpha_ewma * score
        print(f"  [绩效考核-主组件] {component.name} η 更新为: {component.eta:.3f}")
