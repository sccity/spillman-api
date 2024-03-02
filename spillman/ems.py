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
import spillman as s
from flask_restful import Resource, request
from flask import jsonify, abort
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from cachetools import cached, TTLCache

err = SetupLogger("ems", "ems")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Ems(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]

    @cached(TTLCache(maxsize=500, ttl=1800))
    def data_exchange(self, agency, incident_id, call_id, start, end):
        if incident_id == "*":
            start_date = date(
                int(start[0:4]), int(start[5:7]), int(start[8:10])
            ) - timedelta(days=1)
            start_date = str(start_date.strftime("%m/%d/%Y"))

            end_date = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(
                days=1
            )
            end_date = str(end_date.strftime("%m/%d/%Y"))
        elif call_id == "*":
            start_date = date(
                int(start[0:4]), int(start[5:7]), int(start[8:10])
            ) - timedelta(days=1)
            start_date = str(start_date.strftime("%m/%d/%Y"))

            end_date = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(
                days=1
            )
            end_date = str(end_date.strftime("%m/%d/%Y"))
        else:
            start_date = "01/01/1900"
            end_date = "12/31/9999"

        if incident_id is not None and incident_id != "*":
            start_date = "01/01/1900"
            end_date = "12/31/9999"
        if call_id is not None and call_id != "*":
            start_date = "01/01/1900"
            end_date = "12/31/9999"

        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <emmain>
                        <agency search_type="equal_to">{agency}</agency>
                        <number search_type="equal_to">{incident_id}</number>
                        <callid search_type="equal_to">{call_id}</callid>
                        <dispdat search_type="greater_than">{start_date}</dispdat>
                        <dispdat search_type="less_than">{end_date}</dispdat>
                    </emmain>
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
                    "emmain"
                ]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return

        except Exception as e:
            err.error(traceback.format_exc())
            return

        return data

    def process(self, agency, incident_id, call_id, start, end, page, limit):
        spillman = self.data_exchange(agency, incident_id, call_id, start, end)
        data = []

        if spillman is None:
            return

        elif isinstance(spillman, dict):
            try:
                callid = spillman.get("callid")
            except:
                callid = ""

            try:
                incident_id = spillman.get("number")
            except:
                incident_id = ""

            try:
                nature = spillman.get("nature")
            except:
                nature = ""

            try:
                address = spillman.get("address")
                address = address.replace('"', "")
                address = address.replace("'", "")
                address = address.replace(";", "")
            except:
                address = ""

            try:
                city = spillman.get("city")
            except:
                city = ""

            try:
                state = spillman.get("state")
            except:
                state = ""

            try:
                zipcode = spillman.get("zip")
            except:
                zipcode = ""

            try:
                location = spillman.get("locatn")
            except:
                location = ""

            try:
                agency = spillman.get("agency")
            except:
                agency = ""

            try:
                occurred_dt1 = spillman.get("ocurdt1")
                occurred_dt1 = f"{occurred_dt1[15:19]}-{occurred_dt1[9:11]}-{occurred_dt1[12:14]} {occurred_dt1[0:8]}"
            except:
                occurred_dt1 = "1900-01-01 00:00:00"

            try:
                occurred_dt2 = spillman.get("ocurdt2")
                occurred_dt2 = f"{occurred_dt2[15:19]}-{occurred_dt2[9:11]}-{occurred_dt2[12:14]} {occurred_dt2[0:8]}"
            except:
                occurred_dt2 = "1900-01-01 00:00:00"

            try:
                reported_dt = spillman.get("dtrepor")
                reported_dt = f"{reported_dt[15:19]}-{reported_dt[9:11]}-{reported_dt[12:14]} {reported_dt[0:8]}"
            except:
                reported_dt = "1900-01-01 00:00:00"

            try:
                dispatch_dt = spillman.get("dispdat")
                dispatch_dt = f"{dispatch_dt[6:10]}-{dispatch_dt[0:2]}-{dispatch_dt[3:5]} 00:00:00"
            except:
                dispatch_dt = "1900-01-01 00:00:00"

            try:
                condition = spillman.get("condtkn")
            except:
                condition = ""

            try:
                disposition = spillman.get("dispos")
            except:
                disposition = ""

            try:
                howrc = spillman.get("howrc")
            except:
                howrc = ""

            if howrc == "2":
                how_received = "CAD2CAD"
            elif howrc == "9":
                how_received = "911 Line"
            elif howrc == "T":
                how_received = "Telephone"
            elif howrc == "O":
                how_received = "Officer Report"
            elif howrc == "R":
                how_received = "Radio"
            elif howrc == "P":
                how_received = "In Person"
            else:
                how_received = "Other"

            data.append(
                {
                    "call_id": callid,
                    "incident_id": incident_id,
                    "agency": agency,
                    "nature": nature,
                    "zone": location,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zipcode,
                    "received_type": how_received,
                    "condition": condition,
                    "disposition": disposition,
                    "occurred_dt1": occurred_dt1,
                    "occurred_dt2": occurred_dt2,
                    "reported": reported_dt,
                    "date": dispatch_dt,
                }
            )

        else:
            for row in spillman:
                try:
                    callid = row["callid"]
                except:
                    callid = ""

                try:
                    incident_id = row["number"]
                except:
                    incident_id = ""

                try:
                    nature = row["nature"]
                except:
                    nature = ""

                try:
                    address = row["address"]
                    address = address.replace('"', "")
                    address = address.replace("'", "")
                    address = address.replace(";", "")
                except:
                    address = ""

                try:
                    city = row["city"]
                except:
                    city = ""

                try:
                    state = row["state"]
                except:
                    state = ""

                try:
                    zipcode = row["zip"]
                except:
                    zipcode = ""

                try:
                    location = row["locatn"]
                except:
                    location = ""

                try:
                    agency = row["agency"]
                except:
                    agency = ""

                try:
                    occurred_dt1 = row["ocurdt1"]
                    occurred_dt1 = f"{occurred_dt1[15:19]}-{occurred_dt1[9:11]}-{occurred_dt1[12:14]} {occurred_dt1[0:8]}"
                except:
                    occurred_dt1 = "1900-01-01 00:00:00"

                try:
                    occurred_dt2 = row["ocurdt2"]
                    occurred_dt2 = f"{occurred_dt2[15:19]}-{occurred_dt2[9:11]}-{occurred_dt2[12:14]} {occurred_dt2[0:8]}"
                except:
                    occurred_dt2 = "1900-01-01 00:00:00"

                try:
                    reported_dt = row["dtrepor"]
                    reported_dt = f"{reported_dt[15:19]}-{reported_dt[9:11]}-{reported_dt[12:14]} {reported_dt[0:8]}"
                except:
                    reported_dt = "1900-01-01 00:00:00"

                try:
                    dispatch_dt = row["dispdat"]
                    dispatch_dt = f"{dispatch_dt[6:10]}-{dispatch_dt[0:2]}-{dispatch_dt[3:5]} 00:00:00"
                except:
                    dispatch_dt = "1900-01-01 00:00:00"

                try:
                    condition = row["condtkn"]
                except:
                    condition = ""

                try:
                    disposition = row["dispos"]
                except:
                    disposition = ""

                try:
                    howrc = row["howrc"]
                except:
                    howrc = ""

                if howrc == "2":
                    how_received = "CAD2CAD"
                elif howrc == "9":
                    how_received = "911 Line"
                elif howrc == "T":
                    how_received = "Telephone"
                elif howrc == "O":
                    how_received = "Officer Report"
                elif howrc == "R":
                    how_received = "Radio"
                elif howrc == "P":
                    how_received = "In Person"
                else:
                    how_received = "Other"

                data.append(
                    {
                        "call_id": callid,
                        "incident_id": incident_id,
                        "agency": agency,
                        "nature": nature,
                        "zone": location,
                        "address": address,
                        "city": city,
                        "state": state,
                        "zip": zipcode,
                        "received_type": how_received,
                        "condition": condition,
                        "disposition": disposition,
                        "occurred_dt1": occurred_dt1,
                        "occurred_dt2": occurred_dt2,
                        "reported": reported_dt,
                        "date": dispatch_dt,
                    }
                )

        data = sorted(data, key=lambda x: x.get("dispatch_dt", ""), reverse=True)

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
        incident_id = args.get("incident_id", default="*", type=str)
        call_id = args.get("call_id", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)
        page = args.get("page", default=1, type=int)
        limit = args.get("limit", default=10, type=int)

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

        if start == "":
            start = datetime.today().strftime("%Y-%m-%d")

        if end == "":
            end = datetime.today().strftime("%Y-%m-%d")

        s.AuthService.audit_request(
            token, request.access_route[0], "ems", json.dumps([args])
        )

        return self.process(agency, incident_id, call_id, start, end, page, limit)
