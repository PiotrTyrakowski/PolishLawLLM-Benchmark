from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

cert_path = (
    Path(__file__).parent
    / "polishlawllm-benchmark-firebase-adminsdk-fbsvc-e3c923bf3f.json"
)
cred = credentials.Certificate(cert_path)

firebase_admin.initialize_app(cred)
firestore_db = firestore.client()
