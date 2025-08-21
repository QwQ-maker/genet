## GBDT模型训练
# genet_project/scripts/train_model.py

import sys
import os
import yaml
import pandas as pd
import xgboost as xgb
import joblib

# --- 项目路径设置 ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from utils.logger import setup_logger


def train_inference_model(config):
    """
    读取生成的训练数据，训练GBDT推断模型，并保存。
    """
    log = setup_logger(name='ModelTrainer', log_file='model_training.log')
    log.info("Starting GBDT model training process...")

    # 1. 加载训练数据集
    data_path = os.path.join(project_root, 'data', 'training_data.csv')
    try:
        df = pd.read_csv(data_path)
        log.info(f"Successfully loaded {len(df)} training samples from {data_path}")
    except FileNotFoundError:
        log.error(f"FATAL: Training data not found at {data_path}. Please run generate_data.py first.")
        return

    # 2. 准备特征 (X) 和标签 (Y)
    # 特征是9维的网络状态向量
    feature_columns = [
        'r_cl', 'U_cl', 'dD_cl',
        'r_rl', 'U_rl', 'dD_rl',
        'r_prev', 'U_prev', 'dD_prev'
    ]
    # 标签是3个我们要预测的值
    label_columns = ['r_opt_label', 'C_label', 'R_label']

    X = df[feature_columns]
    Y = df[label_columns]

    log.info(f"Features shape: {X.shape}")
    log.info(f"Labels shape: {Y.shape}")

    # 3. 初始化并训练多输出GBDT模型
    # XGBoost本身支持多输出回归
    # 我们可以从配置文件中读取模型的超参数，以方便调优
    model_params = config.get('engine_params', {}).get('inference_engine', {}).get('model_params', {})

    log.info(f"Training XGBoost model with parameters: {model_params}")

    # 使用XGBoost的XGBRegressor，它可以直接处理多输出目标
    # 注意：较新版本的XGBoost才原生支持多输出，如果不行，
    # 也可以使用scikit-learn的MultiOutputRegressor来包装XGBRegressor
    model = xgb.XGBRegressor(**model_params)

    model.fit(X, Y)  # 训练模型

    log.info("Model training completed.")

    # 4. 保存训练好的模型
    output_dir = os.path.join(project_root, 'models')
    os.makedirs(output_dir, exist_ok=True)  # 确保文件夹存在
    model_path = os.path.join(output_dir, 'inference_engine.gbdt')

    joblib.dump(model, model_path)
    log.info(f"Trained model saved successfully to {model_path}")


if __name__ == '__main__':
    # 加载主配置文件
    config_path = os.path.join(project_root, 'config.yml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"FATAL: Could not load config file. Error: {e}")
        sys.exit(1)

    train_inference_model(config)