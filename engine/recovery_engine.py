# 动态扶持协议的核心逻辑（危机监测、虚拟评估）

# genet_project/engine/recovery_engine.py

import numpy as np


class DynamicSupportProtocol:
    """
    实现了“动态扶持”协议。
    该模块负责监测主组件是否陷入危机，并在危机发生时，
    通过虚拟评估来提升次组件的置信度。
    """

    def __init__(self, config):
        """
        初始化扶持协议所需的所有参数。
        """
        recovery_params = config.get('recovery_params', {})
        self.crisis_avg_window = recovery_params.get('crisis_avg_window', 10)
        self.crisis_decline_theta = recovery_params.get('crisis_decline_theta', 0.5)
        self.support_beta = recovery_params.get('support_beta', 0.2)
        self.support_k_activation = recovery_params.get('support_k_activation', 0.8)

    def check_crisis(self, primary_component, current_utility):
        """
        检查主组件是否陷入危机。

        Args:
            primary_component (BaseComponent): 当前的主组件。
            current_utility (float): 主组件刚刚获得的真实效用值。

        Returns:
            bool: 如果触发危机则返回True，否则返回False。
        """
        # 首先，更新主组件的效用值历史记录
        primary_component.update_utility_history(current_utility)

        # 如果历史记录还不够长，则不进行危机判断
        if len(primary_component.utility_history) < self.crisis_avg_window:
            return False

        # 计算近期平均表现水平
        avg_utility = primary_component.get_avg_utility()

        # --- 核心危机触发逻辑 ---
        # 暂时简化，只使用“相对性能衰退”条件
        if current_utility < self.crisis_decline_theta * avg_utility:
            print(f"[危机监测] {primary_component.name} 触发危机! "
                  f"当前效用值({current_utility:.2f}) < "
                  f"{self.crisis_decline_theta} * 平均效用值({avg_utility:.2f})")
            return True

        return False

    def apply_support(self, primary_component, secondary_components, inference_engine):
        """
        为所有“次组件”进行虚拟评估，并给予扶持性奖励。

        Args:
            primary_component (BaseComponent): 陷入危机的主组件。
            secondary_components (list): 所有其他的次组件。
            inference_engine (LearnedInferenceEngine): 推断引擎，用于提供C和R估算。
        """
        print(f"--- [动态扶持协议] 启动 ---")

        # 获取主组件当前的糟糕表现，作为比较基准
        primary_utility_active = primary_component.get_last_utility()

        for secondary in secondary_components:
            print(f"为次组件 {secondary.name} 进行虚拟评估...")
            # 1. 为次组件进行一次安全的虚拟评估
            #    这需要调用推断引擎来获取C和R的估算
            virtual_utility = self._virtual_evaluate(secondary, inference_engine)

            # 2. 计算扶持性奖励 (Supportive Bonus)
            #    基于相对表现
            rho = virtual_utility / primary_utility_active if primary_utility_active != 0 else float('inf')

            # 奖励公式
            reward = self.support_beta * max(0, rho - self.support_k_activation)

            if reward > 0:
                print(f"{secondary.name} 表现出潜力(ρ={rho:.2f})，获得扶持性奖励: +{reward:.3f} η")
                # 3. 将奖励加到次组件的置信度上
                secondary.eta = min(1, secondary.eta + reward)
                print(f"更新后 {secondary.name} 的置信度 η = {secondary.eta:.3f}")

    def _virtual_evaluate(self, component, inference_engine):
        """
        执行虚拟评估的核心逻辑。
        (这是我们下一个要详细实现的模块)
        """
        # --- 待实现 ---
        # 1. 让组件进行“影子决策”，得到 r_shadow
        # 2. 调用推断引擎的职责一，获取 C_est 和 R_est
        # 3. 用流体模型预测出 dD_predicted
        # 4. 计算并返回 U_virtual
        print(f"正在对 {component.name} 进行虚拟评估...")
        # 简化模拟：暂时返回一个随机的、较高的潜在效用值
        return np.random.uniform(500, 1500)