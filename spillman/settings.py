# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
import os, sys, yaml

settings_file = "./spillman/settings.yaml"
if not os.path.exists(settings_file):
    print("settings.yaml not found!")
    sys.exit()

with open(settings_file, "r") as f:
    settings_data = yaml.load(f, Loader=yaml.FullLoader)

version_file = "./spillman/version.yaml"
if not os.path.exists(version_file):
    print("version.yaml not found!")
    sys.exit()

with open(version_file, "r") as f:
    version_data = yaml.load(f, Loader=yaml.FullLoader)
