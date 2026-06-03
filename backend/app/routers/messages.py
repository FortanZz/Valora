from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user_id
from app.database import (
    create_property_message,
    get_message_by_id,
    get_property_by_id,
    get_received_messages,
    get_sent_messages,
    get_user_by_id,
    mark_message_read,
)
from app.schemas.message import MessageCreate, MessageResponse

router = APIRouter(prefix="/api/messages", tags=["messages"])


def _validate_user_exists(user_id: int) -> None:
    if get_user_by_id(user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreate,
    current_user_id: int = Depends(get_current_user_id),
) -> MessageResponse:
    _validate_user_exists(current_user_id)
    property_item = get_property_by_id(payload.property_id)
    if property_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    if property_item["owner_id"] == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send a message to yourself",
        )

    message = create_property_message(
        sender_id=current_user_id,
        property_id=payload.property_id,
        body=payload.body.strip(),
        created_at=datetime.utcnow(),
    )
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return MessageResponse(**message)


@router.get("/inbox", response_model=List[MessageResponse])
def list_inbox(
    current_user_id: int = Depends(get_current_user_id),
) -> List[MessageResponse]:
    _validate_user_exists(current_user_id)
    return [
        MessageResponse(**message)
        for message in get_received_messages(current_user_id)
    ]


@router.get("/sent", response_model=List[MessageResponse])
def list_sent(
    current_user_id: int = Depends(get_current_user_id),
) -> List[MessageResponse]:
    _validate_user_exists(current_user_id)
    return [
        MessageResponse(**message)
        for message in get_sent_messages(current_user_id)
    ]


@router.put("/{message_id}/read", response_model=MessageResponse)
def mark_read(
    message_id: int,
    current_user_id: int = Depends(get_current_user_id),
) -> MessageResponse:
    _validate_user_exists(current_user_id)
    message = get_message_by_id(message_id)
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    if message["recipient_id"] != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the message recipient can mark it as read",
        )

    updated = mark_message_read(message_id, datetime.utcnow())
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    return MessageResponse(**updated)
