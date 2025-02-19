sh '''
python3.10 app.py --check-config
yq -iY '.version = "$commit_hash"' spillman/version.yaml
'''