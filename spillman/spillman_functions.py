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
import sys, json, logging, xmltodict, traceback, collections
import requests
import spillman as s
import urllib.request as urlreq
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import SetupLogger
from .settings import settings_data
from .database import db
from cachetools import cached, TTLCache

err = SetupLogger("functions", "functions")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SpillmanFunctions(Resource):
    unit_name_cache = TTLCache(maxsize=2500, ttl=3600)
    unit_contact_cache = TTLCache(maxsize=2500, ttl=3600)

    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_user = settings_data["spillman"]["user"]
        self.api_password = settings_data["spillman"]["password"]

    def validate_string(self, string):
        try:
            data = string
        except:
            data = ""
        return data

    def validate_date(self, string):
        try:
            data = f"{string[6:10]}-{string[0:2]}-{string[3:5]}"
        except:
            data = "1900-01-01"
        return data
      
    def validate_datetime(self, string):
        try:
            data = f"{string[15:19]}-{string[9:11]}-{string[12:14]} {string[0:8]}"
        except:
            data = "1900-01-01 00:00:00"
        return data

    def validate_phone(self, string):
        try:
            string = string.replace("(", "")
            string = string.replace(")", "")
            string = string.replace("-", "")
            data = string
        except:
            data = ""
        return data
          
    def validate_number(self, string):
        try:
            data = string
        except:
            data = 0
        return data

    @cached(unit_name_cache)
    def get_unit_name(self, unit_id):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <PatrolUnitOfficerDetail>
                        <UnitNumber search_type="equal_to">{unit_id}</UnitNumber>
                        <SequenceNumber search_type="equal_to">1</SequenceNumber>
                    </PatrolUnitOfficerDetail>
                    <Columns>
                      <ColumnName>OfficerName</ColumnName>
                    </Columns>
                    <RowCount>1</RowCount>
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
                    "PatrolUnitOfficerDetail"
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

        return data["OfficerName"]
      
    @cached(unit_contact_cache)
    def get_unit_contact(self, unit_id):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <cdunit>
                        <unitno search_type="equal_to">{unit_id}</unitno>
                    </cdunit>
                    <Columns>
                      <ColumnName>contact</ColumnName>
                    </Columns>
                    <RowCount>1</RowCount>
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
                    "cdunit"
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

        return data["contact"]

    def get_alert_name(self, alert_cd):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <TableOfAlertCodes>
                        <CodeForDangerousAttribute search_type="equal_to">{alert_cd}</CodeForDangerousAttribute>
                    </TableOfAlertCodes>
                    <Columns>
                      <ColumnName>DescriptionOfAttribute</ColumnName>
                    </Columns>
                    <RowCount>1</RowCount>
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
                    "TableOfAlertCodes"
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

        return data["DescriptionOfAttribute"]

    def name_alert_codes(self, name_id):
        session = requests.Session()
        session.auth = (self.api_user, self.api_password)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <AlertCodesForNames>
                        <NameNumber search_type="equal_to">{name_id}</NameNumber>
                    </AlertCodesForNames>
                    <Columns>
                      <ColumnName>AlertCodeForAboveName</ColumnName>
                    </Columns>
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
                    "AlertCodesForNames"
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

        if isinstance(data, dict):
            return [data.get("AlertCodeForAboveName")]

        elif isinstance(data, list):
            return [item.get("AlertCodeForAboveName") for item in data]
