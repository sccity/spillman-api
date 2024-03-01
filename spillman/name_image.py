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
import json, logging, xmltodict, traceback, collections, requests
import spillman as s
import urllib.request as urlreq
from flask_restful import Resource, Api, request
from flask import jsonify, abort
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from .database import db

err = SetupLogger("name_image", "name_image")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class NameImage(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]

    def data_exchange(self, name_id):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <Images>
                        <Parnum search_type="equal_to">{name_id}</Parnum>
                        <Partype search_type="equal_to">nmmain</Partype>
                        <Thumb1 search_type="equal_to">Y</Thumb1>
                    </Images>
                </Query>
            </PublicSafety>
        </PublicSafetyEnvelope>
        """

        try:
            headers = {"Content-Type": "application/xml"}
            try:
                xml = session.post(
                    self.api_url, data=request, headers=headers, verify=False
                )
                decoded = xml.content.decode("utf-8")
                data = json.loads(json.dumps(xmltodict.parse(decoded)))
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"][
                    "Images"
                ]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return

        except:
            err.error(traceback.format_exc())
            return

        return data

    def process(self, name_id):
        spillman = self.data_exchange(name_id)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                image_file = spillman.get("Name")
            except:
                image_file = ""

            data.append(
                {
                    "name_id": name_id,
                    "image_path": "/sds/files/images/",
                    "image_file": image_file,
                }
            )

        else:
            for row in spillman:
                try:
                    image_file = row["Name"]
                except:
                    image_file = ""

                data.append(
                    {
                        "name_id": name_id,
                        "image_path": "/sds/files/images/",
                        "image_file": image_file,
                    }
                )

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        name_id = args.get("name_id", default="", type=str)

        if token == "":
            s.AuthService.audit_request(
                "Missing", request.access_route[0], "AUTH", f"ACCESS DENIED"
            )
            return jsonify(error="No security token provided.")

        auth = s.AuthService.validate_token(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        s.AuthService.audit_request(
            token, request.access_route[0], "nameImage", json.dumps([args])
        )

        return self.process(name_id)
