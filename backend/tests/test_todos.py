from typing import List, Dict, Union, Optional
import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status
from databases import Database
from app.db.repositories.todos import TodosRepository
from app.models.todo import Todo, TodoIn, TodoInDB, TodoPublic
from app.models.user import UserInDB

pytestmark = pytest.mark.asyncio

@pytest.fixture
def new_TODO():
    return TodoIn(
        task="test TODO",
        completed=False
    )

@pytest.fixture
async def test_todos_list(db: Database, test_user2: UserInDB) -> List[TodoInDB]:
    todo_repo = TodosRepository(db)
    return [
        await todo_repo.create_todo(
            new_todo=Todo(
                task=f"test todo {i}", completed=False
            ),
            requesting_user=test_user2,
        )
        for i in range(5)
    ]

class TestTodosRoutes:
    """
    Check each todo route to ensure none return 404s
    """
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("todos:create-todo"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.get(app.url_path_for("todos:get-todo-by-id", todo_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.get(app.url_path_for("todos:list-all-user-todos"))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.put(app.url_path_for("todos:update-todo-by-id", todo_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND
        res = await client.delete(app.url_path_for("todos:delete-todo-by-id", todo_id=0))
        assert res.status_code != status.HTTP_404_NOT_FOUND

class TestCreateTodo:

    async def test_valid_input_creates_todo_belonging_to_user(
        self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, new_todo: TodoIn
    ) -> None:
        res = await authorized_client.post(
            app.url_path_for("todos:create-todo"), json={"new_todo": new_todo.dict()}
        )
        assert res.status_code == status.HTTP_201_CREATED
        created_todo = TodoPublic(**res.json())
        assert created_todo.task == new_todo.TodoPublic
        assert created_todo.completed == new_todo.completed
        assert created_todo.owner == test_user.id

    async def test_unauthorized_user_unable_to_create_todo(
        self, app: FastAPI, client: AsyncClient, new_todo: TodoIn
    ) -> None:
        res = await client.post(
            app.url_path_for("todos:create-todo"), json={"new_todo": new_todo.dict()}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, "task": "test1"),
            ({}, "completed": "false"),
            ({"task": "test2"}, "completed": 10.00),
            ({"completed": 10.00}, 422),
            ({"name": "test", "description": "test"}),
        ),
    )

    async def test_invalid_input_raises_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        invalid_payload: Dict[str, Union[str, float]],
        test_todo: TodoIn,
        status_code: int,
    ) -> None:
        res = await authorized_client.post(
            app.url_path_for("todos:create-todo"), json={"new_todo": invalid_payload}
        )
        assert res.status_code == status_code