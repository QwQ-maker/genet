## 实验运行
# genet_project/scripts/run_experiment.py

import sys
import os
import yaml

# 为了能从脚本中正确导入项目内的其他模块，我们需要将项目根目录添加到Python的搜索路径中
# 这是一种标准的做法
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.genet import Genet
from env.network_env import NetworkEnvironment
from utils.logger import setup_logger

def run_single_experiment(config):
    """
    运行单次完整的Genet实验。
    """
    # 1. 设置日志记录器
    log = setup_logger(name='GenetExperiment', log_file='experiment.log')
    log.info("="*30)
    log.info("Starting a new Genet experiment run.")
    log.info("="*30)

    # 2. 初始化网络环境
    # network_env将负责所有与Mahimahi的交互
    log.info("Initializing network environment...")
    network_env = NetworkEnvironment(config)

    # 3. 初始化Genet算法核心，并将环境和配置注入
    log.info("Initializing Genet core algorithm...")
    genet_algorithm = Genet(config, network_env)

    # 4. 启动Genet的主循环
    # 注意：在一个真实的实验中，您可能需要在这里添加超时控制
    # 或者让run()方法在特定条件下返回，以结束实验。
    # 目前，它是一个无限循环，用于测试。
    try:
        genet_algorithm.run()
    except KeyboardInterrupt:
        log.warning("Experiment interrupted by user.")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        log.info("Experiment run finished.")
        log.info("="*30 + "\n")


if __name__ == '__main__':
    # 加载配置文件
    config_path = os.path.join(project_root, 'config.yml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"FATAL: Configuration file not found at {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"FATAL: Error parsing YAML file: {e}")
        sys.exit(1)

    # 运行实验
    run_single_experiment(config)