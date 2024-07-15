from pydantic import BaseModel


class UserGenerateAPIKeyRequest(BaseModel):
    uid: str


class UserCreateRequest(BaseModel):
    email: str
    password: str


class ValidateAPIKeyRequest(BaseModel):
    api_key: str
