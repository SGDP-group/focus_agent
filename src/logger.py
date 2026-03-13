import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# File handler with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(logs_dir, f'focus_agent_{timestamp}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

logger.info("Logger initialized")