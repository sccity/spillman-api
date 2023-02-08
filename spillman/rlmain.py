# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
from flask_restful import Resource, Api, request
import sys, json, logging, xmltodict, traceback, collections
import requests, uuid
import spillman as s
import urllib.request as urlreq
from datetime import date, timedelta
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data

rlogerr = setup_logger("rlmain", "rlmain")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class rlmain(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def radiolog(self, agency, unit, start, end):
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
                        <logdate search_type="greater_than">00:00:00 {start_date}</logdate>
                        <logdate search_type="less_than">23:59:59 {end_date}</logdate>
                    </rlmain>
                </Query>
            </PublicSafety>
        </PublicSafetyEnvelope>
         """

        try:
            headers = {"Content-Type": "application/xml"}
            try:
                rlog_xml = session.post(self.api_url, data=request, headers=headers, verify=False)
                rlog_decoded = rlog_xml.content.decode('utf-8')
                rlog = json.loads(json.dumps(xmltodict.parse(rlog_decoded)))
                rlog = rlog['PublicSafetyEnvelope']['PublicSafety']['Response']['rlmain']

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    frmain.error(traceback.format_exc())
                    return
            

        except Exception as e:
            error = format(str(e))
            print(error)

            if error.find("'NoneType'") != -1:
                return

            else:
                rlogerr.error(traceback.format_exc())
                return

        return rlog
      
    def format(self, agency, unit, start, end):
        rlog = self.radiolog(agency, unit, start, end)
        data = []
        if type(rlog) == dict:
            return 

        else:
            for results in rlog:
                date = results['logdate']
                logdate = f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
                gps_x    = f"{results['xpos'][:4]}.{results['xpos'][4:]}"
                gps_y    = f"{results['ypos'][:2]}.{results['ypos'][2:]}"
                
                try:
                    callid = results['callid']
                except KeyError:
                    callid = ""  
                
                try:
                    agency = results['agency']
                except KeyError:
                    agency = ""  
                
                try:
                    zone = results['zone']
                except KeyError:
                    zone = ""  
                
                try:
                    tencode = results['tencode']
                except KeyError:
                    tencode = ""  
                
                try:
                    unit = results['unit']
                except KeyError:
                    unit = ""      
                
                try:
                    description = results['desc']
                    description = description.replace('"', '')
                    description = description.replace("'", "")
                except KeyError:
                    description = ""
                    
                try:
                    calltype = results['calltyp']
                except KeyError:
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
        agency = args.get("agency", default="*", type=str)
        unit = args.get("unit", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)
        
        return self.format(agency, unit, start, end)
