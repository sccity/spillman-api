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

table = setup_logger("table", "table")
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class table(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        
    def dataexchange(self, table):
        session = requests.Session()
        session.auth = (self.api_usr, self.api_pwd)
        request = f"""
        <PublicSafetyEnvelope version="1.0">
            <PublicSafety id="">
                <Query>
                    <{table}>
                    </{table}>
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
                data = data["PublicSafetyEnvelope"]["PublicSafety"]["Response"][f"{table}"]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    table.error(traceback.format_exc())
                    return

        except Exception as e:
            table.error(traceback.format_exc())
            return

        return data
      
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        table = args.get("table", default="*", type=str)
        
        auth = s.auth.check(token)
        if auth is True:
            pass
        else:
            return abort(403)
          
        return self.dataexchange(table)