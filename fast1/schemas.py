from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fast1.models import TaskState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UsersList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str  # bearer


class FilterPage(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


class TasksRead(BaseModel):
    id: int
    name: str
    description: str
    state: TaskState


class TasksCreate(BaseModel):
    name: str
    description: str
    state: TaskState


class TaskList(BaseModel):
    tasks: list[TasksRead]


class TaskFilter(FilterPage):
    name: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    state: TaskState | None = None
