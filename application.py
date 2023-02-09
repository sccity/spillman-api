# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from waitress import serve
import spillman as s
from spillman.settings import settings_data, version_data

app = Flask(__name__)
api = Api(app)

@app.route("/")
def http_root():
    return jsonify(application=version_data["program"],
                   version=version_data["version"],
                   environment=version_data["env"],
                   copyright=version_data["copyright"],
                   author=version_data["author"])
               
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404
  
api.add_resource(s.sycad, '/active')
api.add_resource(s.cadmastercalltable, '/incidents/cad')
api.add_resource(s.frmain, '/incidents/fire')
api.add_resource(s.emmain, '/incidents/ems')
api.add_resource(s.lwmain, '/incidents/law')
api.add_resource(s.rlmain, '/radiolog')
api.add_resource(s.rlavllog, '/avl')
api.add_resource(s.cdunit, '/unit')

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=settings_data["global"]["port"])
    app.debug = True
    app.run()
