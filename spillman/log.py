# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
import sys, os, logging, time
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
        subject="Spillman API - Application Error",
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
