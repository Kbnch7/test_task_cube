import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.data.models import Task
from app.data.session import get_db
from app.main import app
from app.services.utils.exceptions import TaskAlreadyDoneError, TaskNotFoundError


async def override_get_db():
    yield AsyncMock()

app.dependency_overrides[get_db] = override_get_db

USER_ID = uuid.uuid4()
TASK_ID = uuid.uuid4()

def get_mock_task() -> Task:
    return Task(
        id=TASK_ID,
        title="test task",
        description="test description",
        user_id=USER_ID,
        status="todo",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.create.tasks_service.create", new_callable=AsyncMock)
async def test_create_task(mock_create, async_client):
    mock_create.return_value = get_mock_task()

    payload = {
        "title": "test task",
        "description": "test description",
        "user_id": str(USER_ID)
    }

    response = await async_client.post("/api/v1/tasks/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["id"] == str(TASK_ID)
    assert data["status"] == "todo"
    mock_create.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.read.tasks_service.read_all", new_callable=AsyncMock)
async def test_get_tasks(mock_read_all, async_client):
    mock_read_all.return_value = [get_mock_task()]

    response = await async_client.get("/api/v1/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(TASK_ID)
    mock_read_all.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.read.tasks_service.read", new_callable=AsyncMock)
async def test_get_task_success(mock_read, async_client):
    mock_read.return_value = get_mock_task()

    response = await async_client.get(f"/api/v1/tasks/{TASK_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(TASK_ID)
    mock_read.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.read.tasks_service.read", new_callable=AsyncMock)
async def test_get_task_not_found(mock_read, async_client):
    mock_read.side_effect = TaskNotFoundError()

    response = await async_client.get(f"/api/v1/tasks/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    mock_read.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.update.tasks_service.update", new_callable=AsyncMock)
async def test_update_task_success(mock_update, async_client):
    updated_task = get_mock_task()
    updated_task.status = "in_progress"
    mock_update.return_value = updated_task

    payload = {"status": "in_progress"}
    response = await async_client.patch(f"/api/v1/tasks/{TASK_ID}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    mock_update.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.update.tasks_service.update", new_callable=AsyncMock)
async def test_update_task_validation_error(mock_update, async_client):
    payload = {"status": "invalid_status"}
    response = await async_client.patch(f"/api/v1/tasks/{TASK_ID}", json=payload)

    assert response.status_code == 422
    mock_update.assert_not_called()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.update.tasks_service.update", new_callable=AsyncMock)
async def test_update_task_already_done(mock_update, async_client):
    mock_update.side_effect = TaskAlreadyDoneError()

    payload = {"status": "in_progress"}
    response = await async_client.patch(f"/api/v1/tasks/{TASK_ID}", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Task already done"
    mock_update.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.delete.tasks_service.delete", new_callable=AsyncMock)
async def test_delete_task_success(mock_delete, async_client):
    mock_delete.return_value = None

    response = await async_client.delete(f"/api/v1/tasks/{TASK_ID}")

    assert response.status_code == 204
    mock_delete.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.tasks.delete.tasks_service.delete", new_callable=AsyncMock)
async def test_delete_task_not_found(mock_delete, async_client):
    mock_delete.side_effect = TaskNotFoundError()

    response = await async_client.delete(f"/api/v1/tasks/{TASK_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
