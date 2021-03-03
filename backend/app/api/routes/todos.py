from typing import List
from fastapi import APIRouter, Body, Path, Depends, HTTPException, status

from app.models.user import UserCreate, UserUpdate, UserInDB, UserPublic
from app.models.todo import Todo, TodoIn, TodoInDB, TodoPublic
from app.db.repositories.todos import TodosRepository
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Todo], name="todos:get-all-todos")
async def get_all_todos(
    todos_repo: TodosRepository = Depends(get_repository(TodosRepository)),
) -> List[Todo]:
    return await todos_repo.get_all_todos()

@router.get("/{todo_id}/", response_model=TodoPublic, name="todos:get-todo-by-id")
async def get_todo_by_id(
    todo_id: int = Path(..., ge=1),
    current_user: UserInDB = Depends(get_current_active_user),
    todos_repo: TodosRepository = Depends(get_repository(TodosRepository)),
) -> TodoPublic:
    todo = await todos_repo.get_todo_by_id(id=todo_id, requesting_user=current_user)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo found with that id.")
    return todo



# Make FastAPI expect JSON with key 'new_todo' that contains the model contents by
# using special `Body` parameter `embed` in the parameter default
@router.post("/", response_model=TodoPublic, name="todos:create-todo", status_code = status.HTTP_201_CREATED)
async def create_todo(
    new_todo: TodoIn = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    todos_repo: TodosRepository = Depends(get_repository(TodosRepository)),
) -> TodoPublic:
    created_todo = await todos_repo.create_todo(new_todo=new_todo, requesting_user=current_user)
    return created_todo

@router.put("/{todo_id}/", response_model=TodoPublic, name="todos:update-todo-by-id")
async def update_todo_by_id(
    todo_id: int = Path(..., ge=1, title="The ID of the todo to update."),
    current_user: UserInDB = Depends(get_current_active_user),
    todo_update: Todo = Body(..., embed=True),
    todos_repo: TodosRepository = Depends(get_repository(TodosRepository)),
) -> TodoPublic:
    updated_todo = await todos_repo.update_todo(todo_id=id, todo_update=todo_update, requesting_user=current_user)
    if not updated_todo:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No todo found with that id.")
    return updated_todo


@router.delete("/{todo_id}/", response_model=int, name="todos:delete-todo-by-id")
async def delete_todo_by_id(
    todo_id: int = Path(..., ge=1, title="The ID of the todo to delete."),
    current_user: UserInDB = Depends(get_current_active_user),
    todos_repo: TodosRepository = Depends(get_repository(TodosRepository)),
) -> int:
    deleted_id = await todos_repo.delete_todo_by_id(todo_id=id, requesting_user=current_user)
    if not deleted_id:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No todo found with that id.")
    return deleted_id

