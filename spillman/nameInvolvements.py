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
import threading
import spillman as s
import urllib.request as urlreq
from flask_restful import Resource, Api, request
from flask import jsonify, abort
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data
from .database import db

err = setup_logger("nameInvolvements", "nameInvolvements")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class nameInvolvements(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]

    def dataexchange(self, name_id):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <TableOfInvolvements>
                        <TypeOfThisRecord search_type="greater_than">999</TypeOfThisRecord>
                        <TypeOfThisRecord search_type="less_than">1201</TypeOfThisRecord>
                        <RtypeRelatedRecordsType search_type="equal_to">900</RtypeRelatedRecordsType>
                        <RelIDRelatedRecordsID search_type="equal_to">{name_id}</RelIDRelatedRecordsID>
                    </TableOfInvolvements>
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
                    "TableOfInvolvements"
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
      
    def getNature(self, incident_id, table_name):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <From>Spillman API - XML to JSON</From>
            <PublicSafety id="">
                <Query>
                    <{table_name}>
                        <number search_type="equal_to">{incident_id}</number>
                    </{table_name}>
                    <Columns>
                      <ColumnName>nature</ColumnName>
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
                    f"{table_name}"
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
          
        return data['nature']

    def process_row(self, name_id, row, data):
        try:
            incident_id = row["RecIDThisRecordsIDNo"]
        except:
            incident_id = ""
    
        try:
            involvement_type = row["RelationshipToOtherRecord"]
        except:
            involvement_type = ""
            
        try:
            record_type = row["TypeOfThisRecord"]
        except:
            record_type = ""
    
        if record_type == "1000":
            incident_type = "Fire"
            nature = self.getNature(incident_id,"frmain")
        elif record_type == "1100":
            incident_type = "EMS"
            nature = self.getNature(incident_id,"emmain")
        elif record_type == "1200":
            incident_type = "Law"
            nature = self.getNature(incident_id,"lwmain")
        else:
            incident_type = "Other"
            nature = "Other"
    
        try:
            involvement_date = row["DateInvolvementOccurred"]
            involvement_date = f"{involvement_date[6:10]}-{involvement_date[0:2]}-{involvement_date[3:5]} 00:00:00"
        except:
            involvement_date = "1900-01-01 00:00:00"
    
        data.append(
            {
                "name_id": name_id,
                "incident_id": incident_id,
                "nature": nature,
                "involvement_type": involvement_type,
                "incident_type": incident_type,
                "involvement_date": involvement_date,
            }
        )

    def process(self, name_id, page, limit):
        spillman = self.dataexchange(name_id)
        data = []

        if spillman is None:
            return

        elif type(spillman) == dict:
            try:
                incident_id = spillman.get("RecIDThisRecordsIDNo")
            except:
                incident_id = ""

            try:
                involvement_type = spillman.get("RelationshipToOtherRecord")
            except:
                involvement_type = ""
                
            try:
                record_type = spillman.get("TypeOfThisRecord")
            except:
                record_type = ""

            if record_type == "1000":
                incident_type = "Fire"
                nature = self.getNature(incident_id,"frmain")
            elif record_type == "1100":
                incident_type = "EMS"
                nature = self.getNature(incident_id,"emmain")
            elif record_type == "1200":
                incident_type = "Law"
                nature = self.getNature(incident_id,"lwmain")
            else:
                incident_type = "Other"
                nature = "Other"
                
            try:
                involvement_date = row["DateInvolvementOccurred"]
                involvement_date = f"{involvement_date[6:10]}-{involvement_date[0:2]}-{involvement_date[3:5]} 00:00:00"
            except:
                involvement_date = "1900-01-01 00:00:00"

            data.append(
                {
                    "name_id": name_id,
                    "incident_id": incident_id,
                    "nature": nature,
                    "involvement_type": involvement_type,
                    "incident_type": incident_type,
                    "involvement_date": involvement_date,
                }
            )

        else:
            threads = []
            for row in spillman:
                try:
                    thread = threading.Thread(target=self.process_row, args=(name_id, row, data))
                    threads.append(thread)
                    thread.start()
                except:
                    continue
                
            for thread in threads:
                    thread.join()
                    
        data = sorted(data, key=lambda x: x.get("involvement_date", ""), reverse=True)
                
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        return paginated_data

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        app = args.get("app", default="*", type=str)
        uid = args.get("uid", default="*", type=str)
        name_id = args.get("name_id", default="", type=str)
        page = args.get('page', default=1, type=int)
        limit = args.get('limit', default=10, type=int)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", f"ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        s.auth.audit(token, request.access_route[0], "nameInvolvements", json.dumps([args]))

        return self.process(name_id, page, limit)
