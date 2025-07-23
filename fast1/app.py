from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from fast1 import database
from fast1.routers import auth, users
from fast1.schemas import Message
from fast1.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa na inicialização da aplicação
    settings = Settings()
    # Cria e atribui o engine à variável no módulo database
    database.engine = create_async_engine(settings.DATABASE_URL)

    print("Engine do banco de dados criado.")
    yield
    # Executa no desligamento da aplicação
    await database.engine.dispose()
    print("Engine do banco de dados descartado.")


app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Servidor rodando'}
