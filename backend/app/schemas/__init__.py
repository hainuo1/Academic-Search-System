"""
Pydantic 请求 / 响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ═══════════════════════════════════════════════════════
# Auth
# ═══════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)

class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: str
    question1: str
    answer1: str
    question2: str
    answer2: str

    @field_validator("username")
    @classmethod
    def check_username(cls, v):
        if len(v) < 2 or len(v) > 20:
            raise ValueError("用户名必须 2-20 个字符")
        if not re.match(r"^[a-zA-Z0-9_一-鿿]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线或中文")
        return v

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        if len(v) < 8 or len(v) > 50:
            raise ValueError("密码必须 8-50 个字符")
        if " " in v:
            raise ValueError("密码不能包含空格")
        return v

class ForgotPasswordStep1(BaseModel):
    username: str
    captcha: str
    step: str = "1"

class ForgotPasswordStep2(BaseModel):
    username: str
    step: str = "2"
    answer1: str
    answer2: str
    new_password: str
    confirm_password: str


# ═══════════════════════════════════════════════════════
# Document
# ═══════════════════════════════════════════════════════

class DocumentOut(BaseModel):
    id: int = Field(alias="document_id")
    title: str
    author: str
    abstract: str = ""
    publish_date: str = ""
    category: str = ""
    file_path: str = ""
    view_count: int = 0
    download_count: int = 0

class DocumentDetail(DocumentOut):
    keywords: list[str] = []
    citations: list[dict] = []
    citation_count: int = 0
    is_favorited: bool = False

class DocumentListOut(BaseModel):
    id: int
    title: str
    author: str
    publish_date: str = ""
    category: str = ""


# ═══════════════════════════════════════════════════════
# Profile
# ═══════════════════════════════════════════════════════

class ChangeEmailRequest(BaseModel):
    current_password: str
    new_email: str
    confirm_new_email: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

class ChangeSecurityRequest(BaseModel):
    current_password: str
    question1: str
    answer1: str
    question2: str
    answer2: str


# ═══════════════════════════════════════════════════════
# Typhoon
# ═══════════════════════════════════════════════════════

class TyphoonAIRequest(BaseModel):
    typhoon_id: str
    analysis_type: str = "trend"


# ═══════════════════════════════════════════════════════
# Earthquake
# ═══════════════════════════════════════════════════════

class EarthquakeAIRequest(BaseModel):
    event_id: str
    analysis_type: str = "trend"


# ═══════════════════════════════════════════════════════
# Tornado
# ═══════════════════════════════════════════════════════

class TornadoAIRequest(BaseModel):
    event_id: int
    analysis_type: str = "trend"


# ═══════════════════════════════════════════════════════
# Common Response wrapper
# ═══════════════════════════════════════════════════════

class ApiResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict | list] = None
