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
import json, logging, xmltodict, traceback, collections, requests, re
import spillman as s
from flask_restful import Resource, Api, request
from flask import jsonify, abort
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data

err = setup_logger("emd", "emd")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class emd(Resource):
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
                    <CADMasterCallCommentsTable>
                        <LongTermCallID search_type="equal_to">{cadcallid}</LongTermCallID>
                    </CADMasterCallCommentsTable>
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
                    "CADMasterCallCommentsTable"
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

    def process(self, cadcallid):
        spillman = self.dataexchange(cadcallid)
        data = []

        if spillman is None:
            return

        try:
            callid = spillman.get("LongTermCallID")
        except:
            callid = ""

        try:
            comment = spillman.get("CallTakerComments")
        except:
            comment = ""
            
        comment = comment.replace('"', "")
        comment = comment.replace("'", "")
        comment = comment.replace(":", "")
    
        try:
            proqa_str = str(
                re.findall("ProQA Code [0-9]+[0-9]+[A-Za-z]+[0-9]+[0-9]+", comment)[
                    -1
                ]
            )
            emd_full = proqa_str[11:16]
            response_cd = proqa_str[13:14]

        except Exception as e:
            error = format(str(e))

            if error.find("'NoneType'") != -1:
                response_cd = "Z"

            elif error.find("'list index out of range'") != -1:
                proqa_sr = str(
                    re.search(
                        "ProQA Code [0-9]+[0-9]+[A-Za-z]+[0-9]+[0-9]+", cad_comment
                    ).group()
                )
                emd_full = proqa_sr[11:16]
                response_cd = proqa_str[13:14]

            else:
                emd_full = "Z"
                response_cd = "Z"
                
        if response_cd == "A":
            response = "Alpha"
        elif response_cd == "B":
            response = "Bravo"
        elif response_cd == "C":
            response = "Charlie"
        elif response_cd == "D":
            response = "Delta"
        elif response_cd == "E":
            response = "Echo"
        else:
            response = "Zulu"
            
        data.append({"call_id": callid, "emd": emd_full, "response": response})

        return data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        cadcallid = args.get("callid", default="", type=str)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", "ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        if cadcallid == "":
            return jsonify(error="Missing callid argument.")

        s.auth.audit(
            token,
            request.access_route[0],
            "EMD",
            f"CALLID: {cadcallid}",
        )

        return self.process(cadcallid)
