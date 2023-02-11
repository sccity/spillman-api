# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.#
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
import os, logging, time
from logging.handlers import SMTPHandler
from spillman.settings import settings_data


formatter = logging.Formatter(
    "%(levelname)s - %(asctime)s\nFunction: %(funcName)s\nMessage:\n%(message)s\n"
)


def setup_logger(name, log_file, level=settings_data["global"]["loglevel"]):
    log_path = os.path.exists("./logs/")
    if not log_path:
        os.makedirs("./logs")
    handler = logging.FileHandler(f"./logs/{log_file}.log")
    handler.setFormatter(formatter)

    credentials = (
        settings_data["global"]["smtp"]["user"],
        settings_data["global"]["smtp"]["pass"],
    )

    mail_handler = SMTPHandler(
        mailhost=(
            settings_data["global"]["smtp"]["host"],
            settings_data["global"]["smtp"]["port"],
        ),
        fromaddr=settings_data["global"]["smtp"]["from"],
        toaddrs=settings_data["global"]["smtp"]["to"],
        subject="Spillman API",
        credentials=credentials,
        secure=(),
    )
    mail_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(settings_data["global"]["loglevel"])
    logger.propagate = False
    logger.addHandler(handler)
    logger.addHandler(mail_handler)

    return logger
