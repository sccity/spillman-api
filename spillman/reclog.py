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

err = setup_logger("reclog", "reclog")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class reclog(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]

    def dataexchange(self, cadcallid):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <cdreclst>
                        <callid search_type="equal_to">{cadcallid}</callid>
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
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["cdreclst"]

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

    def process(self,cadcallid):
        spillman = self.dataexchange(cadcallid)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                callid = spillman.get("callid")
            except:
                callid = ""

            try:
                recnum = spillman.get("recnum")
            except:
                recnum = ""

            try:
                unit = spillman.get("unit")
            except:
                unit = ""

            try:
                desc = spillman.get("desc")
            except:
                desc = ""

            try:
                funtcn = spillman.get("funtcn")
            except:
                funtcn = ""

            try:
                recom = spillman.get("recom")
            except:
                recom = ""

            try:
                select = spillman.get("select")
            except:
                select = ""

            try:
                disptch = spillman.get("disptch")
            except:
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
                    except:
                        recnum = ""

                    try:
                        unit = row["unit"]
                    except:
                        unit = ""
                        
                    try:
                        funtcn = row["funtcn"]
                    except:
                        funtcn = ""
                        
                    try:
                        recom = row["recom"]
                    except:
                        recom = ""
                        
                    try:
                        select = row["select"]
                    except:
                        select = ""
                        
                    try:
                        disptch = row["disptch"]
                    except:
                        disptch = ""
                        
                    try:
                        desc = row["desc"]
                    except:
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

                except:
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
        cadcallid = args.get("callid", default="*", type=str)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", "ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        s.auth.audit(token, request.access_route[0], "reclog", json.dumps([args]))

        return self.process(cadcallid)
