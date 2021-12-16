from loguru import logger
import sys
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
