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
from flask_restful import Resource, request
from flask import jsonify, abort
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data
from .database import db

err = setup_logger("avl", "avl")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class avl(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]

    def dataexchange(self, agency, unit, start, end):
        start_date = date(
            int(start[0:4]), int(start[5:7]), int(start[8:10])
        ) - timedelta(days=1)
        start_date = str(start_date.strftime("%m/%d/%Y"))
        end_date = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(
            days=1
        )
        end_date = str(end_date.strftime("%m/%d/%Y"))

        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)

        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <rlavllog>
                        <agency search_type="equal_to">{agency}</agency>
                        <assgnmt search_type="equal_to">{unit}</assgnmt>
                        <logdate search_type="greater_than">23:59:59 {start_date}</logdate>
                        <logdate search_type="less_than">00:00:00 {end_date}</logdate>
                    </rlavllog>
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
                    "rlavllog"
                ]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return

        except Exception as e:
            error = format(str(e))
            print(error)

            if error.find("'NoneType'") != -1:
                return

            else:
                err.error(traceback.format_exc())
                return

        return data

    def process(self, agency, unit, start, end):
        spillman = self.dataexchange(agency, unit, start, end)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                date = spillman.get("logdate")
                logdate = f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
            except:
                logdate = "1900-01-01 00:00:00"

            try:
                gps_x = spillman.get("xlng")
            except:
                gps_x = 0

            try:
                gps_y = spillman.get("ylat")
            except:
                gps_y = 0

            try:
                agency = spillman.get("agency")
            except:
                agency = ""

            try:
                status = spillman.get("stcode")
            except:
                status = ""

            try:
                unit = spillman.get("assgnmt")
            except:
                unit = ""

            try:
                heading = spillman.get("heading")
            except:
                heading = ""

            try:
                speed = spillman.get("speed")
            except:
                speed = ""

            data.append(
                {
                    "agency": agency,
                    "unit": unit,
                    "status": status,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "heading": heading,
                    "speed": speed,
                    "date": logdate,
                }
            )

        else:
            for row in spillman:
                try:
                    try:
                        date = row["logdate"]
                        logdate = (
                            f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
                        )
                    except:
                        logdate = "1900-01-01 00:00:00"

                    try:
                        gps_x = row["xlng"]
                    except:
                        gps_x = 0

                    try:
                        gps_y = row["ylat"]
                    except:
                        gps_y = 0

                    try:
                        agency = row["agency"]
                    except:
                        agency = ""

                    try:
                        status = row["stcode"]
                    except:
                        status = ""

                    try:
                        unit = row["assgnmt"]
                    except:
                        unit = ""

                    try:
                        heading = row["heading"]
                    except:
                        heading = ""

                    try:
                        speed = row["speed"]
                    except:
                        speed = ""

                except:
                    continue

                data.append(
                    {
                        "agency": agency,
                        "unit": unit,
                        "status": status,
                        "latitude": gps_y,
                        "longitude": gps_x,
                        "heading": heading,
                        "speed": speed,
                        "date": logdate,
                    }
                )

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        agency = args.get("agency", default="*", type=str)
        unit = args.get("unit", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", f"ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = s.auth.check(token, request.access_route[0])

        if auth is True:
            pass
        else:
            return abort(403)

        if start == "":
            start = datetime.today().strftime("%Y-%m-%d")

        if end == "":
            end = datetime.today().strftime("%Y-%m-%d")

        s.auth.audit(
            token,
            request.access_route[0],
            "RLAVLLOG",
            f"UNIT: {unit} AGENCY: {agency} START DATE: {start} END DATE: {end}",
        )

        return self.process(agency, unit, start, end)
