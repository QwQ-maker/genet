## 日志功能
# genet_project/utils/logger.py

import logging
import sys

def setup_logger(name='GenetLogger', log_level=logging.INFO, log_file=None):
    """
    配置并返回一个logger实例。

    Args:
        name (str): logger的名称。
        log_level (int): 日志记录的级别 (e.g., logging.INFO, logging.DEBUG)。
        log_file (str, optional): 如果提供，日志将同时输出到指定的文件。

    Returns:
        logging.Logger: 配置好的logger实例。
    """
    # 1. 创建一个logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 2. 创建一个formatter，定义日志的输出格式
    # 格式包含：时间戳 - logger名称 - 日志级别 - 消息
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 避免重复添加handler
    if not logger.handlers:
        # 3. 创建一个handler，用于将日志输出到控制台 (stdout)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # 4. 如果指定了日志文件，则创建一个handler，用于写入文件
        if log_file:
            file_handler = logging.FileHandler(log_file, mode='a') # 'a'表示追加模式
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

# -- 使用示例 --
if __name__ == '__main__':
    # 创建一个默认的logger
    log = setup_logger()
    log.info("这是一条普通的信息 (INFO)")
    log.debug("这是一条用于调试的信息 (DEBUG), 默认不显示")
    log.warning("这是一条警告信息 (WARNING)")

    print("-" * 20)

    # 创建一个更详细的logger，记录到文件
    debug_log = setup_logger(name='GenetDebugger', log_level=logging.DEBUG, log_file='debug.log')
    debug_log.info("这条INFO信息会显示在控制台和文件里")
    debug_log.debug("这条DEBUG信息也会显示在控制台和文件里")
    debug_log.error("这是一条错误信息 (ERROR)")