# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.#
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
from .database import db

class auth:
    def __init__(self):
        return
      
    def check(token, ipaddr):
        cursor = db.cursor()
        cursor.execute(f"""SELECT active from tokens where token = '{token}'""")
        db_response = cursor.fetchone()
        
        try:
            db_valid = db_response[0]
        except:
            db_valid = 0
            
        cursor.close()
        
        if db_valid is None:
            valid = False
            cursor = db.cursor()
            cursor.execute(f"insert into audit (token,ipaddr,resource,action,datetime) values ('{token}','{ipaddr}','AUTH','ACCESS DENIED',now())")
            db.commit()
            cursor.close()
        elif db_valid == 1:
            valid = True
        else:
            valid = False
            cursor = db.cursor()
            cursor.execute(f"insert into audit (token,ipaddr,resource,action,datetime) values ('{token}','{ipaddr}','AUTH','ACCESS DENIED',now())")
            db.commit()
            cursor.close()
        
        return valid
      
    def audit(token, ipaddr, resource, action):
        cursor = db.cursor()
        cursor.execute(f"insert into audit (token,ipaddr,resource,action,datetime) values ('{token}','{ipaddr}','{resource}','{action}',now())")
        db.commit()
        cursor.close()
        return
