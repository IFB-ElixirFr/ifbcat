import json
import os

import requests
from decouple import config

if not os.path.exists("settings.ini"):
    with open('settings.ini', 'w') as f:
        f.writelines(
            '\n'.join(["[settings]", "username=jdoe@ifb.fr", "password=unsecured", "baseurl=http://127.0.0.1:8092"])
        )


baseUrl = config('baseurl')
r = requests.post(
    url=f'{baseUrl}/api/user_auth/',
    data=dict(
        username=config('username'),
        password=config('password'),
    ),
)

token = json.loads(r.content.decode())["token"]


headers = {'Authorization': f'Token {token}'}
r = requests.get(f'{baseUrl}/api/licence/', headers=headers)
print(json.dumps(json.loads(r.content.decode()), indent=4))


r = requests.post(
    url=f'{baseUrl}/api/service/',
    data=dict(
        comments="my comment",
        training="Recurrent",
        mentoring=True,
        collaboration="both",
        prestation="Custom",
        team=f"{baseUrl}/api/team/ATGC/",
        domain=f"{baseUrl}/api/servicedomain/Transcriptomique/",
        analysis=f"{baseUrl}/api/kindofanalysis/RNAseq/",
        category=f"{baseUrl}/api/servicecategory/Data analysis/",
        communities=[
            f"{baseUrl}/api/lifesciencecommunity/Human/",
            f"{baseUrl}/api/lifesciencecommunity/Plants/",
        ],
    ),
    headers=headers,
)

print(r.content)
