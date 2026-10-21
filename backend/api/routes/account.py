from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from api import usage
from api.config import Settings
from api.data import delete_user_everything
from api.deps import current_user, get_settings
from services.auth_service import verify_login

router = APIRouter(prefix="/me", tags=["account"])


class UsageOut(BaseModel):
    used_today: int
    limit_today: int


class DeleteIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: str = Field(min_length=1, max_length=128)


@router.get("/usage", response_model=UsageOut)
def my_usage(user: dict = Depends(current_user), settings: Settings = Depends(get_settings)):
    return UsageOut(used_today=usage.count_user_since(user["id"], 86400), limit_today=settings.ai_per_day)


@router.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_data(body: DeleteIn, response: Response, user: dict = Depends(current_user), settings: Settings = Depends(get_settings)):
    """Permanently delete the account and everything it owns. Re-checks the password first."""
    if verify_login(user["email"], body.password) is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "That password is not correct.")
    delete_user_everything(user["id"])
    response.delete_cookie(
        key=settings.cookie_name, path="/", secure=settings.cookie_secure, httponly=True, samesite=settings.cookie_samesite
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
