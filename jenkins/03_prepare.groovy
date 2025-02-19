sh '''
cp config/settings.yaml.example config/settings.yaml

yq eval '.database.host = "localhost"' -i config/settings.yaml
yq eval '.database.schema = "spillmanapi"' -i config/settings.yaml
yq eval '.database.user = "root"' -i config/settings.yaml
yq eval '.database.password = ""' -i config/settings.yaml
'''