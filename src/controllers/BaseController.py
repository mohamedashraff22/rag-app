"""
a base controller that all other controller will inherit from it as they have some shard properties (ex: get_settings) and constructors.
"""

from helpers.config import get_settings, Settings
import os
import random
import string


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # get the directory of the current file (controller)
        self.files_dir = os.path.join(self.base_dir, "../assets/files")

    def generate_random_string(self, length: int = 12):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
