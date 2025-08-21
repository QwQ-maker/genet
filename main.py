## 程序入口

# genet_project/main.py

import yaml  # 1. 导入PyYAML库，通常简写为yaml
from core.genet import Genet

def main():
    # 1. 加载YAML配置文件
    try:
        with open('config.yml', 'r') as f:
            # 2. 使用 yaml.safe_load() 来解析文件
            config = yaml.safe_load(f)
        print("YAML configuration loaded successfully.")
    except FileNotFoundError:
        print("Error: config.yml not found! Please create it.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    # 2. 将配置传递给Genet实例 (这部分代码完全不需要改变)
    genet_algorithm = Genet(config)

    # 3. 启动主循环 (这部分代码也完全不需要改变)
    genet_algorithm.run()


if __name__ == '__main__':
    main()