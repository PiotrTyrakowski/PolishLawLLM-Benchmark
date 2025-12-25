import firebase_admin
from firebase_admin import firestore

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(
    "polishlawllm-benchmark-firebase-adminsdk-fbsvc-e3c923bf3f.json"
)
firebase_admin.initialize_app(cred)

db = firestore.client()
