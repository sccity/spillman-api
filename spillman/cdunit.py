# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
from flask_restful import Resource, Api, reqparse
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
        
    def dataexchange(self):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <cdunit>
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
      
    def format(self):
        data = []
        cdunit_data = self.dataexchange()
        
        if type(cdunit_data) == dict:
            return

        else:
            for records in cdunit_data:
                try:
                    try:
                        unit = records["unitno"]
                    except:
                        unit = ""
                    
                    try:
                        desc = records["desc"]
                    except:
                        desc = "" 
                      
                    agency_id = records["agency"]
                    
                    try:
                        zone = records["zone"]
                    except:
                        zone = ""

                    if records["type"] == "l":
                        type = "Law"
                    elif records["type"] == "f":
                        type = "Fire"
                    elif records["type"] == "e":
                        type = "EMS"
                    else:
                        type = "Other"
                        
                    try:
                        kind = records["kind"]
                    except:
                        kind = ""
     
                    try:
                        station = records["station"]
                    except:
                        station = ""

                except Exception as e:
                    cdunit.error(traceback.format_exc())
                    continue
                  
                data.append({
                    "unit": unit,
                    "agency": agency_id,
                    "zone": zone,
                    "type": type,
                    "kind": kind,
                    "station": station,
                    "description": desc
                })
                
        return data
                  
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        
        auth = s.auth.check(token)
        if auth is True:
            pass
        else:
            return abort(403)
          
        return self.format()
