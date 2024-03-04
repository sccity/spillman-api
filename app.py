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
# from spillman.api import create_app
from flask import jsonify
from flask_restful import Api
import spillman as s
from spillman.settings import settings_data, version_data
from flask_swagger_ui import get_swaggerui_blueprint

app = s.spillman_api()
api = Api(app)

SWAGGER_URL = "/docs"
API_URL = "/static/swagger.yaml"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": version_data["program"]}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.errorhandler(404)
def PageNotFound(e):
    return jsonify(error=str(e)), 404


@app.route("/", methods=["GET"])
def HttpRoot():
    return jsonify(
        application=version_data["program"],
        version=version_data["version"],
        environment=settings_data["global"]["env"],
        copyright=version_data["copyright"],
        author=version_data["author"],
    )


api.add_resource(s.ActiveCalls, "/cad/active")
api.add_resource(s.ActiveUnits, "/cad/active/units")
api.add_resource(s.Avl, "/avl")
api.add_resource(s.Calls, "/incidents/cad")
api.add_resource(s.Comments, "/cad/comments")
api.add_resource(s.Ems, "/incidents/ems")
api.add_resource(s.Emd, "/emd")
api.add_resource(s.Fire, "/incidents/fire")
api.add_resource(s.Law, "/incidents/law")
api.add_resource(s.LawNarrative, "/incidents/law/narrative")
api.add_resource(s.NameImage, "/name/image")
api.add_resource(s.NameInvolvements, "/name/involvements")
api.add_resource(s.Names, "/name")
api.add_resource(s.RadioLog, "/radiolog")
api.add_resource(s.RecLog, "/incidents/reclog")
api.add_resource(s.Table, "/spillman/table")
api.add_resource(s.TableList, "/spillman/table/list")
api.add_resource(s.UnitStatus, "/spillman/unit/status")
api.add_resource(s.Units, "/spillman/unit")

if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=settings_data["global"]["port"], threads=100)
