import json
import os

auth = {}

# Open up `secrets.json` which is in the same directory as `secrets.py`.
secrets_file = open(os.path.join(os.path.dirname(__file__),'secrets.json'),'r')
auth = json.load(secrets_file)
secrets_file.close()
