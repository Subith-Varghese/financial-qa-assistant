import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
log_path = os.path.join(LOG_DIR, log_file)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)