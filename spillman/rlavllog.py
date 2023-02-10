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

rlogerr = setup_logger("rlavllog", "rlavllog")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class rlavllog(Resource):
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
                    <rlavllog>
                        <agency search_type="equal_to">{agency}</agency>
                        <assgnmt search_type="equal_to">{unit}</assgnmt>
                        <logdate search_type="greater_than">23:59:59 {start_date}</logdate>
                        <logdate search_type="less_than">00:00:00 {end_date}</logdate>
                    </rlavllog>
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
                data = data['PublicSafetyEnvelope']['PublicSafety']['Response']['rlavllog']

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    rlavllog.error(traceback.format_exc())
                    return
            
        except Exception as e:
            error = format(str(e))
            print(error)

            if error.find("'NoneType'") != -1:
                return

            else:
                rlogerr.error(traceback.format_exc())
                return

        return data
      
    def process(self, agency, unit, start, end):
        spillman = self.dataexchange(agency, unit, start, end)
        data = []
        
        if type(spillman) == dict:
            return 

        else:
            for row in spillman:
                date = row['logdate']
                logdate = f"{date[15:19]}-{date[9:11]}-{date[12:14]} {date[0:8]}"
                
                gps_x    = row['xlng']
                gps_y    = row['ylat']
                
                try:
                    agency = row['agency']
                except KeyError:
                    agency = ""  
                
                try:
                    status = row['stcode']
                except KeyError:
                    status = ""  
                
                try:
                    unit = row['assgnmt']
                except KeyError:
                    unit = ""      
                    
                try:
                    heading = row['heading']
                except KeyError:
                    heading = ""
                    
                try:
                    speed = row['speed']
                except KeyError:
                    speed = ""
                  
                data.append({
                    "agency": agency,
                    "unit": unit,
                    "status": status,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "heading": heading,
                    "speed": speed,
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
        
        auth = s.auth.check(token)
        if auth is True:
            pass
        else:
            return abort(403)
        
        if start == "":
            return jsonify(error="Missing start date argument.")
          
        if end == "":
            return jsonify(error="Missing end date argument.")
        
        return self.process(agency, unit, start, end)
