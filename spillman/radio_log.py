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
from flask_restful import Resource, Api, request
from flask import jsonify, abort
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from .database import db
from cachetools import cached, TTLCache

err = SetupLogger("radio_log", "radio_log")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class RadioLog(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]

    @cached(TTLCache(maxsize=500, ttl=120))
    def data_exchange(self, agency, unit, callid, status, start, end):
        start_date = date(
            int(start[0:4]), int(start[5:7]), int(start[8:10])
        ) - timedelta(days=1)
        start_date = str(start_date.strftime("%m/%d/%Y"))
        start_date = f"23:59:59 {start_date}"
        end_date = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(
            days=1
        )
        end_date = str(end_date.strftime("%m/%d/%Y"))
        end_date = f"00:00:00 {end_date}"

        session = requests.Session()
        session.auth = (self.api_user, self.api_password)

        if callid == "*":
            request = f"""
            <PublicSafetyEnvelope version="1.0">
                <From>Spillman API - XML to JSON</From>
                <PublicSafety id="">
                    <Query>
                        <rlmain>
                            <agency search_type="equal_to">{agency}</agency>
                            <unit search_type="equal_to">{unit}</unit>
                            <callid search_type="equal_to">{callid}</callid>
                            <tencode search_type="equal_to">{status}</tencode>
                            <logdate search_type="greater_than">{start_date}</logdate>
                            <logdate search_type="less_than">{end_date}</logdate>
                        </rlmain>
                    </Query>
                </PublicSafety>
            </PublicSafetyEnvelope>
             """

        else:
            request = f"""
            <PublicSafetyEnvelope version="1.0">
                <PublicSafety id="">
                    <Query>
                        <rlmain>
                            <agency search_type="equal_to">{agency}</agency>
                            <unit search_type="equal_to">{unit}</unit>
                            <callid search_type="equal_to">{callid}</callid>
                            <tencode search_type="equal_to">{status}</tencode>
                        </rlmain>
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
                    "rlmain"
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

            if error.find("'NoneType'") != -1:
                return

            else:
                err.error(traceback.format_exc())
                return

        return data

    def process(self, agency, unit, callid, status, start, end, page, limit):
        spillman = self.data_exchange(agency, unit, callid, status, start, end)
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
                xpos = spillman.get("xpos")
            except:
                xpos = 0

            try:
                ypos = spillman.get("ypos")
            except:
                ypos = 0

            try:
                gps_x = f"{row['xpos'][:4]}.{row['xpos'][4:]}"
            except:
                gps_x = 0

            try:
                gps_y = f"{row['ypos'][:2]}.{row['ypos'][2:]}"
            except:
                gps_y = 0

            try:
                callid = spillman.get("callid")
            except:
                callid = ""

            try:
                agency = spillman.get("agency")
            except:
                agency = ""

            try:
                zone = spillman.get("zone")
            except:
                zone = ""

            try:
                tencode = spillman.get("tencode")
            except KeyError:
                tencode = ""

            try:
                unit = spillman.get("unit")
            except:
                unit = ""

            try:
                description = spillman.get("desc")
                description = description.replace('"', "")
                description = description.replace("'", "")
            except:
                description = ""

            try:
                calltype = spillman.get("calltyp")
            except:
                calltype = ""

            data.append(
                {
                    "call_id": callid,
                    "agency": agency,
                    "unit": unit,
                    "status": tencode,
                    "zone": zone,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "description": description,
                    "date": logdate,
                }
            )

        else:
            for row in spillman:
                try:
                    date = row["logdate"]
                    logdate = f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
                except:
                    logdate = "1900-01-01 00:00:00"

                try:
                    gps_x = f"{row['xpos'][:4]}.{row['xpos'][4:]}"
                except:
                    gps_x = 0

                try:
                    gps_y = f"{row['ypos'][:2]}.{row['ypos'][2:]}"
                except:
                    gps_y = 0

                try:
                    callid = row["callid"]
                except:
                    callid = ""

                try:
                    agency = row["agency"]
                except:
                    agency = ""

                try:
                    zone = row["zone"]
                except:
                    zone = ""

                try:
                    tencode = row["tencode"]
                except KeyError:
                    tencode = ""

                try:
                    unit = row["unit"]
                except:
                    unit = ""

                try:
                    description = row["desc"]
                    description = description.replace('"', "")
                    description = description.replace("'", "")
                except:
                    description = ""

                try:
                    calltype = row["calltyp"]
                except:
                    calltype = ""

                data.append(
                    {
                        "call_id": callid,
                        "agency": agency,
                        "unit": unit,
                        "status": tencode,
                        "zone": zone,
                        "latitude": gps_y,
                        "longitude": gps_x,
                        "description": description,
                        "date": logdate,
                    }
                )

        data = sorted(data, key=lambda x: x.get("logdate", ""), reverse=True)

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        return paginated_data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        agency = args.get("agency", default="*", type=str)
        unit = args.get("unit", default="*", type=str)
        callid = args.get("callid", default="*", type=str)
        status = args.get("status", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)
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

        if start == "":
            start = datetime.today().strftime("%Y-%m-%d")

        if end == "":
            end = datetime.today().strftime("%Y-%m-%d")

        s.AuthService.audit_request(
            token, request.access_route[0], "radiolog", json.dumps([args])
        )

        return self.process(agency, unit, callid, status, start, end, page, limit)
