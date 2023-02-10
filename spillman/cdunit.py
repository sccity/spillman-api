# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
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

cdunit = setup_logger("cdunit", "cdunit")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class cdunit(Resource):
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
                    cdunit.error(traceback.format_exc())
                    return

        except Exception as e:
            cdunit.error(traceback.format_exc())
            return

        return data
      
    def process(self, unit, agency, zone, utype, kind):
        spillman = self.dataexchange(unit, agency, zone, utype, kind)
        data = []
        
        if type(spillman) == dict:
            return

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

                except Exception as e:
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
        
        auth = s.auth.check(token)
        if auth is True:
            pass
        else:
            return abort(403)
          
        return self.process(unit, agency, zone, utype, kind)
