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

lwmain = setup_logger("lwmain", "lwmain")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class lwmain(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def incident(self, agency, start, end):
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
                    <lwmain>
                        <agency search_type="equal_to">{agency}</agency>
                        <dispdat search_type="greater_than">{start_date}</dispdat>
                        <dispdat search_type="less_than">{end_date}</dispdat>
                    </lwmain>
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
                calls = calls["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["lwmain"]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    lwmain.error(traceback.format_exc())
                    return

        except Exception as e:
            lwmain.error(traceback.format_exc())
            return

        return calls
      
    def format(self, agency, start, end):
        calls = self.incident(agency, start, end)
        data = []
        if type(calls) == dict:
            return 

        else:
            for call in calls:
                try:
                    callid = call['callid']
                except KeyError:
                    continue
                except TypeError:
                    continue
                  
                try:
                    incident_id = call['number']
                except KeyError:
                    continue
                except TypeError:
                    continue
                  
                try:
                    nature = call['nature']
                except KeyError:
                    nature = ""
                    
                try:
                    address = call['address']
                    address = address.replace('"', '')
                    address = address.replace("'", "")
                    address = address.replace(";", "")  
                except KeyError:
                    address = ""
                    
                try:
                    city = call['city']
                except KeyError:
                    city = ""   
                
                try:
                    state = call['state']
                except KeyError:
                    state = ""   
                    
                try:
                    zip = call['zip']
                except KeyError:
                    zip = ""     
                  
                try:
                    location = call['locatn']
                except KeyError:
                    location = ""      
                  
                try:
                    agency = call['agency']
                except KeyError:
                    agency = ""
                except TypeError:
                    agency = ""
            
                try:
                    occurred_dt1 = call['ocurdt1']
                    occurred_dt1 = f"{occurred_dt1[15:19]}-{occurred_dt1[9:11]}-{occurred_dt1[12:14]} {occurred_dt1[0:8]}"
                except KeyError:
                    occurred_dt1 = "1900:01:01 00:00:00"
                    
                try:
                    occurred_dt2 = call['ocurdt2']
                    occurred_dt2 = f"{occurred_dt2[15:19]}-{occurred_dt2[9:11]}-{occurred_dt2[12:14]} {occurred_dt2[0:8]}"
                except KeyError:
                    occurred_dt2 = "1900:01:01 00:00:00"
                try:
                    reported_dt = call['dtrepor']
                    reported_dt = f"{reported_dt[15:19]}-{reported_dt[9:11]}-{reported_dt[12:14]} {reported_dt[0:8]}"
                except KeyError:
                    reported_dt = "1900:01:01 00:00:00"
                
                try:
                    dispatch_dt = call['dispdat']
                    dispatch_dt = f"{dispatch_dt[6:10]}-{dispatch_dt[0:2]}-{dispatch_dt[3:5]} 00:00:00"
                except KeyError:
                    dispatch_dt = "1900:01:01 00:00:00"
                
                try:
                    contact = call['contact']
                    contact = contact.replace('"', '')
                    contact = contact.replace("'", "")
                except KeyError:
                    contact = ""
                    
                try:
                    condition = call['condtkn']
                except KeyError:
                    condition = ""
                    
                try:
                    disposition = call['dispos']
                except KeyError:
                    disposition = ""
                        
                try:
                    howrc = call["howrc"]
                except:
                    howrc = ""
                    
                if howrc == "2":
                    how_received = "CAD2CAD"
                elif howrc == "9":
                    how_received = "911 Line"
                elif howrc == "T":
                    how_received = "Telephone"
                elif howrc == "O":
                    how_received = "Officer Report"
                elif howrc == "R":
                    how_received = "Radio"
                elif howrc == "P":
                    how_received = "In Person"
                else:
                    how_received = "Other"
                  
                data.append({
                    "call_id": callid,
                    "incident_id": incident_id,
                    "agency": agency,
                    "nature": nature,
                    "zone": location,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zip,
                    "received_type": how_received,
                    "condition": condition,
                    "disposition": disposition,
                    "occurred_dt1": occurred_dt1,
                    "occurred_dt2": occurred_dt2,
                    "reported": reported_dt,
                    "date": dispatch_dt
                })
                
        return data
                  
    def get(self):
        args = request.args
        agency = args.get("agency", default="*", type=str)
        start = args.get("start", default="", type=str)
        end = args.get("end", default="", type=str)
        
        return self.format(agency, start, end)
