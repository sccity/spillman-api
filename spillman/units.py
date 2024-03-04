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
from flask import abort
import json, xmltodict, traceback
import requests
import spillman as s
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from cachetools import cached, TTLCache

err = SetupLogger("units", "units")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Units(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]
        self.f = s.SpillmanFunctions()

    @cached(TTLCache(maxsize=1500, ttl=1800))
    def data_exchange(self, unit, agency, zone, utype, kind):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <cdunit>
                        <unitno search_type="equal_to">{unit}</unitno>
                        <agency search_type="equal_to">{agency}</agency>
                        <zone search_type="equal_to">{zone}</zone>
                        <type search_type="equal_to">{utype}</type>
                        <kind search_type="equal_to">{kind}</kind>
                    </cdunit>
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
                    "cdunit"
                ]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return

        except Exception:
            err.error(traceback.format_exc())
            return

        return data

    def process(self, unit, agency, zone, utype, kind):
        spillman = self.data_exchange(unit, agency, zone, utype, kind)
        data = []

        if spillman is None:
            return

        elif isinstance(spillman, dict):
            try:
                unit = spillman.get("unitno")
            except Exception:
                unit = ""

            try:
                desc = spillman.get("desc")
            except Exception:
                desc = ""

            agency = spillman.get("agency")

            try:
                zone = spillman.get("zone")
            except Exception:
                zone = ""

            if spillman.get("type") == "l":
                utype = "Law"
            elif spillman.get("type") == "f":
                utype = "Fire"
            elif spillman.get("type") == "e":
                utype = "EMS"
            else:
                utype = "Other"

            try:
                kind = spillman.get("kind")
            except Exception:
                kind = ""

            try:
                station = spillman.get("station")
            except Exception:
                station = ""

            try:
                name = self.f.get_unit_name(unit)
            except Exception:
                name = ""

            try:
                contact = self.f.get_unit_contact(unit)
            except Exception:
                contact = ""

            data.append(
                {
                    "unit": unit,
                    "name": name,
                    "agency": agency,
                    "zone": zone,
                    "type": utype,
                    "kind": kind,
                    "station": station,
                    "description": desc,
                    "contact": contact,
                }
            )

        else:
            for row in spillman:
                try:
                    try:
                        unit = row["unitno"]
                    except Exception:
                        unit = ""

                    try:
                        desc = row["desc"]
                    except Exception:
                        desc = ""

                    agency = row["agency"]

                    try:
                        zone = row["zone"]
                    except Exception:
                        zone = ""

                    if row["type"] == "l":
                        utype = "Law"
                    elif row["type"] == "f":
                        utype = "Fire"
                    elif row["type"] == "e":
                        utype = "EMS"
                    else:
                        utype = "Other"

                    try:
                        kind = row["kind"]
                    except Exception:
                        kind = ""

                    try:
                        station = row["station"]
                    except Exception:
                        station = ""

                    try:
                        name = self.f.get_unit_name(unit)
                    except Exception:
                        name = ""

                    try:
                        contact = self.f.get_unit_contact(unit)
                    except Exception:
                        contact = ""

                except Exception:
                    continue

                data.append(
                    {
                        "unit": unit,
                        "name": name,
                        "agency": agency,
                        "zone": zone,
                        "type": utype,
                        "kind": kind,
                        "station": station,
                        "description": desc,
                        "contact": contact,
                    }
                )

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        unit = args.get("unit", default="*", type=str)
        agency = args.get("agency", default="*", type=str)
        zone = args.get("zone", default="*", type=str)
        utype = args.get("type", default="*", type=str)
        kind = args.get("kind", default="*", type=str)

        if (app == "" or app == "*"):
            app = "default"

        if (uid == "" or uid == "*"):
            uid = "default"

        if token == "":
            s.AuthService.audit_request(
                "Missing", request.access_route[0], "AUTH", "ACCESS DENIED"
            )
            abort(403, description="Missing or invalid security token.")

        auth = s.AuthService.validate_token(token, request.access_route[0])
        if auth is True:
            pass
        else:
            abort(401, description="Invalid or disabled security token provided.")

        s.AuthService.audit_request(
            token, request.access_route[0], "units", json.dumps([args])
        )

        return self.process(unit, agency, zone, utype, kind)
