# Spillman API [![CircleCI](https://dl.circleci.com/status-badge/img/gh/sccity/spillman-api/tree/prod.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/sccity/spillman-api/tree/prod) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/b9f3e0f2cc6b4731af46372f79cab252)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sccity/spillman-api&amp;utm_campaign=Badge_Grade)

The Spillman API is an attempt to modernize the Spillman DataExchange for further application development on top of Spillman data. It takes a typical URL based GET request, translates it into the XML POST request DataExchange expects, and then converts the DataExchange XML output into standardized JSON. This also allows for ease of upgrades in the event Spillman changes something.

## REQUIREMENTS
*  Spillman server with proper access rights & DataExchange enabled.
*  A MySQL/MariaDB database with proper access rights. Currently, we are using Amazon AWS RDS.
*  Docker & Docker Compose

## INSTALL
We highly recommend people use docker for running the Spillman API, whether you are on Windows, macOS or Linux. This assumes you have Docker and Docker Compose already installed. You may have to make some changes to work on macOS or Windows; it's been untested on these environments. This will create three microservices utilizing docker. It will create a spillman-api prod/dev instance, and a proxy server.
```
cd /opt
git clone https://github.com/sccity/spillman-api.git
cd spillman-api
./server.sh start
```

## SETTINGS
### Spillman DataExchange
In the config directory you will find a dev and prod folder that needs a settings.yaml. There is an example in each called settings.yaml.example. You will notice there are smtp, spillman, and database settings. The smtp settings are for error reporting outside of file logging. The spillman settings are for your specific install of the DataExchange. It should look like https://yourserver/DataExchange/REST. The prod folder should point to your production Spillman DataExchange, and the dev folder should point to your dev/practice DataExchange. Finally, the database settings are for tokens and audit trail data. If you want to completely separate the environments out, you can use two different SQL servers as well. However, we use a shared databse as we want all of the audit data in one location. Sometimes we will test in dev on the production spillman server instead of practice, and this allows all audit data to be stored in one place. 

### Proxy Server
In the config/nginx folder you will see example configuration files. They need to be renamed to just default.conf, spillman-api-dev.conf, and spillman-api-prod.conf. You only need to edit the server_name to be your hostname. If you don't want to do host based routing for the proxy server, you can only enable default.com and it can be reached via http://yourip. It is strongly recommended however to use host based routing for externally published endpoints so that you can enable SSL encryption. While this document does not cover enabling SSL, CloudFlare makes the process easy and seemless.

## BASIC COMMANDS
```
# Start the Spillman API
$ ./server.sh start

# Restart Spillman API (useful if things get stuck)
$ ./server.sh restart

# Stop the Spillman API server (temporarily)
$ ./server.sh stop

# Halt the Spillman API server
$ ./server.sh down

# Update everything to the latest version
$ ./server.sh update

# Rebuild everything from scratch
$ ./server.sh rebuild
```

## PORTS USED
80: Proxy Server\
8888: Spillman API Production\
8889: Spillman API Development

## LICENSE
Copyright (c) Santa Clara City UT\
Developed for Sanata Clara - Ivins Fire & Rescue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
