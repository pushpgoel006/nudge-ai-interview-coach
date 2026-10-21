from fastapi import APIRouter, Depends, HTTPException, Response, status

from api.config import Settings
from api.deps import current_user, get_settings, owned_session
from api.schemas import SessionIn, SessionOut
from services.session_service import archive_session, create_session, list_sessions

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionOut])
def list_my_sessions(user: dict = Depends(current_user)):
    return list_sessions(user["id"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_my_session(body: SessionIn, user: dict = Depends(current_user), settings: Settings = Depends(get_settings)):
    if len(list_sessions(user["id"])) >= settings.max_sessions_per_user:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"You can keep {settings.max_sessions_per_user} prep sessions at a time. Remove one to add another.",
        )
    return create_session(user["id"], body.company_name, body.role, body.jd_text)


@router.get("/{session_id}", response_model=SessionOut)
def get_my_session(session: dict = Depends(owned_session)):
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_my_session(session: dict = Depends(owned_session), user: dict = Depends(current_user)):
    archive_session(session["id"], user["id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
