from pydantic import BaseModel
from typing import Dict, Any

print("Attempting to define classes without forward references...")
try:

    class FirebaseDocument(BaseModel):
        fields: Dict[str, Any]
        collections: Dict[str, FirebaseCollection]

    class FirebaseCollection(BaseModel):
        documents: Dict[str, FirebaseDocument]

except NameError as e:
    print(f"Caught expected NameError: {e}")
except Exception as e:
    print(f"Caught unexpected exception: {e}")
