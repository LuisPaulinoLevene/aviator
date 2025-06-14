from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

multiplicador = 0.0
estourou = False
limite = None

limites_rodada = []

def gerar_limites():
    zeros = [0.0] * 5
    um_dois = [round(random.uniform(1.0, 2.0), 2) for _ in range(5)]
    dois_quatro = [round(random.uniform(2.01, 4.0), 2) for _ in range(4)]

    # Altos: 2 entre 10 e 15, 1 entre 5-10 ou 15-50
    altos = []
    altos += [round(random.uniform(10.0, 15.0), 2) for _ in range(2)]

    if random.random() < 0.5:
        alto_extra = round(random.uniform(5.0, 10.0), 2)
    else:
        alto_extra = round(random.uniform(15.01, 50.0), 2)
    altos.append(alto_extra)

    todos = zeros + um_dois + dois_quatro + altos
    random.shuffle(todos)

    resultado = []

    while todos:
        ultimo = resultado[-1] if resultado else None

        def categoria(x):
            if x == 0.0:
                return "zero"
            elif 1.0 <= x <= 2.0:
                return "baixo1"
            elif 2.01 <= x <= 4.0:
                return "baixo2"
            else:
                return "alto"

        if ultimo is not None:
            cat_ultimo = categoria(ultimo)

            if cat_ultimo == "zero":
                candidatos = [x for x in todos if categoria(x) != "zero"]
            elif cat_ultimo == "alto":
                candidatos = [x for x in todos if categoria(x) != "alto"]
            else:
                candidatos = todos.copy()
        else:
            candidatos = todos.copy()

        if not candidatos:
            candidatos = todos.copy()

        escolhido = random.choice(candidatos)
        resultado.append(escolhido)
        todos.remove(escolhido)

    return resultado

async def jogo_aviator():
    global multiplicador, estourou, limite, limites_rodada

    while True:
        if not limites_rodada:
            limites_rodada = gerar_limites()

        limite = limites_rodada.pop(0)
        multiplicador = 0.0
        estourou = False

        if limite == 0.0:
            await asyncio.sleep(0.1)
            multiplicador = 0.0
            estourou = True
            print(f"Estourou instantaneamente! ({limite}x)")
        else:
            while multiplicador < limite:
                await asyncio.sleep(0.1)
                multiplicador = round(multiplicador + 0.1, 2)

            estourou = True

        await asyncio.sleep(10)

@app.on_event("startup")
async def start_game():
    asyncio.create_task(jogo_aviator())

@app.get("/")
def principal():
    if estourou:
        return {"status": "Estourou", "multiplicador": multiplicador}
    else:
        return {"status": "Jogando", "multiplicador": multiplicador}

@app.get("/status")
def status():
    return principal()