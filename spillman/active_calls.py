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
from .log import SetupLogger
from .settings import settings_data

err = SetupLogger("active_calls", "active_calls")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ActiveCalls(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]
        self.f = s.SpillmanFunctions()

    def data_exchange(self, agency, status, call_type, city, cad_call_id):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <sycad>
                        <callid search_type="equal_to">{cad_call_id}</callid>
                        <agency search_type="equal_to">{agency}</agency>
                        <stat search_type="equal_to">{status}</stat>
                        <type search_type="equal_to">{call_type}</type>
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

    def process(self, agency, status, call_type, city, cad_call_id, page, limit):
        spillman = self.data_exchange(agency, status, call_type, city, cad_call_id)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            callid = self.f.validate_string(spillman.get("callid"))
            recid = self.f.validate_string(spillman.get("recid"))
            agency_id = self.f.validate_string(spillman.get("agency"))
            zone = self.f.validate_string(spillman.get("zone"))
            unit = self.f.validate_string(spillman.get("unit"))
            address = self.f.validate_string(spillman.get("rtaddr"))
            address = address.split(";", 1)[0]
            xpos = self.f.validate_number(spillman.get("xpos"))
            ypos = self.f.validate_number(spillman.get("ypos"))
            gps_x = f"{xpos[:4]}.{xpos[4:]}"
            gps_y = f"{ypos[:2]}.{ypos[2:]}"
            reported_dt = self.f.validate_datetime(spillman.get("reprtd"))
            status = self.f.validate_string(spillman.get("stat"))
            nature = self.f.validate_string(spillman.get("nature"))
            city = self.f.validate_string(spillman.get("rtcity"))

            if spillman.get("type") == "l":
                call_type = "Law"
            elif spillman.get("type") == "f":
                call_type = "Fire"
            elif spillman.get("type") == "e":
                call_type = "EMS"
            else:
                call_type = "Other"

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
                    "date": reported_dt,
                }
            )

        else:
            for row in spillman:
                try:
                    callid = self.f.validate_string(row.get("callid", ""))
                    recid = self.f.validate_string(row.get("recid", ""))
                    agency_id = self.f.validate_string(row.get("agency", ""))
                    zone = self.f.validate_string(row.get("zone", ""))
                    unit = self.f.validate_string(row.get("unit", ""))
                    address = self.f.validate_string(row.get("rtaddr", ""))
                    address = address.split(";", 1)[0]
                    xpos = self.f.validate_number(row.get("xpos", ""))
                    ypos = self.f.validate_number(row.get("ypos", ""))
                    gps_x = f"{xpos[:4]}.{xpos[4:]}"
                    gps_y = f"{ypos[:2]}.{ypos[2:]}"
                    reported_dt = self.f.validate_datetime(row.get("reprtd", ""))
                    status = self.f.validate_string(row.get("stat", ""))
                    nature = self.f.validate_string(row.get("nature", ""))
                    city = self.f.validate_string(row.get("rtcity", ""))
        
                    if row.get("type") == "l":
                        call_type = "Law"
                    elif row.get("type") == "f":
                        call_type = "Fire"
                    elif row.get("type") == "e":
                        call_type = "EMS"
                    else:
                        call_type = "Other"

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
                        "date": reported_dt,
                    }
                )

        data = sorted(data, key=lambda x: x.get("date", ""), reverse=True)

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        return paginated_data

    #@s.app.route('/cad/active', methods=['POST'])
    def get(self):
        """Register a new user"""
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        cad_call_id = args.get("callid", default="*", type=str)
        agency = args.get("agency", default="*", type=str)
        status = args.get("status", default="*", type=str)
        call_type = args.get("type", default="*", type=str)
        city = args.get("city", default="*", type=str)
        page = args.get("page", default=1, type=int)
        limit = args.get("limit", default=100, type=int)

        if token == "":
            s.AuthService.audit_request(
                "Missing", request.access_route[0], "AUTH", "ACCESS DENIED"
            )
            return jsonify(error="No security token provided.")

        auth = s.AuthService.validate_token(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        s.AuthService.audit_request(
            token, request.access_route[0], "active", json.dumps([args])
        )

        return self.process(agency, status, call_type, city, cad_call_id, page, limit)
