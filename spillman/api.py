# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import Flask
from apifairy import APIFairy
from .settings import settings_data, version_data

apifairy = APIFairy()


def spillman_api():
    app = Flask(__name__)
    app.config["APIFAIRY_TITLE"] = version_data["program"]
    app.config["APIFAIRY_VERSION"] = version_data["version"]
    apifairy.init_app(app)
    return app


# flask run --host=0.0.0.0 --port=8080
# pip3 install -U -r requirements.txt
# pipreqs --force ~/spillman-api/dev

# python3 -m venv venv
# source venv/bin/activate
# deactivate
