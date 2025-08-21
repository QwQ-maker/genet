## 模型核心
# genet_project/core/genet.py

from .components import CubicComponent, SageComponent
from .utility import calculate_utility


# 我们将智能引擎的逻辑暂时先放在这个文件里，后续再拆分
# from engine.recovery_engine import DynamicSupportProtocol
# from engine.inference_engine import LearnedInferenceEngine
# from engine.trigger_engine import DualDimensionSmartTrigger

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
        self.cubic = CubicComponent()
        self.sage = SageComponent()
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

    def run(self):
        """
        这是Genet的宏观主循环，它会周而复始地运行。
        """
        print("Genet main loop started.")
        while True:
            # --- 阶段一：评估 ---
            performance_report = self._evaluation_stage()

            # --- 阶段二：决策 ---
            primary_component, execution_rate, execution_duration = self._decision_stage(performance_report)

            # --- 阶段三：执行 ---
            self._execution_stage(primary_component, execution_rate, execution_duration)

    def _evaluation_stage(self):
        """
        在2个RTT内，真实地、交替地运行每个活跃算法，并计算其真实效用值。
        """
        print("\n--- [评估阶段] 开始 ---")
        performance_report = {}
        for component in self.components:
            # 假设 network_env.run_and_get_feedback() 返回了包含测量值的字典
            feedback = self.network_env.run_and_get_feedback(component)

            # 调用utility函数时，传入超参数配置
            utility = calculate_utility(feedback, self.config['utility_params'])
            performance_report[component.name] = (utility, component)

        print(f"评估报告: { {k: v[0] for k, v in performance_report.items()} }")
        return performance_report

    def _decision_stage(self, performance_report):
        """
        根据评估结果，进行主组件加冕、绩效考核和任期授权。
        """
        print("--- [决策阶段] 开始 ---")

        # a. 主组件加冕：选出本轮表现最好的组件
        primary_component_name = max(performance_report, key=lambda k: performance_report[k][0])
        primary_component = performance_report[primary_component_name][1]
        print(f"主组件加冕: {primary_component.name}")

        # b. 绩效考核：更新所有组件的置信度
        self._update_all_confidence_scores(performance_report)

        # c. 授权任期：根据胜出者的最新置信度，计算其任期
        execution_duration = self._calculate_adaptive_tenure(primary_component)

        # d. 决定执行速率 (在这里简化为直接使用主组件的建议速率)
        # 实际中，这里会先调用“双维智能触发器”判断是否需要推断
        execution_rate = primary_component.get_suggested_rate({})  # 传入一个空state

        return primary_component, execution_rate, execution_duration

    def _update_all_confidence_scores(self, performance_report):
        """
        根据本轮表现，用EWMA公式更新所有算法的置信度分数。
        """
        utilities = [v[0] for v in performance_report.values()]
        U_max = max(utilities) if utilities else 1  # 避免除以零

        for name, (utility, component) in performance_report.items():
            # 计算本轮表现分 (PerformanceScore)
            score = utility / U_max if U_max > 0 else (1.0 if utility > 0 else 0.0)
            score = max(0, score)  # 确保分数不为负

            # EWMA更新
            component.eta = (1 - self.alpha_ewma) * component.eta + self.alpha_ewma * score

        print(f"置信度更新: CUBIC η={self.cubic.eta:.3f}, Sage η={self.sage.eta:.3f}")

    def _calculate_adaptive_tenure(self, primary_component):
        """
        根据主组件的置信度，计算其执行周期的长度N。
        """
        eta_primary = primary_component.eta

        # 核心公式
        duration_N = self.N_min + (eta_primary ** 2) * (self.N_max - self.N_min)

        print(f"主组件信誉为 {eta_primary:.3f}, 获得任期: {int(duration_N)} RTTs")
        return int(duration_N)

    def _execution_stage(self, primary_component, execution_rate, execution_duration):
        """
        执行主组件的决策。
        (我们将在下一步加入“动态扶持”的逻辑)
        """
        print(f"--- [执行阶段] 开始，主组件: {primary_component.name}, 任期: {execution_duration} RTTs ---")
        # 模拟执行
        self.network_env.execute_for_n_rtts(primary_component, execution_rate, execution_duration)
        print(f"执行阶段完成。")