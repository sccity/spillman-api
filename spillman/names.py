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
import json, xmltodict, traceback
import requests
import spillman as s
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from cachetools import cached, TTLCache

err = SetupLogger("names", "names")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Names(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]
        self.f = s.SpillmanFunctions()

    @cached(TTLCache(maxsize=500, ttl=1800))
    def data_exchange(
        self, number, last, first, middle, phone, ntype, dl, dlstate, stateid, ssn
    ):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <nmmain>
                        <number search_type="equal_to">{number}</number>
                        <last search_type="equal_to">{last}</last>
                        <first search_type="equal_to">{first}</first>
                        <middle search_type="equal_to">{middle}</middle>
                        <phone search_type="equal_to">{phone}</phone>
                        <nametyp search_type="equal_to">{ntype}</nametyp>
                        <dlnum search_type="equal_to">{dl}</dlnum>
                        <dlstate search_type="equal_to">{dlstate}</dlstate>
                        <stateid search_type="equal_to">{stateid}</stateid>
                        <ssnum search_type="equal_to">{ssn}</ssnum>
                    </nmmain>
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
                    "nmmain"
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

    def process_alerts(self, name_id):
        try:
            f = s.SpillmanFunctions()
            alert_list = f.name_alert_codes(name_id)
            alert_names = [f.get_alert_name(alert) for alert in alert_list]
            result = ", ".join(alert_names)
            return result
        except:
            return "NONE"

    def process(
        self,
        number,
        last,
        first,
        middle,
        phone,
        ntype,
        dl,
        dlstate,
        stateid,
        ssn,
        page,
        limit,
    ):
        spillman = self.data_exchange(
            number, last, first, middle, phone, ntype, dl, dlstate, stateid, ssn
        )
        data = []

        if spillman is None:
            return

        elif isinstance(spillman, dict):
            name_id = self.f.validate_string(spillman.get("number"))
            name_type = self.f.validate_string(spillman.get("nametyp"))
            ssn = self.f.validate_string(spillman.get("ssnum"))
            license_num = self.f.validate_string(spillman.get("dlnum"))
            license_state = self.f.validate_string(spillman.get("dlstate"))
            state_id = self.f.validate_string(spillman.get("stateid"))
            first_name = self.f.validate_string(spillman.get("first"))
            last_name = self.f.validate_string(spillman.get("last"))
            middle_name = self.f.validate_string(spillman.get("middle"))
            suffix = self.f.validate_string(spillman.get("suffix"))
            alias = self.f.validate_string(spillman.get("aka"))
            birth_day = self.f.validate_date(spillman.get("birthd"))
            height = self.f.validate_string(spillman.get("height"))
            height = height.replace("'", "ft ")
            height = height.replace('"', "in")
            weight = self.f.validate_string(spillman.get("weight"))
            sex = self.f.validate_string(spillman.get("sex"))
            gender = self.f.validate_string(spillman.get("gender"))
            race = self.f.validate_string(spillman.get("race"))
            ethnic = self.f.validate_string(spillman.get("ethnic"))
            hair = self.f.validate_string(spillman.get("hair"))
            hairstyle = self.f.validate_string(spillman.get("hairsty"))
            eyes = self.f.validate_string(spillman.get("eyes"))
            glasses = self.f.validate_string(spillman.get("glasses"))
            build = self.f.validate_string(spillman.get("build"))
            complexion = self.f.validate_string(spillman.get("cmplx"))
            facial = self.f.validate_string(spillman.get("facial"))
            speech = self.f.validate_string(spillman.get("speech"))
            address = self.f.validate_string(spillman.get("street"))
            address = address.replace('"', "")
            address = address.replace("'", "")
            address = address.replace(";", "")
            city = self.f.validate_string(spillman.get("city"))
            state = self.f.validate_string(spillman.get("state"))
            zipcode = self.f.validate_string(spillman.get("zip"))
            primary_phone = self.f.validate_phone(spillman.get("phone"))
            work_phone = self.f.validate_phone(spillman.get("wrkphn"))
            alerts = self.process_alerts(name_id)

            data.append(
                {
                    "name_id": name_id,
                    "name_type": name_type,
                    "ssn": ssn,
                    "license_num": license_num,
                    "license_state": license_state,
                    "state_id": state_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "middle_name": middle_name,
                    "suffix": suffix,
                    "alias": alias,
                    "birth_date": birth_day,
                    "height": height,
                    "weight": weight,
                    "sex": sex,
                    "gender": gender,
                    "race": race,
                    "ethnicity": ethnic,
                    "hair_color": hair,
                    "hair_style": hairstyle,
                    "eye_color": eyes,
                    "glasses": glasses,
                    "build": build,
                    "complexion": complexion,
                    "facial_hair": facial,
                    "speech_style": speech,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zipcode,
                    "primary_phone": primary_phone,
                    "work_phone": work_phone,
                    "alerts": alerts,
                }
            )

        else:
            for row in spillman:
                try:
                    name_id = self.f.validate_string(row.get("number", ""))
                    name_type = self.f.validate_string(row.get("nametyp", ""))
                    ssn = self.f.validate_string(row.get("ssnum", ""))
                    license_num = self.f.validate_string(row.get("dlnum", ""))
                    license_state = self.f.validate_string(row.get("dlstate", ""))
                    state_id = self.f.validate_string(row.get("stateid", ""))
                    first_name = self.f.validate_string(row.get("first", ""))
                    last_name = self.f.validate_string(row.get("last", ""))
                    middle_name = self.f.validate_string(row.get("middle", ""))
                    suffix = self.f.validate_string(row.get("suffix", ""))
                    alias = self.f.validate_string(row.get("aka", ""))
                    birth_day = self.f.validate_date(row.get("birthd", ""))
                    height = self.f.validate_string(row.get("height", ""))
                    height = height.replace("'", "ft ")
                    height = height.replace('"', "in")
                    weight = self.f.validate_string(row.get("weight", ""))
                    sex = self.f.validate_string(row.get("sex", ""))
                    gender = self.f.validate_string(row.get("gender", ""))
                    race = self.f.validate_string(row.get("race", ""))
                    ethnic = self.f.validate_string(row.get("ethnic", ""))
                    hair = self.f.validate_string(row.get("hair", ""))
                    hairstyle = self.f.validate_string(row.get("hairsty", ""))
                    eyes = self.f.validate_string(row.get("eyes", ""))
                    glasses = self.f.validate_string(row.get("glasses", ""))
                    build = self.f.validate_string(row.get("build", ""))
                    complexion = self.f.validate_string(row.get("cmplx", ""))
                    facial = self.f.validate_string(row.get("facial", ""))
                    speech = self.f.validate_string(row.get("speech", ""))
                    address = self.f.validate_string(row.get("street", ""))
                    address = address.replace('"', "")
                    address = address.replace("'", "")
                    address = address.replace(";", "")
                    city = self.f.validate_string(row.get("city", ""))
                    state = self.f.validate_string(row.get("state", ""))
                    zipcode = self.f.validate_string(row.get("zip", ""))
                    primary_phone = self.f.validate_phone(row.get("phone", ""))
                    work_phone = self.f.validate_phone(row.get("wrkphn", ""))
                    alerts = self.process_alerts(name_id)

                except:
                    continue

                data.append(
                    {
                        "name_id": name_id,
                        "name_type": name_type,
                        "ssn": ssn,
                        "license_num": license_num,
                        "license_state": license_state,
                        "state_id": state_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "middle_name": middle_name,
                        "suffix": suffix,
                        "alias": alias,
                        "birth_date": birth_day,
                        "height": height,
                        "weight": weight,
                        "sex": sex,
                        "gender": gender,
                        "race": race,
                        "ethnicity": ethnic,
                        "hair_color": hair,
                        "hair_style": hairstyle,
                        "eye_color": eyes,
                        "glasses": glasses,
                        "build": build,
                        "complexion": complexion,
                        "facial_hair": facial,
                        "speech_style": speech,
                        "address": address,
                        "city": city,
                        "state": state,
                        "zip": zipcode,
                        "primary_phone": primary_phone,
                        "work_phone": work_phone,
                        "alerts": alerts,
                    }
                )

        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        return paginated_data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        number = args.get("num", default="*", type=str)
        last = args.get("last", default="*", type=str)
        first = args.get("first", default="*", type=str)
        middle = args.get("middle", default="*", type=str)
        phone = args.get("phone", default="*", type=str)
        ntype = args.get("type", default="*", type=str)
        dl = args.get("dl", default="*", type=str)
        dlstate = args.get("dlstate", default="*", type=str)
        stateid = args.get("stateid", default="*", type=str)
        ssn = args.get("ssn", default="*", type=str)
        page = args.get("page", default=1, type=int)
        limit = args.get("limit", default=10, type=int)
        
        if (app == "" or app == "*"):
            app = "default"
        
        if (uid == "" or uid == "*"):
            uid = "default"

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

        if ssn == "*":
            ssn = "*"
        else:
            ssn = f"{ssn[0:3]}-{ssn[3:5]}-{ssn[5:10]}"

        s.AuthService.audit_request(
            token, request.access_route[0], "names", json.dumps([args])
        )

        return self.process(
            number,
            last,
            first,
            middle,
            phone,
            ntype,
            dl,
            dlstate,
            stateid,
            ssn,
            page,
            limit,
        )
