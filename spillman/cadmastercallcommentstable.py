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

cadmastercallcommentstable = setup_logger("cadmastercallcommentstable", "cadmastercallcommentstable")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class cadmastercallcommentstable(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def dataexchange(self, cadcallid):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <CADMasterCallCommentsTable>
                        <LongTermCallID search_type="equal_to">{cadcallid}</LongTermCallID>
                    </CADMasterCallCommentsTable>
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
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"]["CADMasterCallCommentsTable"]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    cadmastercallcommentstable.error(traceback.format_exc())
                    return

        except Exception as e:
            cadmastercallcommentstable.error(traceback.format_exc())
            return

        return data
      
    def process(self, cadcallid):
        spillman = self.dataexchange(cadcallid)
        data = []
        
        try:
            callid = spillman.get("LongTermCallID")
        except:
            callid = ""
        
        try:
            comment = spillman.get("CallTakerComments")
        except:
            comment = "" 
              
        data.append({
            "call_id": callid,
            "comments": comment
        })
                
        return data
                  
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        cadcallid = args.get("callid", default="", type=str)

        auth = s.auth.check(token)
        if auth is True:
            pass
        else:
            return abort(403)
          
        if cadcallid == "":
            return jsonify(error="Missing callid argument.")
          
        return self.process(cadcallid)
