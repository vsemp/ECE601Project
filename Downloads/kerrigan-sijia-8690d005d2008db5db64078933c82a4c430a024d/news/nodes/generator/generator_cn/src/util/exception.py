import traceback
import sys


class IgnoreMessage(Exception):

    def __init__(self, description=''):
        self.description = description

    def __str__(self):
        return self.description


def create_traceback_info(msg):
    traceback_info = msg.strip() + '\n'
    exc_traceback = traceback.format_tb(sys.exc_info()[2])
    for tb in exc_traceback:
        traceback_info += tb
    return traceback_info.strip()
