sh '''
cp config/settings.yaml.example config/settings.yaml

yq -iY '.database.host = "localhost"' config/settings.yaml
yq -iY '.database.schema = "spillmanapi"' config/settings.yaml
yq -iY '.database.user = "root"' config/settings.yaml
yq -iY '.database.password = ""' config/settings.yaml
'''