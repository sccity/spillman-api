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
import spillman as s
from .log import setup_logger
from .settings import settings_data

tablelist = setup_logger("tablelist", "tablelist")

class tablelist(Resource):
    def __init__(self):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
      
    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        tablelist = args.get("tablelist", default="*", type=str)
        
        auth = s.auth.check(token)
        if auth is True:
            pass
        else:
            return abort(403)
          
        data = []
        
        data.append({
                    "table": "apagncy",
                    "description": "Agency Codes"
                })
                
        data.append({
                    "table": "apagmisc",
                    "description": "Misc Agency Information"
                })
                
        data.append({
                    "table": "apcity",
                    "description": "City Codes"
                })
              
        data.append({
                    "table": "apnames",
                    "description": "Officer Names"
                })              
              
        data.append({
                    "table": "cdnatunt",
                    "description": "Units to Dispatch by Nature"
                })             
              
        data.append({
                    "table": "cdoffst",
                    "description": "Officer Status Codes"
                })
                
        data.append({
                    "table": "cdstatn",
                    "description": "Station Codes"
                })
                
        data.append({
                    "table": "cdunit",
                    "description": "Units"
                })
                
        data.append({
                    "table": "hmcbase",
                    "description": "Hazmat Chemicals"
                })
                
        data.append({
                    "table": "hmccas",
                    "description": "Chemical CAS Numbers"
                })
                
        data.append({
                    "table": "hmcnam",
                    "description": "Chemical Names"
                })
                
        data.append({
                    "table": "hmcsyn",
                    "description": "Chemical Synonyms"
                })
                
        data.append({
                    "table": "rumain",
                    "description": "Recommended Units Table"
                })
                
        data.append({
                    "table": "rutypes",
                    "description": "Recommended Unit Types"
                })
                
        data.append({
                    "table": "ruvalid",
                    "description": "Recommended Unit Times"
                })
                
        data.append({
                    "table": "tbakaknd",
                    "description": "Vehicle Kinds"
                })
                
        data.append({
                    "table": "tbhowrc",
                    "description": "How Received Codes"
                })
                
        data.append({
                    "table": "tbnataka",
                    "description": "Nature Alias Table"
                })
                
        data.append({
                    "table": "tbnatur",
                    "description": "Natures"
                })
                
        data.append({
                    "table": "tbpdterm",
                    "description": "Determinant Codes"
                })
                
        data.append({
                    "table": "tbvehaka",
                    "description": "Vehicle Kind Alias"
                })
                
        data.append({
                    "table": "tbvehknd",
                    "description": "Vehicle Kind"
                })
                
        data.append({
                    "table": "tbxnames",
                    "description": "Officer Extra Data"
                })
                
        data.append({
                    "table": "tbzones",
                    "description": "Zones"
                })
                
        data.append({
                    "table": "tbzones",
                    "description": "Zones"
                })
                
        data.append({
                    "table": "syunit",
                    "description": "System Units "
                })
                
        return data
