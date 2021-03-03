from typing import List
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.todo import Todo, TodoIn, TodoInDB, TodoPublic
from app.models.user import UserInDB

CREATE_TODO_QUERY = """
    INSERT INTO todos (task, completed, owner)
    VALUES (:task, :completed)
    RETURNING id, task, completed, owner, created_at, updated_at;
"""

GET_TODO_BY_ID_QUERY = """
    SELECT id, task, completed, owner, created_at, updated_at
    FROM todos
    WHERE id = :id;
"""

GET_ALL_TODOS_QUERY = """
    SELECT id, task, completed
    FROM todos;  
"""

UPDATE_TODO_BY_ID_QUERY = """
    UPDATE todos  
    SET task         = :task,  
        completed  = :completed
    WHERE id = :id AND owner = :owner
    RETURNING id, task, completed, owner, created_at, updated_at;
"""

DELETE_TODO_BY_ID_QUERY = """
    DELETE FROM todos  
    WHERE id = :id AND owner = :owner
    RETURNING id;  
""" 

LIST_ALL_USER_TODOS_QUERY = """
    SELECT id, task, completed, owner, created_at, updated_at
    FROM todos
    WHERE owner = :owner;
"""


class TodosRepository(BaseRepository):
    """"
    All database actions associated with the Todo resource
    """
    async def create_todo(self, *, new_todo: TodoIn, requesting_user: UserInDB) -> TodoInDB:
        todo = await self.db.fetch_one(query=CREATE_TODO_QUERY, values={**new_todo.dict(), "owner": requesting_user.id})
        return TodoInDB(**todo)

    async def get_todo_by_id(self, *, id: int, requesting_user: UserInDB) -> TodoInDB:
        todo = await self.db.fetch_one(query=GET_TODO_BY_ID_QUERY, values={"id": id})
        if not todo:
            return None
        return TodoInDB(**todo)

    async def get_all_todos(self) -> List[Todo]:
        todos = await self.db.fetch_all(query=GET_ALL_TODOS_QUERY)
        return [Todo(**l) for l in todos]

    async def list_all_user_todos(self, requesting_user: UserInDB) -> List[TodoInDB]:
        todos_list = await self.db.fetch_all(
            query=LIST_ALL_USER_TODOS_QUERY, values={"owner": requesting_user.id}
        )
        return [TodoInDB(**l) for l in todos_list]

    async def update_todo(
        self, *, id: int, todo_update: Todo, requesting_user: UserInDB
    ) -> TodoInDB:
        todo = await self.get_todo_by_id(id=id, requesting_user=requesting_user)
        if not todo:
            return None
        if todo.owner != requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users are only able to update todos that they created.",
            )
        todo_update_params = todo.copy(update=todo_update.dict(exclude_unset=True))
        if todo_update_params.completed is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid completed checkbox. Cannot be None."
            )
        updated_todo = await self.db.fetch_one(
            query=UPDATE_TODO_BY_ID_QUERY,
            values={
                **todo_update_params.dict(exclude={"created_at", "updated_at"}),
                "owner": requesting_user.id,
            },
        )
        return TodoInDB(**updated_todo)


    async def delete_todo_by_id(self, *, id: int, requesting_user: UserInDB) -> int:
        todo = await self.get_todo_by_id(id=id, requesting_user=requesting_user)
        if not todo:
            return None
        if todo.owner != requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users are only able to delete todos that they created.",
            )
        deleted_id = await self.db.execute(query=DELETE_TODO_BY_ID_QUERY, values={"id": id, "owner": requesting_user.id})
        return deleted_id

