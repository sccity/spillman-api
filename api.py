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
               <h1>Spillman API</h1>
               <p>Copyright Santa Clara City, UT<br>Developed for Santa Clara - Ivins Fire & Rescue</p>
               </body>
               </html>"""
  
api.add_resource(s.sycad, '/active')
api.add_resource(s.cadmastercalltable, '/incidents/cad')
api.add_resource(s.frmain, '/incidents/fire')
api.add_resource(s.emmain, '/incidents/ems')
api.add_resource(s.lwmain, '/incidents/law')
api.add_resource(s.rlmain, '/radiolog')
api.add_resource(s.rlavllog, '/avl')
api.add_resource(s.cdunit, '/unit')

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)
    app.debug = True
    app.run()
