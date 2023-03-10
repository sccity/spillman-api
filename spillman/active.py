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
from flask_restful import Resource, request
from flask import jsonify, abort
import sys, json, logging, xmltodict, traceback, collections
import requests, uuid
import spillman as s
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data

err = setup_logger("active", "active")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class active(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]

    def dataexchange(self, agency, status, ctype, city, cadcallid):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <sycad>
                        <callid search_type="equal_to">{cadcallid}</callid>
                        <agency search_type="equal_to">{agency}</agency>
                        <stat search_type="equal_to">{status}</stat>
                        <type search_type="equal_to">{ctype}</type>
                        <rtcity search_type="equal_to">{city}</rtcity>
                    </sycad>
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
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["sycad"]

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

    def process(self, agency, status, ctype, city, cadcallid):
        spillman = self.dataexchange(agency, status, ctype, city, cadcallid)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                callid = spillman.get("callid")
            except:
                callid = ""

            try:
                recid = spillman.get("recid")
            except:
                recid = ""

            agency_id = spillman.get("agency")

            try:
                zone = spillman.get("zone")
            except:
                zone = ""

            try:
                unit = spillman.get("unit")
            except:
                unit = ""

            address = spillman.get("rtaddr")
            address = address.split(";", 1)[0]

            try:
                xpos = spillman.get("xpos")
            except:
                xpos = 0

            try:
                ypos = spillman.get("ypos")
            except:
                ypos = 0

            gps_x = f"{xpos[:4]}.{xpos[4:]}"
            gps_y = f"{ypos[:2]}.{ypos[2:]}"

            reported = spillman.get("reprtd")
            sql_date = (
                f"{reported[15:19]}-{reported[9:11]}-{reported[12:14]} {reported[0:8]}"
            )

            if spillman.get("type") == "l":
                call_type = "Law"
            elif spillman.get("type") == "f":
                call_type = "Fire"
            elif spillman.get("type") == "e":
                call_type = "EMS"
            else:
                call_type = "Other"

            try:
                status = spillman.get("stat")
            except:
                status = ""

            try:
                nature = spillman.get("nature")
            except:
                nature = ""

            try:
                city = spillman.get("rtcity")
            except:
                city = ""

            data.append(
                {
                    "call_id": callid,
                    "incident_id": recid,
                    "agency": agency_id,
                    "nature": nature,
                    "zone": zone,
                    "responsible_unit": unit,
                    "address": address,
                    "city": city,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "type": call_type,
                    "status": status,
                    "date": sql_date,
                }
            )

        else:
            for row in spillman:
                try:
                    callid = row["callid"]

                    try:
                        recid = row["recid"]
                    except:
                        recid = ""

                    agency_id = row["agency"]

                    try:
                        zone = row["zone"]
                    except:
                        zone = ""

                    try:
                        unit = row["unit"]
                    except:
                        unit = ""

                    address = row["rtaddr"]
                    address = address.split(";", 1)[0]

                    try:
                        xpos = row["xpos"]
                    except:
                        xpos = 0

                    try:
                        ypos = row["ypos"]
                    except:
                        ypos = 0

                    try:
                        gps_x = f"{xpos[:4]}.{xpos[4:]}"
                    except:
                        gps_x = 0

                    try:
                        gps_y = f"{ypos[:2]}.{ypos[2:]}"
                    except:
                        gps_y = 0

                    try:
                        reported = row["reprtd"]
                        sql_date = f"{reported[15:19]}-{reported[9:11]}-{reported[12:14]} {reported[0:8]}"
                    except:
                        sql_date = "1900-01-01 00:00:00"

                    if row["type"] == "l":
                        call_type = "Law"
                    elif row["type"] == "f":
                        call_type = "Fire"
                    elif row["type"] == "e":
                        call_type = "EMS"
                    else:
                        call_type = "Other"

                    try:
                        status = row["stat"]
                    except:
                        status = ""

                    try:
                        nature = row["nature"]
                    except:
                        nature = ""

                    try:
                        city = row["rtcity"]
                    except:
                        city = ""

                except:
                    continue

                data.append(
                    {
                        "call_id": callid,
                        "incident_id": recid,
                        "agency": agency_id,
                        "nature": nature,
                        "zone": zone,
                        "responsible_unit": unit,
                        "address": address,
                        "city": city,
                        "latitude": gps_y,
                        "longitude": gps_x,
                        "type": call_type,
                        "status": status,
                        "date": sql_date,
                    }
                )

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        cadcallid = args.get("callid", default="*", type=str)
        agency = args.get("agency", default="*", type=str)
        status = args.get("status", default="*", type=str)
        ctype = args.get("type", default="*", type=str)
        city = args.get("city", default="*", type=str)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", "ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        s.auth.audit(
            token,
            request.access_route[0],
            "SYCAD",
            f"CALLID: {cadcallid} AGENCY: {agency} STATUS: {status} TYPE: {ctype} CITY: {city}",
        )

        return self.process(agency, status, ctype, city, cadcallid)
