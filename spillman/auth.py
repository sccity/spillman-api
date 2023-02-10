# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
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
            cursor = db.cursor()
            cursor.execute(f"insert into audit (token,ipaddr,resource,action,datetime) values ('{token}','{ipaddr}','AUTH','ACCESS GRANTED',now())")
            db.commit()
            cursor.close()
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
