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
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data
from .database import db

err = setup_logger("rlmain", "rlmain")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class rlmain(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def dataexchange(self, agency, unit, start, end):
        start_date = date(int(start[0:4]), int(start[5:7]), int(start[8:10])) - timedelta(days=1)
        start_date = str(start_date.strftime("%m/%d/%Y"))
        end_date = date(int(end[0:4]), int(end[5:7]), int(end[8:10])) + timedelta(days=1)
        end_date = str(end_date.strftime("%m/%d/%Y"))
        
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <rlmain>
                        <agency search_type="equal_to">{agency}</agency>
                        <unit search_type="equal_to">{unit}</unit>
                        <logdate search_type="greater_than">23:59:59 {start_date}</logdate>
                        <logdate search_type="less_than">00:00:00 {end_date}</logdate>
                    </rlmain>
                </Query>
            </PublicSafety>
        </PublicSafetyEnvelope>
         """

        try:
            headers = {"Content-Type": "application/xml"}
            try:
                xml = session.post(self.api_url, data=request, headers=headers, verify=False)
                decoded = xml.content.decode('utf-8')
                data = json.loads(json.dumps(xmltodict.parse(decoded)))
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["rlmain"]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return
            

        except Exception as e:
            error = format(str(e))
            print(error)

            if error.find("'NoneType'") != -1:
                return

            else:
                err.error(traceback.format_exc())
                return

        return data
      
    def process(self, agency, unit, start, end):
        spillman = self.dataexchange(agency, unit, start, end)
        data = []
        
        if spillman is None:
            return
        
        elif type(spillman) == dict:
            try:
                date = spillman.get("logdate")
                logdate = f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
            except:
                logdate = "1900-01-01 00:00:00"
            
            try:    
                gps_x = f"{row['xpos'][:4]}.{row['xpos'][4:]}"
            except:
                gps_x = 0
                
            try:    
                gps_y = f"{row['ypos'][:2]}.{row['ypos'][2:]}"
            except:
                gps_y = 0
            
            try:
                callid = spillman.get("callid")
            except:
                callid = ""  
            
            try:
                agency = spillman.get("agency")
            except:
                agency = ""  
            
            try:
                zone = spillman.get("zone")
            except:
                zone = ""  
            
            try:
                tencode = spillman.get("tencode")
            except KeyError:
                tencode = ""  
            
            try:
                unit = spillman.get("unit")
            except:
                unit = ""      
            
            try:
                description = spillman.get("desc")
                description = description.replace('"', '')
                description = description.replace("'", "")
            except:
                description = ""
                
            try:
                calltype = spillman.get("calltyp")
            except:
                calltype = ""
              
            data.append({
                "call_id": callid,
                "agency": agency,
                "unit": unit,
                "status": tencode,
                "zone": zone,
                "latitude": gps_y,
                "longitude": gps_x,
                "description": description,
                "date": logdate
            })

        else:
            for row in spillman:
                try:
                    date = row["logdate"]
                    logdate = f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
                except:
                    logdate = "1900-01-01 00:00:00"
                
                try:    
                    gps_x = f"{row['xpos'][:4]}.{row['xpos'][4:]}"
                except:
                    gps_x = 0
                    
                try:    
                    gps_y = f"{row['ypos'][:2]}.{row['ypos'][2:]}"
                except:
                    gps_y = 0
                
                try:
                    callid = row["callid"]
                except:
                    callid = ""  
                
                try:
                    agency = row["agency"]
                except:
                    agency = ""  
                
                try:
                    zone = row["zone"]
                except:
                    zone = ""  
                
                try:
                    tencode = row["tencode"]
                except KeyError:
                    tencode = ""  
                
                try:
                    unit = row["unit"]
                except:
                    unit = ""      
                
                try:
                    description = row["desc"]
                    description = description.replace('"', '')
                    description = description.replace("'", "")
                except:
                    description = ""
                    
                try:
                    calltype = row["calltyp"]
                except:
                    calltype = ""
                  
                data.append({
                    "call_id": callid,
                    "agency": agency,
                    "unit": unit,
                    "status": tencode,
                    "zone": zone,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "description": description,
                    "date": logdate
                })
                
        return data
                  
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        agency = args.get("agency", default="*", type=str)
        unit = args.get("unit", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)
        
        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", f"ACCESS DENIED")
            return jsonify(error="No security token provided.")
        
        auth = s.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)
        
        if start == "":
            start = datetime.today().strftime('%Y-%m-%d')
          
        if end == "":
            end = datetime.today().strftime('%Y-%m-%d')
          
        s.auth.audit(token, request.access_route[0], "RLMAIN", f"UNIT: {unit} AGENCY: {agency} START DATE: {start} END DATE: {end}")
        
        return self.process(agency, unit, start, end)
