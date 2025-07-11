from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get('/')
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
