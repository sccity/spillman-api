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
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from cachetools import cached, TTLCache

err = SetupLogger("calls", "calls")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Calls(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]

    @cached(TTLCache(maxsize=500, ttl=1800))
    def data_exchange(self, start, end):
        start_date = date(
            int(start[0:4]), int(start[5:7]), int(start[8:10])
        ) - timedelta(days=1)
        start_date = str(start_date.strftime("%m/%d/%Y"))
        end_date = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(
            days=1
        )
        end_date = str(end_date.strftime("%m/%d/%Y"))

        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <CADMasterCallTable>
                        <TimeDateReported search_type="greater_than">{start_date}</TimeDateReported>
                        <TimeDateReported search_type="less_than">{end_date}</TimeDateReported>
                    </CADMasterCallTable>
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
                    "CADMasterCallTable"
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

    def process(self, start, end, page, limit):
        spillman = self.data_exchange(start, end)
        data = []

        if spillman is None:
            return

        elif isinstance(spillman, dict):
            try:
                callid = spillman.get("RecordNumber")
            except:
                callid = ""

            try:
                nature = spillman.get("CallNature")
            except:
                nature = ""

            try:
                address = spillman.get("RespondToAddress")
                address = address.replace('"', "")
                address = address.replace("'", "")
                address = address.replace(";", "")
            except:
                address = ""

            try:
                city = spillman.get("CityCode")
            except:
                city = ""

            try:
                occurred_dt1 = spillman.get("TimeDateOccurredEarliest")
                occurred_dt1 = f"{occurred_dt1[15:19]}-{occurred_dt1[9:11]}-{occurred_dt1[12:14]} {occurred_dt1[0:8]}"
            except:
                occurred_dt1 = "1900-01-01 00:00:00"

            try:
                occurred_dt2 = spillman.get("TimeDateOccuredLatest")
                occurred_dt2 = f"{occurred_dt2[15:19]}-{occurred_dt2[9:11]}-{occurred_dt2[12:14]} {occurred_dt2[0:8]}"
            except:
                occurred_dt2 = "1900-01-01 00:00:00"

            try:
                reported_dt = spillman.get("TimeDateReported")
                reported_dt = f"{reported_dt[15:19]}-{reported_dt[9:11]}-{reported_dt[12:14]} {reported_dt[0:8]}"
            except:
                reported_dt = "1900-01-01 00:00:00"

            try:
                howrc = spillman.get("HowReceived")
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
                    "nature": nature,
                    "address": address,
                    "city": city,
                    "received_type": how_received,
                    "occurred_dt1": occurred_dt1,
                    "occurred_dt2": occurred_dt2,
                    "reported": reported_dt,
                }
            )

        else:
            for row in spillman:
                try:
                    callid = row["RecordNumber"]
                except:
                    callid = ""

                try:
                    nature = row["CallNature"]
                except:
                    nature = ""

                try:
                    address = row["RespondToAddress"]
                    address = address.replace('"', "")
                    address = address.replace("'", "")
                    address = address.replace(";", "")
                except:
                    address = ""

                try:
                    city = row["CityCode"]
                except:
                    city = ""

                try:
                    occurred_dt1 = row["TimeDateOccurredEarliest"]
                    occurred_dt1 = f"{occurred_dt1[15:19]}-{occurred_dt1[9:11]}-{occurred_dt1[12:14]} {occurred_dt1[0:8]}"
                except:
                    occurred_dt1 = "1900-01-01 00:00:00"

                try:
                    occurred_dt2 = row["TimeDateOccuredLatest"]
                    occurred_dt2 = f"{occurred_dt2[15:19]}-{occurred_dt2[9:11]}-{occurred_dt2[12:14]} {occurred_dt2[0:8]}"
                except:
                    occurred_dt2 = "1900-01-01 00:00:00"

                try:
                    reported_dt = row["TimeDateReported"]
                    reported_dt = f"{reported_dt[15:19]}-{reported_dt[9:11]}-{reported_dt[12:14]} {reported_dt[0:8]}"
                except:
                    reported_dt = "1900-01-01 00:00:00"

                try:
                    howrc = row["HowReceived"]
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
                        "nature": nature,
                        "address": address,
                        "city": city,
                        "received_type": how_received,
                        "occurred_dt1": occurred_dt1,
                        "occurred_dt2": occurred_dt2,
                        "reported": reported_dt,
                    }
                )

        data = sorted(data, key=lambda x: x.get("reported_dt", ""), reverse=True)

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        return paginated_data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)
        page = args.get("page", default=1, type=int)
        limit = args.get("limit", default=10, type=int)

        if token == "":
            s.AuthService.audit_request(
                "Missing", request.access_route[0], "AUTH", f"ACCESS DENIED"
            )
            abort(403, description="Missing or invalid security token.")

        auth = s.AuthService.validate_token(token, request.access_route[0])
        if auth is True:
            pass
        else:
            abort(401, description="Invalid or disabled security token provided.")

        if start == "":
            start = datetime.today().strftime("%Y-%m-%d")

        if end == "":
            end = datetime.today().strftime("%Y-%m-%d")

        s.AuthService.audit_request(
            token, request.access_route[0], "calls", json.dumps([args])
        )

        return self.process(start, end, page, limit)
