# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
from flask_restful import Resource, Api, reqparse
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
        
    def active(self):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <sycad>
                    </sycad>
                </Query>
            </PublicSafety>
        </PublicSafetyEnvelope>
        """
        
        try:
            headers = {"Content-Type": "application/xml"}
            try:
                calls_xml = session.post(
                    self.api_url, data=request, headers=headers, verify=False
                )
                calls_decoded = calls_xml.content.decode("utf-8")
                calls = json.loads(json.dumps(xmltodict.parse(calls_decoded)))
                calls = calls["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["sycad"]

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

        return calls
      
    def format(self):
        calls = self.active()
        data = []
        if type(calls) == dict:
            try:
                callid = calls.get("callid")
                    
                try:
                    recid = calls.get("recid")
                except:
                    recid = "" 
                  
                agency_id = calls.get("agency")
                
                try:
                    zone = calls.get("zone")
                except:
                    zone = ""
                    
                try:
                    unit = calls.get("unit")
                except:
                    unit = ""
                    
                address = calls.get("rtaddr")
                address = address.split(";", 1)[0]
                gps_x = f"{xpos[:4]}.{xpos[4:]}"
                gps_y = f"{ypos[:2]}.{ypos[2:]}"
                reported = calls.get("reprtd")
                sql_date = f"{reported[15:19]}-{reported[9:11]}-{reported[12:14]} {reported[0:8]}"
                
                if calls.get("type") == "l":
                    call_type = "Law"
                elif calls.get("type") == "f":
                    call_type = "Fire"
                elif calls.get("type") == "e":
                    call_type = "EMS"
                else:
                    call_type = "Other"
                    
                  
                try:
                    status = calls.get("stat")
                except:
                    status = ""
    
                try:
                    nature = calls.get("nature")
                except:
                    nature = ""
                    
                try:
                    city = calls.get("rtcity")
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
            for active_calls in calls:
                try:
                    callid = active_calls["callid"]
                    
                    try:
                        recid = active_calls["recid"]
                    except:
                        recid = "" 
                      
                    agency_id = active_calls["agency"]
                    
                    try:
                        zone = active_calls["zone"]
                    except:
                        zone = ""
                        
                    try:
                        unit = active_calls["unit"]
                    except:
                        unit = ""
                        
                    address = active_calls["rtaddr"]
                    address = address.split(";", 1)[0]
                    gps_x = f"{active_calls['xpos'][:4]}.{active_calls['xpos'][4:]}"
                    gps_y = f"{active_calls['ypos'][:2]}.{active_calls['ypos'][2:]}"
                    reported = active_calls["reprtd"]
                    sql_date = f"{reported[15:19]}-{reported[9:11]}-{reported[12:14]} {reported[0:8]}"
                    
                    if active_calls["type"] == "l":
                        call_type = "Law"
                    elif active_calls["type"] == "f":
                        call_type = "Fire"
                    elif active_calls["type"] == "e":
                        call_type = "EMS"
                    else:
                        call_type = "Other"
                        
                      
                    try:
                        status = active_calls["stat"]
                    except:
                        status = ""
     
                    try:
                        nature = active_calls["nature"]
                    except:
                        nature = ""
                        
                    try:
                        city = active_calls["rtcity"]
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
        return self.format()
