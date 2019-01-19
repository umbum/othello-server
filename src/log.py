"""
Usage
-----
import common
common.logger.debug("string")
"""
import os, sys
import logging
import logging.handlers

formatter = logging.Formatter("%(asctime)s[%(levelname)s|%(filename)s:%(lineno)s]: %(message)s")

def addFileHandler():
    """ RotatingFileHander는 지정된 파일 크기에 도달할 때 까지 foo.log에 이어서 쓰다가
    크기가 초과하면 foo.log.1 -> foo.log.2로 밀어내고 foo.log -> foo.log.1로 만든 다음
    다시 foo.log에 쓴다. 즉, 항상 foo.log에 쓰기 때문에 이게 최신 로그이고 숫자가 클 수록 오래된 로그다.
    """
    file_max_byte = 100 * 1024 * 1024
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = BASE_PATH + "\\log\\log.txt"
    file_handler  = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=file_max_byte, backupCount=10)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def addConsoleHandler():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)



logger = logging.getLogger("othello")
logger.setLevel(logging.DEBUG)


addFileHandler()
addConsoleHandler()

if __name__ == "__main__":
    logger.log(11, "asdf")
    try:
        raise ValueError("error test")
    except Exception as e:
        logger.debug("test debug", exc_info=e)

