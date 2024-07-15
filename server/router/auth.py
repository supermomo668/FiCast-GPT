import firebase_admin
from firebase_admin import auth, firestore
from fastapi import APIRouter, HTTPException, Request
import secrets
from datetime import datetime

from .validators import (
    UserCreateRequest,
    UserGenerateAPIKeyRequest,
    ValidateAPIKeyRequest,
)

# Initialize Firestore DB
db = firestore.client()

router = APIRouter()


@router.post("/create-user")
async def create_user(user: UserCreateRequest):
    try:
        user_record = auth.create_user(email=user.email, password=user.password)

        # Store the user's email in Firestore (without API key)
        db.collection("users").document(user_record.uid).set({"email": user.email})
        return {"message": "User created successfully", "uid": user_record.uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-api-key")
async def generate_api_key_for_user(request: UserGenerateAPIKeyRequest):

    def generate_api_key():
        return secrets.token_hex(32)

    try:
        user_ref = db.collection("users").document(request.uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            api_key = generate_api_key()
            user_ref.update(
                {
                    "api_key": api_key,
                    "api_key_created_at": datetime.utcnow().isoformat(),
                }
            )
            return {"message": "API key generated successfully", "api_key": api_key}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate-api-key")
async def validate_api_key(request: ValidateAPIKeyRequest):
    try:
        # Query Firestore for the user with the given API key
        users_ref = db.collection("users")
        query = users_ref.where("api_key", "==", request.api_key)
        results = query.stream()

        # Check if any user matches the API key
        for user in results:
            user_data = user.to_dict()
            if "api_key" in user_data and user_data["api_key"] == request.api_key:
                return {"message": "API key is valid", "uid": user.id}

        # If no user matches the API key
        raise HTTPException(status_code=401, detail="Invalid API key")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# class GoogleSignInRequest(BaseModel):
#     id_token: str


# @router.post(
#     "/google-signin",
#     summary="Google Sign-In",
#     response_description="User signed in successfully",
# )
# async def google_signin(sign_in_request: GoogleSignInRequest):
#     id_token = sign_in_request.id_token
#     if not id_token:
#         raise HTTPException(status_code=400, detail="ID token is required")

#     try:
#         # Verify the ID token
#         decoded_token = auth.verify_id_token(id_token)
#         uid = decoded_token["uid"]
#         return {"message": "User signed in successfully", "uid": uid}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
