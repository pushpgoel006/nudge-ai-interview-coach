"""Request and response shapes. Responses never include password hashes or owner ids."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _In(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RegisterIn(_In):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=60)

    @field_validator("password")
    @classmethod
    def _bcrypt_limit(cls, value: str) -> str:
        # bcrypt only uses the first 72 bytes; refuse longer ones instead of silently truncating.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes.")
        return value


class LoginIn(_In):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str


class SessionIn(_In):
    company_name: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    jd_text: str = Field(default="", max_length=20000)


class SessionOut(BaseModel):
    id: str
    company_name: str
    role: str
    jd_text: str
    status: str
    created_at: datetime | None = None


class SourceOut(BaseModel):
    file_name: str
    page: int
    doc_type: str | None = None
