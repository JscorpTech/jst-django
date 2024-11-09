import logging
from colorlog import StreamHandler, ColoredFormatter

handler = StreamHandler()
handler.setFormatter(
    ColoredFormatter("%(log_color)s %(asctime)s %(levelname)s %(message)s")
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)