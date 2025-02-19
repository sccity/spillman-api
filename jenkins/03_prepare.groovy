sh '''
cp config/settings.yaml.example config/settings.yaml

sed -i 's/^host=.*/host=localhost/' config/settings.yaml
sed -i 's/^schema=.*/schema=influence360/' config/settings.yaml
sed -i 's/^user=.*/user=root/' config/settings.yaml
sed -i 's/^password=.*/password=/' config/settings.yaml
'''