# genet_project/core/components.py

import numpy as np

class BaseComponent:
    """
    所有拥塞控制组件的基类 (Interface)。
    它定义了每个组件必须具备的属性和方法。
    """
    def __init__(self, name):
        self.name = name
        self.eta = 0.5  # 置信度分数 (eta)，初始为中立
        self.utility_history = [] # 用于未来可能的危机监测

    def get_suggested_rate(self, network_state):
        """
        根据当前网络状态，返回一个建议的发送速率。
        这是一个抽象方法，每个子类都必须重写它。
        """
        raise NotImplementedError

    def update_utility_history(self, utility):
        """记录最近的效用值，用于危机监测"""
        self.utility_history.append(utility)
        # 只保留最近的N个记录，例如10个
        if len(self.utility_history) > 10:
            self.utility_history.pop(0)

    def get_avg_utility(self):
        """计算近期的平均效用值"""
        if not self.utility_history:
            return 0
        return np.mean(self.utility_history)


class CubicComponent(BaseComponent):
    """
    CUBIC组件的实现。
    """
    def __init__(self):
        super().__init__("CUBIC")

    def get_suggested_rate(self, network_state):
        # --- 待实现 ---
        # 在这里，我们将调用内核中的CUBIC逻辑，或者用一个简化的模型来模拟它。
        # 目前，我们先用一个占位符。
        print(f"[{self.name}] 根据网络状态 {network_state} 计算速率...")
        # 简化模拟：假设CUBIC总是比当前速率高一点点
        suggested_rate = network_state.get('current_rate', 50) * 1.1
        return suggested_rate


class SageComponent(BaseComponent):
    """
    Sage组件的实现。
    """
    def __init__(self):
        super().__init__("Sage")
        # 在这里加载Sage的预训练神经网络模型
        # self.model = self.load_sage_model()
        print(f"[{self.name}] 正在加载Sage模型...")


    def get_suggested_rate(self, network_state):
        # --- 待实现 ---
        # 将网络状态喂给神经网络，得到建议速率。
        # 目前，我们先用一个占位符。
        print(f"[{self.name}] 根据网络状态 {network_state} 进行模型预测...")
        # 简化模拟：假设Sage总是比当前速率高很多
        suggested_rate = network_state.get('current_rate', 50) * 1.5
        return suggested_rate