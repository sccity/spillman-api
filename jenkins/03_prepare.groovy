sh '''
cp config/settings.yaml.example config/settings.yaml

sed -i 's/^\(\s*host:\).*/\1 localhost/' config/settings.yaml
sed -i 's/^\(\s*schema:\).*/\1 spillmanapi/' config/settings.yaml
sed -i 's/^\(\s*user:\).*/\1 root/' config/settings.yaml
sed -i 's/^\(\s*password:\).*/\1 ""/' config/settings.yaml
'''