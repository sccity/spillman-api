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
