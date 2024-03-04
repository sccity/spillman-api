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

err = SetupLogger("rec_log", "rec_log")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class RecLog(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]

    @cached(TTLCache(maxsize=500, ttl=600))
    def data_exchange(self, cad_call_id):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <cdreclst>
                        <callid search_type="equal_to">{cad_call_id}</callid>
                    </cdreclst>
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
                    "cdreclst"
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

    def process(self, cad_call_id):
        spillman = self.data_exchange(cad_call_id)
        data = []

        if spillman is None:
            return

        elif isinstance(spillman, dict):
            try:
                callid = spillman.get("callid")
            except Exception:
                callid = ""

            try:
                recnum = spillman.get("recnum")
            except Exception:
                recnum = ""

            try:
                unit = spillman.get("unit")
            except Exception:
                unit = ""

            try:
                desc = spillman.get("desc")
            except Exception:
                desc = ""

            try:
                funtcn = spillman.get("funtcn")
            except Exception:
                funtcn = ""

            try:
                recom = spillman.get("recom")
            except Exception:
                recom = ""

            try:
                select = spillman.get("select")
            except Exception:
                select = ""

            try:
                disptch = spillman.get("disptch")
            except Exception:
                disptch = ""

            if recom == "Y":
                recom = "Yes"
            elif recom == "N":
                recom = "No"
            else:
                recom = "ERR"

            if select == "Y":
                select = "Yes"
            elif select == "N":
                select = "No"
            else:
                select = "ERR"

            if disptch == "Y":
                disptch = "Yes"
            elif disptch == "N":
                disptch = "No"
            else:
                disptch = "ERR"

            data.append(
                {
                    "call_id": callid,
                    "plan_id": recnum,
                    "unit": unit,
                    "function": funtcn,
                    "recommended": recom,
                    "selected": select,
                    "dispatched": disptch,
                    "description": desc,
                }
            )

        else:
            for row in spillman:
                try:
                    callid = row["callid"]

                    try:
                        recnum = row["recnum"]
                    except Exception:
                        recnum = ""

                    try:
                        unit = row["unit"]
                    except Exception:
                        unit = ""

                    try:
                        funtcn = row["funtcn"]
                    except Exception:
                        funtcn = ""

                    try:
                        recom = row["recom"]
                    except Exception:
                        recom = ""

                    try:
                        select = row["select"]
                    except Exception:
                        select = ""

                    try:
                        disptch = row["disptch"]
                    except Exception:
                        disptch = ""

                    try:
                        desc = row["desc"]
                    except Exception:
                        desc = ""

                    if recom == "Y":
                        recom = "Yes"
                    elif recom == "N":
                        recom = "No"
                    else:
                        recom = "ERR"

                    if select == "Y":
                        select = "Yes"
                    elif select == "N":
                        select = "No"
                    else:
                        select = "ERR"

                    if disptch == "Y":
                        disptch = "Yes"
                    elif disptch == "N":
                        disptch = "No"
                    else:
                        disptch = "ERR"

                except Exception:
                    continue

                data.append(
                    {
                        "call_id": callid,
                        "plan_id": recnum,
                        "unit": unit,
                        "function": funtcn,
                        "recommended": recom,
                        "selected": select,
                        "dispatched": disptch,
                        "description": desc,
                    }
                )

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        cad_call_id = args.get("callid", default="*", type=str)

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
            token, request.access_route[0], "reclog", json.dumps([args])
        )

        return self.process(cad_call_id)
