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
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger
from .settings import settings_data

sycad = setup_logger("sycad", "sycad")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class sycad(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def dataexchange(self, agency, status, ctype, city):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <sycad>
                        <agency search_type="equal_to">{agency}</agency>
                        <stat search_type="equal_to">{status}</stat>
                        <type search_type="equal_to">{ctype}</type>
                        <rtcity search_type="equal_to">{city}</rtcity>
                    </sycad>
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
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["sycad"]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    sycad.error(traceback.format_exc())
                    return

        except Exception as e:
            sycad.error(traceback.format_exc())
            return

        return data
      
    def process(self, agency, status, ctype, city):
        spillman = self.dataexchange(agency, status, ctype, city)
        data = []
        
        if type(spillman) == dict:
            try:
                callid = spillman.get("callid")
                    
                try:
                    recid = spillman.get("recid")
                except:
                    recid = "" 
                  
                agency_id = spillman.get("agency")
                
                try:
                    zone = spillman.get("zone")
                except:
                    zone = ""
                    
                try:
                    unit = spillman.get("unit")
                except:
                    unit = ""
                    
                address = spillman.get("rtaddr")
                address = address.split(";", 1)[0]
                gps_x = f"{xpos[:4]}.{xpos[4:]}"
                gps_y = f"{ypos[:2]}.{ypos[2:]}"
                reported = spillman.get("reprtd")
                sql_date = f"{reported[15:19]}-{reported[9:11]}-{reported[12:14]} {reported[0:8]}"
                
                if spillman.get("type") == "l":
                    call_type = "Law"
                elif spillman.get("type") == "f":
                    call_type = "Fire"
                elif spillman.get("type") == "e":
                    call_type = "EMS"
                else:
                    call_type = "Other"
                    
                  
                try:
                    status = spillman.get("stat")
                except:
                    status = ""
    
                try:
                    nature = spillman.get("nature")
                except:
                    nature = ""
                    
                try:
                    city = spillman.get("rtcity")
                except:
                    city = ""
                        
            except:
                sycad.error(traceback.format_exc())
                return
              
                data.append({
                    "call_id": callid,
                    "incident_id": recid,
                    "agency": agency_id,
                    "nature": nature,
                    "zone": zone,
                    "responsible_unit": unit,
                    "address": address,
                    "city": city,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "date:": sql_date,
                    "type": call_type
                })
              
            return data

        else:
            for row in spillman:
                try:
                    callid = row["callid"]
                    
                    try:
                        recid = row["recid"]
                    except:
                        recid = "" 
                      
                    agency_id = row["agency"]
                    
                    try:
                        zone = row["zone"]
                    except:
                        zone = ""
                        
                    try:
                        unit = row["unit"]
                    except:
                        unit = ""
                        
                    address = row["rtaddr"]
                    address = address.split(";", 1)[0]
                    gps_x = f"{row['xpos'][:4]}.{row['xpos'][4:]}"
                    gps_y = f"{row['ypos'][:2]}.{row['ypos'][2:]}"
                    reported = row["reprtd"]
                    sql_date = f"{reported[15:19]}-{reported[9:11]}-{reported[12:14]} {reported[0:8]}"
                    
                    if row["type"] == "l":
                        call_type = "Law"
                    elif row["type"] == "f":
                        call_type = "Fire"
                    elif row["type"] == "e":
                        call_type = "EMS"
                    else:
                        call_type = "Other"
                        
                      
                    try:
                        status = row["stat"]
                    except:
                        status = ""
     
                    try:
                        nature = row["nature"]
                    except:
                        nature = ""
                        
                    try:
                        city = row["rtcity"]
                    except:
                        city = ""

                except Exception as e:
                    sycad.error(traceback.format_exc())
                    continue
                  
                data.append({
                    "call_id": callid,
                    "incident_id": recid,
                    "agency": agency_id,
                    "nature": nature,
                    "zone": zone,
                    "responsible_unit": unit,
                    "address": address,
                    "city": city,
                    "latitude": gps_y,
                    "longitude": gps_x,
                    "type": call_type,
                    "status": status,
                    "date:": sql_date
                })
                
        return data
                  
    def get(self):
        args = request.args
        agency = args.get("agency", default="*", type=str)
        status = args.get("status", default="*", type=str)
        ctype = args.get("type", default="*", type=str)
        city = args.get("city", default="*", type=str)
        
        return self.process(agency, status, ctype, city)
