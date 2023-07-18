# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# **********************************************************
# Spillman API
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import Flask, jsonify
from flask_restful import Api
import spillman as s
from spillman.settings import settings_data, version_data

app = Flask(__name__)
api = Api(app)

@app.route("/")
def http_root():
    return jsonify(
        application=version_data["program"],
        version=version_data["version"],
        environment=settings_data["global"]["env"],
        copyright=version_data["copyright"],
        author=version_data["author"],
    )

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

api.add_resource(s.table, "/spillman/table")
api.add_resource(s.tablelist, "/spillman/table/list")
api.add_resource(s.units, "/spillman/unit")
api.add_resource(s.unitstatus, "/spillman/unit/status")
api.add_resource(s.active, "/cad/active")
api.add_resource(s.comments, "/cad/comments")
api.add_resource(s.names, "/name")
api.add_resource(s.calls, "/incidents/cad")
api.add_resource(s.law, "/incidents/law")
api.add_resource(s.fire, "/incidents/fire")
api.add_resource(s.ems, "/incidents/ems")
api.add_resource(s.reclog, "/incidents/reclog")
api.add_resource(s.radiolog, "/radiolog")
api.add_resource(s.avl, "/avl")
api.add_resource(s.emd, "/emd")
api.add_resource(s.rlog, "/rlog")

if __name__ == "__main__":
    app.run()
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=8000)
