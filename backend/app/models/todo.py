from typing import Optional
from enum import Enum
from app.models.core import IDModelMixin, CoreModel
from pydantic import BaseModel

from typing import Optional, Union
from enum import Enum
from app.models.core import IDModelMixin, DateTimeModelMixin, CoreModel
from app.models.user import UserPublic


# used as payload to Create or Update note endpoints
class TodoIn(BaseModel):
    task: str
    completed: bool

# used as response to retrieve notes collection or a single note given its id
class Todo(BaseModel):
    id: int
    task: str
    completed: bool

class TodoInDB(IDModelMixin, DateTimeModelMixin, BaseModel):
    id: int
    task: str
    completed: bool
    owner: Union[int, UserPublic]
    
class TodoPublic(TodoInDB):
    pass
