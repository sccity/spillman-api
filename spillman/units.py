# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.#
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
from flask_restful import Resource, Api, request
from flask import jsonify, abort
import sys, json, logging, xmltodict, traceback, collections
import requests, uuid
import spillman as s
import urllib.request as urlreq
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data
from .database import db

err = setup_logger("units", "units")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class units(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def dataexchange(self, unit, agency, zone, utype, kind):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <cdunit>
                        <unitno search_type="equal_to">{unit}</unitno>
                        <agency search_type="equal_to">{agency}</agency>
                        <zone search_type="equal_to">{zone}</zone>
                        <type search_type="equal_to">{utype}</type>
                        <kind search_type="equal_to">{kind}</kind>
                    </cdunit>
                </Query>
            </PublicSafety>
        </PublicSafetyEnvelope>
        """
        
        try:
            headers = {"Content-Type": "application/xml"}
            try:
                xml = session.post(self.api_url, data=request, headers=headers, verify=False)
                decoded = xml.content.decode("utf-8")
                data = json.loads(json.dumps(xmltodict.parse(decoded)))
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["cdunit"]

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
      
    def process(self, unit, agency, zone, utype, kind):
        spillman = self.dataexchange(unit, agency, zone, utype, kind)
        data = []
        
        if spillman is None:
            return
        
        elif type(spillman) == dict:
            try:
                unit = spillman.get("unitno")
            except:
                unit = ""
            
            try:
                desc = spillman.get("desc")
            except:
                desc = "" 
              
            agency = spillman.get("agency")
            
            try:
                zone = spillman.get("zone")
            except:
                zone = ""

            if spillman.get("type") == "l":
                utype = "Law"
            elif spillman.get("type") == "f":
                utype = "Fire"
            elif spillman.get("type") == "e":
                utype = "EMS"
            else:
                utype = "Other"
                
            try:
                kind = spillman.get("kind")
            except:
                kind = ""

            try:
                station = spillman.get("station")
            except:
                station = ""
              
            data.append({
                "unit": unit,
                "agency": agency,
                "zone": zone,
                "type": utype,
                "kind": kind,
                "station": station,
                "description": desc
            })

        else:
            for row in spillman:
                try:
                    try:
                        unit = row["unitno"]
                    except:
                        unit = ""
                    
                    try:
                        desc = row["desc"]
                    except:
                        desc = "" 
                      
                    agency = row["agency"]
                    
                    try:
                        zone = row["zone"]
                    except:
                        zone = ""

                    if row["type"] == "l":
                        utype = "Law"
                    elif row["type"] == "f":
                        utype = "Fire"
                    elif row["type"] == "e":
                        utype = "EMS"
                    else:
                        utype = "Other"
                        
                    try:
                        kind = row["kind"]
                    except:
                        kind = ""
     
                    try:
                        station = row["station"]
                    except:
                        station = ""

                except:
                    continue
                  
                data.append({
                    "unit": unit,
                    "agency": agency,
                    "zone": zone,
                    "type": utype,
                    "kind": kind,
                    "station": station,
                    "description": desc
                })
                
        return data
                  
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        unit = args.get("unit", default="*", type=str)
        agency = args.get("agency", default="*", type=str)
        zone = args.get("zone", default="*", type=str)
        utype = args.get("type", default="*", type=str)
        kind = args.get("kind", default="*", type=str)
        
        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", f"ACCESS DENIED")
            return jsonify(error="No security token provided.")
        
        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)
          
        s.auth.audit(token, request.access_route[0], "CDUNIT", f"UNIT: {unit} AGENCY: {agency} ZONE: {zone} TYPE: {utype} KIND: {kind}")
          
        return self.process(unit, agency, zone, utype, kind)
