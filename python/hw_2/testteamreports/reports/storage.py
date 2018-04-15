import uuid
import os
from os import path

from testteamreports.settings import REPORT_STORAGE_FOLDER


def get_storage_folder() -> str:
    report_folder = path.join(
        path.abspath(os.getcwd()),
        REPORT_STORAGE_FOLDER
    )
    if not path.isdir(report_folder):
        try:
            if path.exists(report_folder):
                raise Exception()
            os.makedirs(report_folder)
        except Exception as ex:
            raise IOError("Path {} cannot be created".format(report_folder))

    return report_folder


def get_new_file_name(extension: str) -> str:
    return path.join(
        get_storage_folder(),
        str(uuid.uuid4()) + extension)
