# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
from flask import Flask
from flask_restful import Resource, Api, reqparse
from waitress import serve
import spillman as s
from spillman.settings import settings_data

app = Flask(__name__)
api = Api(app)

@app.route("/")
def http_root():
    return f"""<html>
               <head>
               <title>Spillman API</title>
               </head>
               <body>
               <p>Spillman API</p><br>
               <p>Copyright Santa Clara City, UT</p><br>
               <p>Developed for Santa Clara - Ivins Fire & Rescue</p>
               </body>
               </html>"""
               
@app.route("/v1")
def v1_root():
    return ""
  
api.add_resource(s.sycad, '/v1/active')
api.add_resource(s.frmain, '/v1/incidents/fire')
api.add_resource(s.emmain, '/v1/incidents/ems')
api.add_resource(s.lwmain, '/v1/incidents/law')
api.add_resource(s.rlmain, '/v1/radiolog')
api.add_resource(s.rlavllog, '/v1/avl')

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)
    app.run()
