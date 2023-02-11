# Spillman API
The Spillman API is an attempt to modernize the Spillman DataExchange for further application development on top of Spillman data. It takes a typical URL based GET request, translates it into the XML POST request DataExchange expects, and then converts the DataExchange XML output into standardized JSON. This also allows for ease of upgrades in the event Spillman changes something.

## REQUIREMENTS
*  A MySQL/MariaDB database with proper access rights. Currently, we are using Amazon AWS RDS.
*  Python 3.7+
*  AWS Elastic Beanstalk

This project is still in the early development phase and we will update this document accordingly as required.

## INSTALL
run: python3 -m venv venv && source venv/bin/activate\
run: pip install -r requirements.txt\

Rename example.settings.yaml to settings.yaml and update with your credentials and information\
Test that everything is working with python3 app.py\
The following commands are specific to Elastic Beanstalk, eb init will ask a few questions that will be specific to your environment\

run: eb init\
run: eb create\
run: eb deploy\

## SETTINGS
In the settings.yaml file you will notice there are smtp, spillman, and database settings. The smtp settings are for error reporting outside of file logging. The spillman settings are for your specific install of the DataExchange. It should look like https://yourserver/DataExchange/REST. Finally, the database settings are for tokens and audit trail data.

## USAGE
Will update this section soon!

## LICENSE
Copyright (c) Santa Clara City UT\
Developed for Sanata Clara - Ivins Fire & Rescue.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
