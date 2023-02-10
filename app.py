# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
from flask import Flask, jsonify
from flask_restful import Resource, Api
import spillman as s
from spillman.settings import version_data

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
  
api.add_resource(s.table, '/spillman/table')
api.add_resource(s.tablelist, '/spillman/table/list')
api.add_resource(s.cdunit, '/spillman/unit')
api.add_resource(s.sycad, '/cad/active')
api.add_resource(s.cadmastercallcommentstable, '/cad/comments')
api.add_resource(s.cadmastercalltable, '/incidents/cad')
api.add_resource(s.lwmain, '/incidents/law')
api.add_resource(s.frmain, '/incidents/fire')
api.add_resource(s.emmain, '/incidents/ems')
api.add_resource(s.rlmain, '/radiolog')
api.add_resource(s.rlavllog, '/avl')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
