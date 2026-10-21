from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from api.config import Settings
from api.deps import current_user, get_settings
from api.ratelimit import client_ip, login_by_email, login_by_ip, register_by_ip, too_many
from api.schemas import LoginIn, RegisterIn, UserOut
from api.security import create_token
from services.auth_service import register_user, verify_login

router = APIRouter(prefix="/auth", tags=["auth"])


def _start_login(response: Response, user: dict, settings: Settings) -> None:
    response.set_cookie(
        key=settings.cookie_name,
        value=create_token(user["id"], settings.secret_key, settings.session_ttl_seconds),
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


def _public(user: dict) -> UserOut:
    return UserOut(id=user["id"], email=user["email"], display_name=user["display_name"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, request: Request, response: Response, settings: Settings = Depends(get_settings)):
    if not register_by_ip.allow(client_ip(request)):
        raise too_many(3600)
    try:
        user = register_user(body.email, body.password, body.display_name)
    except ValueError as error:
        message = str(error)
        code = status.HTTP_409_CONFLICT if "already exists" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(code, message) from error
    _start_login(response, user, settings)
    return _public(user)


@router.post("/login", response_model=UserOut)
def login(body: LoginIn, request: Request, response: Response, settings: Settings = Depends(get_settings)):
    if not login_by_ip.allow(client_ip(request)) or not login_by_email.allow(body.email.strip().lower()):
        raise too_many(600)
    user = verify_login(body.email, body.password)
    if user is None:
        # One message for "no such account" and "wrong password".
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")
    _start_login(response, user, settings)
    return _public(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, settings: Settings = Depends(get_settings)):
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(current_user)):
    return _public(user)
