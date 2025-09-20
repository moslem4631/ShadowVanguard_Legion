# utils/logger_config.py (نسخه 2.0)
import logging
import sys
from pathlib import Path

def setup_logging(project_root: Path, log_level=logging.INFO):
    """Sets up the central logging system."""
    log_format = logging.Formatter(
        fmt="%(asctime)s - [%(levelname)-8s] - (%(name)-22s) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    
    # فایل لاگ در ریشه پروژه ساخته می‌شود
    log_file_path = project_root / "legion_activity.log"
    file_handler = logging.FileHandler(log_file_path, mode='w') # 'w' to overwrite
    file_handler.setFormatter(log_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    
    logging.info("Logger configuration complete.")