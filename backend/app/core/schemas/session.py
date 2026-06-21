from datetime import datetime

from pydantic import BaseModel


class SessionRead(BaseModel):
    session_id: str
    device: str
    browser: str
    os: str
    ip: str
    created_at: datetime
    last_active: datetime
    is_current: bool = False