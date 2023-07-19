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
import json, logging, xmltodict, traceback, collections, requests, time
import spillman as spillman
from flask_restful import Resource, Api, request
from flask import jsonify, abort
from datetime import date, timedelta
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .log import setup_logger
from .settings import settings_data
from .database import db

err = setup_logger("rlog", "rlog")

class rlog(Resource):
    def rlog(self, rlog_unit, rlog_status, rlog_comment, rlog_user, rlog_pass):
        o = Options()
        o.binary_location = "/usr/bin/google-chrome"
        o.add_argument("--no-sandbox")
        o.add_argument("--disable-extensions")
        o.add_argument("--disable-dev-shm-usage")
        o.add_argument("--headless=new")
        o.add_argument("--disable-gpu")
        o.add_argument("--remote-debugging-port=9222")
        
        try:
            browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=o)
            browser.get(settings_data["spillman"]["touch_url"])
    
        except:
            err.error(traceback.format_exc())
            return jsonify(result="error")
    
        time.sleep(0.1)
    
        username = browser.find_element(By.ID, "j_username")
        username.send_keys(rlog_user)
        password = browser.find_element(By.ID, "j_password")
        password.send_keys(rlog_pass)
        password = browser.find_element(By.ID, "unit")
        password.send_keys(rlog_unit)
    
        time.sleep(0.1)
    
        try:
            browser.find_element(By.XPATH, value='//input[@value="Login"]').submit()
        except:
            return jsonify(result="error")
    
        time.sleep(0.1)
    
        try:
            browser.get(settings_data["spillman"]["touch_url"] + "secure/radiolog")
        except:
            return jsonify(result="error")
    
        time.sleep(0.1)
    
        try:
            rlog = Select(browser.find_element(By.XPATH, "//select[@name='status']"))
            rlog.select_by_value(rlog_status)
    
        except:
            return jsonify(result="error")
    
        try:
            comment = browser.find_element(By.NAME, "comment")
            comment.send_keys(rlog_comment + " - Fire MDC")
    
        except:
            return jsonify(result="error")
    
        time.sleep(0.1)
    
        try:
            browser.find_element(By.XPATH, value='//input[@value="Submit"]').submit()
    
        except:
            return jsonify(result="error")
    
        browser.quit()
        return jsonify(result="success")

    def get(self):
        args = request.args
        token = args.get("token", default="", type=str)
        rlog_unit = args.get("unit", default="", type=str)
        rlog_status = args.get("status", default="", type=str)
        rlog_comment = args.get("comment", default="", type=str)
        rlog_user = args.get("usr", default="", type=str)
        rlog_pass = args.get("pwd", default="", type=str)

        if token == "":
            s.auth.audit("Missing", request.access_route[0], "AUTH", "ACCESS DENIED")
            return jsonify(error="No security token provided.")

        auth = spillman.auth.check(token, request.access_route[0])
        if auth is True:
            pass
        else:
            return abort(403)

        spillman.auth.audit(
            token,
            request.access_route[0],
            "RLOG",
            f"UNIT: {rlog_unit} STATUS: {rlog_status} COMMENNT: {rlog_comment}",
        )

        return self.rlog(rlog_unit, rlog_status, rlog_comment, rlog_user, rlog_pass)
