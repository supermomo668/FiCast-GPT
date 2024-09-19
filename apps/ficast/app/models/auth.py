from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import timedelta, datetime, timezone

# Enum to define access levels with tied default durations and restrictions
class AccessLevelEnum(str, Enum):
    FREEMIUM = "freemium"
    PREMIUM = "premium"
    ADMIN = "admin"

class AccessDurationModel(Enum):
    FREEMIUM = timedelta(days=180)
    PREMIUM = timedelta(days=180)
    ADMIN = timedelta(days=365 * 100)

class AccessMaxParticipantModel(Enum):
    FREEMIUM = 2
    PREMIUM = None
    ADMIN = None

# Define Access Level
class AccessLevelModel(BaseModel):
    access_level: AccessLevelEnum
    token_duration: timedelta  = Field(
      AccessDurationModel.FREEMIUM, 
      description="Default duration for access level"
    )
    token_expiry: Optional[datetime] = Field(
      None, 
      description="Specific expiry date and time for the token"
    )
    max_participants: Optional[int] = Field(
      AccessMaxParticipantModel.FREEMIUM, 
      description="Maximum participants allowed for podcast creation"
    )
    @field_validator('token_expiry')
    def validate_token_expiry(cls, value, values):
        if value and 'token_duration' in values:
            raise ValueError(
                "Cannot set both 'token_duration' and 'token_expiry'")
        return value
    @classmethod
    def get_access_level_info(cls, access_level: AccessLevelEnum) -> "AccessLevelModel":
        """ Returns the default values for each access level """
        if access_level == AccessLevelEnum.FREEMIUM:
            return AccessLevelModel(
                access_level=AccessLevelEnum.FREEMIUM,
            )
        elif access_level == AccessLevelEnum.PREMIUM:
            return AccessLevelModel(
                access_level=AccessLevelEnum.PREMIUM,
                max_participants=None  # Unlimited participants
            )
        elif access_level == AccessLevelEnum.ADMIN:
            return AccessLevelModel(
                access_level=AccessLevelEnum.ADMIN,
                token_duration=timedelta(
                    days=365 * 100),  
            )

class TokenSourceModel(str, Enum):
    # use only lowercase 
    FIREBASE = "firebase"
    BEARER = "bearer"
    LOGIN = "login"

# Token parameters model
class TokenAuthModel(BaseModel):
    token_type: TokenSourceModel = TokenSourceModel.BEARER
    access_level: AccessLevelEnum
    expire_delta: Optional[timedelta] = Field(default=AccessDurationModel.FREEMIUM, alias="expires_in")
    expires_at: Optional[timedelta] = None
    @model_validator(mode="after")
    def fill_expires_in(self):
        access_info = AccessLevelModel.get_access_level_info(self.access_level)
        if not self.expire_delta:
            self.expire_delta = access_info.token_duration
        if not self.expire_delta:
            self.expires_at = access_info.token_expiry
        return self

# Token issue models
class TokenIssueModel(TokenAuthModel):
    access_token: str
    
class AdminTokenIssueModel(TokenIssueModel):
    access_level: AccessLevelEnum = AccessLevelEnum.ADMIN
    expire_delta: Optional[timedelta] = AccessDurationModel.ADMIN

# User info only response
class UserAuthenticationResponse(BaseModel):
    username: str
    auth_type: TokenSourceModel

# token payload model
class TokenEncodingModel(BaseModel):
    sub: str
    exp: Optional[datetime] = None
    access_level: Optional[AccessLevelEnum] = None
    auth_type: Optional[TokenSourceModel] = None