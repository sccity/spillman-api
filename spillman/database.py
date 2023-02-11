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
import pymysql
from sqlalchemy import create_engine
from .settings import settings_data

db_info = {}
db_info["user"] = settings_data["database"]["user"]
db_info["password"] = settings_data["database"]["password"]
db_info["host"] = settings_data["database"]["host"]
db_info["schema"] = settings_data["database"]["schema"]

db = pymysql.connect(
    host=db_info["host"],
    user=db_info["user"],
    password=db_info["password"],
    database=db_info["schema"],
)

cursor = db.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
cursor.close()
