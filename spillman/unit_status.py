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
import json, xmltodict, traceback, requests
import threading
import spillman as s
from flask_restful import Resource, request
from flask import jsonify, abort
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from cachetools import cached, TTLCache

err = SetupLogger("unit_status", "unit_status")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class UnitStatus(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]
        self.f = s.SpillmanFunctions()

    @cached(TTLCache(maxsize=1500, ttl=300))
    def data_exchange(self, unit, agency, zone, utype, kind, callid):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <syunit>
                        <unit search_type="equal_to">{unit}</unit>
                        <agency search_type="equal_to">{agency}</agency>
                        <zone search_type="equal_to">{zone}</zone>
                        <utype search_type="equal_to">{utype}</utype>
                        <kind search_type="equal_to">{kind}</kind>
                        <callid search_type="equal_to">{callid}</callid>
                    </syunit>
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
                    "syunit"
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

    def process_row(self, row, data):
        try:
            unit = row["unit"]
        except:
            unit = ""

        try:
            status = row["stcode"]
        except:
            status = ""

        try:
            status_time = row["stime"]
            sql_date = f"{status_time[15:19]}-{status_time[9:11]}-{status_time[12:14]} {status_time[0:8]}"
        except:
            sql_date = "1900-01-01 00:00:00"

        try:
            agency = row["agency"]
        except:
            agency = ""

        try:
            zone = row["zone"]
        except:
            zone = ""

        try:
            if row["utype"] == "l":
                utype = "Law"
            elif row["utype"] == "f":
                utype = "Fire"
            elif row["utype"] == "e":
                utype = "EMS"
            else:
                utype = "Other"
        except:
            utype = "Other"

        try:
            kind = row["kind"]
        except:
            kind = ""

        try:
            station = row["statn"]
        except:
            station = ""

        try:
            gps_x = f"{xpos[:4]}.{xpos[4:]}"
        except:
            gps_x = 0

        try:
            gps_y = f"{ypos[:2]}.{ypos[2:]}"
        except:
            gps_y = 0

        try:
            callid = row["callid"]
        except:
            callid = ""

        try:
            desc = row["desc"]
        except:
            desc = ""

        try:
            if status != "OFFDT":
                name = self.f.get_unit_name(unit)
            else:
                name = ""
        except:
            name = ""

        data.append(
            {
                "unit": unit,
                "status": status,
                "status_time": sql_date,
                "call_id": callid,
                "agency": agency,
                "zone": zone,
                "type": utype,
                "kind": kind,
                "station": station,
                "latitude": gps_y,
                "longitude": gps_x,
                "description": desc,
                "name": name,
            }
        )

    def process(self, unit, agency, zone, utype, kind, callid, page, limit):
        spillman = self.data_exchange(unit, agency, zone, utype, kind, callid)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                unit = spillman.get("unit")
            except:
                unit = ""

            try:
                status = spillman.get("stcode")
            except:
                status = ""

            try:
                status_time = spillman.get("stime")
                sql_date = f"{status_time[15:19]}-{status_time[9:11]}-{status_time[12:14]} {status_time[0:8]}"
            except:
                sql_date = "1900-01-01 00:00:00"

            try:
                agency = spillman.get("agency")
            except:
                agency = ""

            try:
                zone = spillman.get("zone")
            except:
                zone = ""

            if spillman.get("utype") == "l":
                utype = "Law"
            elif spillman.get("utype") == "f":
                utype = "Fire"
            elif spillman.get("utype") == "e":
                utype = "EMS"
            else:
                utype = "Other"

            try:
                kind = spillman.get("kind")
            except:
                kind = ""

            try:
                station = spillman.get("statn")
            except:
                station = ""

            try:
                gps_x = f"{xpos[:4]}.{xpos[4:]}"
            except:
                gps_x = 0

            try:
                gps_y = f"{ypos[:2]}.{ypos[2:]}"
            except:
                gps_y = 0

            try:
                callid = spillman.get("callid")
            except:
                callid = ""

            try:
                desc = spillman.get("desc")
            except:
                desc = ""

            try:
                name = self.f.get_unit_name(unit)
            except:
                name = ""

            data.append(
                {
                    "unit": unit,
                    "status": status,
                    "status_time": sql_date,
                    "call_id": callid,
                    "agency": agency,
                    "zone": zone,
                    "type": utype,
                    "kind": kind,
                    "station": station,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "description": desc,
                    "name": name,
                }
            )

        else:
            threads = []
            for row in spillman:
                try:
                    thread = threading.Thread(target=self.process_row, args=(row, data))
                    threads.append(thread)
                    thread.start()
                except:
                    err.error(traceback.format_exc())
                    continue

            for thread in threads:
                thread.join()

        data = sorted(data, key=lambda x: x.get("status_time", ""), reverse=True)

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        return paginated_data

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
        callid = args.get("callid", default="*", type=str)
        page = args.get("page", default=1, type=int)
        limit = args.get("limit", default=10, type=int)

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
            token, request.access_route[0], "unitstatus", json.dumps([args])
        )

        return self.process(unit, agency, zone, utype, kind, callid, page, limit)
