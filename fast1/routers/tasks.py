from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fast1.database import get_session

router = APIRouter(prefix='/tasks', tags=['tasks'])


Session_DB = Annotated[AsyncSession, Depends(get_session)]

# @router.post('/', response_model=TasksRead)
# async def create_task(task: TasksCreate, session: Session_DB):
