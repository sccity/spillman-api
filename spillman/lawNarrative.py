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
from .log import setup_logger
from .settings import settings_data
from .database import db

err = setup_logger("lawNarrative", "lawNarrative")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class lawNarrative(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]

    def dataexchange(self, incident_id):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <LawIncidentNarrative>
                        <number search_type="equal_to">{incident_id}</number>
                    </LawIncidentNarrative>
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
                    "LawIncidentNarrative"
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

    def process(self, incident_id):
        spillman = self.dataexchange(incident_id)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                incident_id = spillman.get("IncidentNumber")
            except:
                incident_id = ""

            try:
                narrative = spillman.get("Narrative")
            except:
                narrative = ""

            data.append(
                {
                    "incident_id": incident_id,
                    "narrative": narrative,
                }
            )

        else:
            for row in spillman:
                try:
                    incident_id = row["IncidentNumber"]
                except:
                    incident_id = ""

                try:
                    narrative = row["Narrative"]
                except:
                    narrative = ""

                data.append(
                    {
                        "incident_id": incident_id,
                        "narrative": narrative,
                    }
                )

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        incident_id = args.get("incident_id", default="", type=str)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", f"ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        s.auth.audit(token, request.access_route[0], "lawNarrative", json.dumps([args]))

        return self.process(incident_id)
