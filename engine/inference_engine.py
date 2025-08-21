# 学习式速率推断引擎（GBDT模型加载与调用）
# genet_project/engine/inference_engine.py

import joblib  # 用于加载/保存Scikit-learn模型 (GBDT)
from core.utility import calculate_utility


class LearnedInferenceEngine:
    """
    实现了学习式速率推断引擎。
    该模块负责加载预训练的GBDT模型，并提供两种核心服务：
    1. 估算网络状态 (C_est, R_est) 以支持虚拟评估。
    2. 在“两者皆差”时，推断并验证最优发送速率。
    """

    def __init__(self, config, network_env):
        """
        初始化推断引擎，加载模型。
        """
        self.config = config
        self.network_env = network_env  # 用于推断后验证

        # 从配置文件中获取模型路径
        model_path = config.get('models', {}).get('inference_engine_path', 'models/inference_engine.gbdt')

        try:
            self.model = joblib.load(model_path)
            print(f"GBDT model loaded successfully from {model_path}")
        except FileNotFoundError:
            print(f"Warning: GBDT model not found at {model_path}. Inference will not work.")
            self.model = None

    def estimate_network_conditions(self, network_state):
        """
        职责一：作为“危机评估顾问”，估算C和R。
        """
        if not self.model:
            # 如果模型不存在，返回默认值
            return {'C_est': 100, 'R_est': 10}  # 返回默认的估算值

        # GBDT模型被设计为多输出，可以同时预测C和R
        # 假设模型的predict方法返回一个包含所有预测值的字典
        predictions = self.model.predict([network_state])  # 模型输入需要是2D数组

        estimated_conditions = {
            'C_est': predictions['C_est'][0],
            'R_est': predictions['R_est'][0]
        }
        return estimated_conditions

    def infer_and_confirm(self, performance_report):
        """
        职责二：作为“最终决策仲裁者”，实现完整的“推断确认协议”。
        """
        print("--- [推断引擎] 启动推断确认协议 ---")
        if not self.model:
            print("模型不存在，无法推断。将返回本轮最高分速率。")
            # 降级处理：返回本轮表现最好的算法的建议速率
            best_component_name = max(performance_report, key=lambda k: performance_report[k][0])
            best_component = performance_report[best_component_name][1]
            return best_component.get_suggested_rate({})

        # 1. 初步推断：从GBDT获取建议速率
        current_network_state = self.network_env.get_current_state()
        predictions = self.model.predict([current_network_state])
        r_candidate = predictions['r_opt'][0]
        print(f"初步推断建议速率: {r_candidate:.2f} Mbps")

        # 2. 真实验证：占用1个RTT，真实地运行r_candidate
        print("进行1 RTT真实验证...")
        feedback_candidate = self.network_env.run_rate_for_one_rtt(r_candidate)
        U_candidate = calculate_utility(feedback_candidate, self.config['utility_params'])
        print(f"验证效用值 U_candidate: {U_candidate:.2f}")

        # 3. 最终裁决：比较三者，选择最高分
        U_cubic = performance_report['CUBIC'][0]
        U_sage = performance_report['Sage'][0]

        if U_candidate >= U_cubic and U_candidate >= U_sage:
            print("裁决结果: 推断速率胜出！")
            return r_candidate
        elif U_cubic >= U_sage:
            print("裁决结果: CUBIC胜出！")
            return self.network_env.get_component_by_name('CUBIC').get_suggested_rate(current_network_state)
        else:
            print("裁决结果: Sage胜出！")
            return self.network_env.get_component_by_name('Sage').get_suggested_rate(current_network_state)