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
from flask_restful import Resource, Api, request
from flask import jsonify, abort
import json
import requests
import spillman as s
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from cachetools import cached, TTLCache

err = SetupLogger("active_units", "active_units")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ActiveUnits(Resource):
    @cached(TTLCache(maxsize=500, ttl=60))
    def process(self, cad_call_id):
        date = datetime.today().strftime("%Y-%m-%d")
        rlog = s.RadioLog()
        spillman = rlog.process("*", "*", cad_call_id, "*", date, date, 1, 100)

        if spillman is None:
            return []

        unique_units = set()
        result = []

        for entry in spillman:
            unit = entry["unit"]

            if unit not in unique_units:
                unique_units.add(unit)
                past_time = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                time_difference = current_time - past_time
                minutes, seconds = divmod(time_difference.seconds, 60)
                formatted_time = f"{minutes}m {seconds}s"
                entry["elapsed"] = (
                    formatted_time  # Update the elapsed time for the current entry
                )
                result.append(
                    {
                        "agency": entry["agency"],
                        "unit": unit,
                        "status": entry["status"],
                        "elapsed": formatted_time,
                    }
                )

        result = [
            entry
            for entry in result
            if entry["status"] not in ["CMPLT", "8", "ONDT", None, ""]
        ]

        return result

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        cad_call_id = args.get("callid", default="", type=str)
        
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

        return self.process(cad_call_id)
