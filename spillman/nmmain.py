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

err = setup_logger("nmmain", "nmmain")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class nmmain(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def dataexchange(self, number, last, first, middle, phone, ntype, dl, dlstate, stateid, ssn):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <nmmain>
                        <number search_type="equal_to">{number}</number>
                        <last search_type="equal_to">{last}</last>
                        <first search_type="equal_to">{first}</first>
                        <middle search_type="equal_to">{middle}</middle>
                        <phone search_type="equal_to">{phone}</phone>
                        <nametyp search_type="equal_to">{ntype}</nametyp>
                        <dlnum search_type="equal_to">{dl}</dlnum>
                        <dlstate search_type="equal_to">{dlstate}</dlstate>
                        <stateid search_type="equal_to">{stateid}</stateid>
                        <ssnum search_type="equal_to">{ssn}</ssnum>
                    </nmmain>
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
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["nmmain"]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return

        except Exception as e:
            err.error(traceback.format_exc())
            return

        return data
      
    def process(self, number, last, first, middle, phone, ntype, dl, dlstate, stateid, ssn):
        spillman = self.dataexchange(number, last, first, middle, phone, ntype, dl, dlstate, stateid, ssn)
        data = []
        
        if spillman is None:
            return
        
        elif type(spillman) == dict:
            try:
                name_id = spillman.get("number")
            except:
                name_id = ""
                
            try:
                name_type = spillman.get("nametyp")
            except:
                name_type = ""
                
            try:
                ssn = spillman.get("ssnum")
            except:
                ssn = ""
                
            try:
                license_num = spillman.get("dlnum")
            except:
                license_num = ""
                
            try:
                license_state = spillman.get("dlstate")
            except:
                license_state = ""
                
            try:
                state_id = spillman.get("stateid")
            except:
                state_id = ""
              
            try:
                first_name = spillman.get("first")
            except:
                first_name = ""
              
            try:
                last_name = spillman.get("last")
            except:
                last_name = ""
                
            try:
                middle_name = spillman.get("middle")
            except:
                middle_name = ""
                
            try:
                suffix = spillman.get("suffix")
            except:
                suffix = ""
                
            try:
                alias = spillman.get("aka")
            except:
                alias = ""
                
            try:
                bday = spillman.get("birthd")
                birth_day = f"{bday[6:10]}-{bday[0:2]}-{bday[3:5]}"
            except:
                birth_day = "1900-01-01 00:00:00"
                
            try:
                height = spillman.get("height")
                height = height.replace("'", "ft ")
                height = height.replace('"', "in")
            except:
                height = ""
                
            try:
                weight = spillman.get("weight")
            except:
                weight = ""
                
            try:
                sex = spillman.get("sex")
            except:
                sex = ""
                
            try:
                gender = spillman.get("gender")
            except:
                gender = ""
                
            try:
                race = spillman.get("race")
            except:
                race = ""
                
            try:
                ethnic = spillman.get("ethnic")
            except:
                ethnic = ""
                
            try:
                hair = spillman.get("hair")
            except:
                hair = ""
                
            try:
                hairstyle = spillman.get("hairsty")
            except:
                hairstyle = ""
                
            try:
                eyes = spillman.get("eyes")
            except:
                eyes = ""
                
            try:
                glasses = spillman.get("glasses")
            except:
                glasses = ""
                
            try:
                build = spillman.get("build")
            except:
                build = ""
                
            try:
                complexion = spillman.get("cmplx")
            except:
                complexion = ""
                
            try:
                facial = spillman.get("facial")
            except:
                facial = ""
                
            try:
                speech = spillman.get("speech")
            except:
                speech = ""
                
            try:
                address = spillman.get("street")
                address = address.replace('"', '')
                address = address.replace("'", "")
                address = address.replace(";", "")  
            except:
                address = ""
                
            try:
                city = spillman.get("city")
            except:
                city = ""   
            
            try:
                state = spillman.get("state")
            except:
                state = ""   
                
            try:
                zip = spillman.get("zip")
            except:
                zip = ""
                
            try:
                primary_phone = spillman.get("phone")
                primary_phone = primary_phone.replace('(', '')
                primary_phone = primary_phone.replace(")", "")
                primary_phone = primary_phone.replace("-", "")
            except:
                primary_phone = ""
                
            try:
                work_phone = spillman.get("wrkphn")
                work_phone = work_phone.replace('(', '')
                work_phone = work_phone.replace(")", "")
                work_phone = work_phone.replace("-", "")
            except:
                work_phone = ""
              
            data.append({
                "name_id": name_id,
                "name_type": name_type,
                "ssn": ssn,
                "license_num": license_num,
                "license_state": license_state,
                "state_id": state_id,
                "first_name": first_name,
                "last_name": last_name,
                "middle_name": middle_name,
                "suffix": suffix,
                "alias": alias,
                "birth_date": birth_day,
                "height": height,
                "weight": weight,
                "sex": sex,
                "gender": gender,
                "race": race,
                "ethnicity": ethnic,
                "hair_color": hair,
                "hair_style": hairstyle,
                "eye_color": eyes,
                "glasses": glasses,
                "build": build,
                "complexion": complexion,
                "facial_hair": facial,
                "speech_style": speech,
                "address": address,
                "city": city,
                "state": state,
                "zip": zip,
                "primary_phone": primary_phone,
                "work_phone": work_phone
            })

        else:
            for row in spillman:
                try:
                    name_id = row["number"]
                except:
                    name_id = ""
                    
                try:
                    name_type = row["nametyp"]
                except:
                    name_type = ""
                    
                try:
                    ssn = row["ssnum"]
                except:
                    ssn = ""
                    
                try:
                    license_num = row["dlnum"]
                except:
                    license_num = ""
                    
                try:
                    license_state = row["dlstate"]
                except:
                    license_state = ""
                    
                try:
                    state_id = row["stateid"]
                except:
                    state_id = ""
                  
                try:
                    first_name = row["first"]
                except:
                    first_name = ""
                  
                try:
                    last_name = row["last"]
                except:
                    last_name = ""
                    
                try:
                    middle_name = row["middle"]
                except:
                    middle_name = ""
                    
                try:
                    suffix = row["suffix"]
                except:
                    suffix = ""
                    
                try:
                    alias = row["aka"]
                except:
                    alias = ""
                    
                try:
                    bday = row["birthd"]
                    birth_day = f"{bday[6:10]}-{bday[0:2]}-{bday[3:5]}"
                except:
                    birth_day = "1900-01-01 00:00:00"
                    
                try:
                    height = row["height"]
                    height = height.replace("'", "ft ")
                    height = height.replace('"', "in")
                except:
                    height = ""
                    
                try:
                    weight = row["weight"]
                except:
                    weight = ""
                    
                try:
                    sex = row["sex"]
                except:
                    sex = ""
                    
                try:
                    gender = row["gender"]
                except:
                    gender = ""
                    
                try:
                    race = row["race"]
                except:
                    race = ""
                    
                try:
                    ethnic = row["ethnic"]
                except:
                    ethnic = ""
                    
                try:
                    hair = row["hair"]
                except:
                    hair = ""
                    
                try:
                    hairstyle = row["hairsty"]
                except:
                    hairstyle = ""
                    
                try:
                    eyes = row["eyes"]
                except:
                    eyes = ""
                    
                try:
                    glasses = row["glasses"]
                except:
                    glasses = ""
                    
                try:
                    build = row["build"]
                except:
                    build = ""
                    
                try:
                    complexion = row["cmplx"]
                except:
                    complexion = ""
                    
                try:
                    facial = row["facial"]
                except:
                    facial = ""
                    
                try:
                    speech = row["speech"]
                except:
                    speech = ""
                    
                try:
                    address = row["street"]
                    address = address.replace('"', '')
                    address = address.replace("'", "")
                    address = address.replace(";", "")  
                except:
                    address = ""
                    
                try:
                    city = row["city"]
                except:
                    city = ""   
                
                try:
                    state = row["state"]
                except:
                    state = ""   
                    
                try:
                    zip = row["zip"]
                except:
                    zip = ""
                    
                try:
                    primary_phone = row["phone"]
                    primary_phone = primary_phone.replace('(', '')
                    primary_phone = primary_phone.replace(")", "")
                    primary_phone = primary_phone.replace("-", "")
                except:
                    primary_phone = ""
                    
                try:
                    work_phone = row["wrkphn"]
                    work_phone = work_phone.replace('(', '')
                    work_phone = work_phone.replace(")", "")
                    work_phone = work_phone.replace("-", "")
                except:
                    work_phone = ""
                  
                data.append({
                    "name_id": name_id,
                    "name_type": name_type,
                    "ssn": ssn,
                    "license_num": license_num,
                    "license_state": license_state,
                    "state_id": state_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "middle_name": middle_name,
                    "suffix": suffix,
                    "alias": alias,
                    "birth_date": birth_day,
                    "height": height,
                    "weight": weight,
                    "sex": sex,
                    "gender": gender,
                    "race": race,
                    "ethnicity": ethnic,
                    "hair_color": hair,
                    "hair_style": hairstyle,
                    "eye_color": eyes,
                    "glasses": glasses,
                    "build": build,
                    "complexion": complexion,
                    "facial_hair": facial,
                    "speech_style": speech,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zip": zip,
                    "primary_phone": primary_phone,
                    "work_phone": work_phone
                })
                
        return data
                  
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        number = args.get("num", default="*", type=str)
        last = args.get("last", default="*", type=str)
        first = args.get("first", default="*", type=str)
        middle = args.get("middle", default="*", type=str)
        phone = args.get("phone", default="*", type=str)
        ntype = args.get("type", default="*", type=str)
        dl = args.get("dl", default="*", type=str)
        dlstate = args.get("dlstate", default="*", type=str)
        stateid = args.get("stateid", default="*", type=str)
        ssn = args.get("ssn", default="*", type=str)
        
        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", f"ACCESS DENIED")
            return jsonify(error="No security token provided.")
        
        auth = s.auth.check(token, request.access_route[0])
        
        if auth is True:
            pass
        else:
            return abort(403)
          
        if ssn == "*":
            ssn = "*"
        else:
            ssn = f"{ssn[0:3]}-{ssn[3:5]}-{ssn[5:10]}"
          
        s.auth.audit(token, request.access_route[0], "NMMAIN", 
        f"NUMBER: {number} LAST: {last} FIRST: {first} MIDDLE: {middle} PHONE: {phone} TYPE: {ntype} DLNUM: {dl} DLSTATE: {dlstate} STATEID: {stateid} SSN: {ssn}")
        
        return self.process(number, last, first, middle, phone, ntype, dl, dlstate, stateid, ssn)
