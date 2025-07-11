from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fast1.schemas import Message
from http import HTTPStatus

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Servidor rodando'}


@app.get('/exercicio-html', response_class=HTMLResponse)
def read_html():
    return """
    <html>
        <head>
            <title>Um olá mundo!</title>
            <body>
                <h1>Olá mundooooo! Hozier é maravilhoso</h1>
            </body>
        </head>
    </html>
"""
