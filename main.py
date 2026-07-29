from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

html_test = """
<!DOCTYPE html>
<html lang="es">
<head>
    <title>Test WebSocket Render</title>
    <style>
        body { font-family: Arial; padding: 40px; }
        #status { padding: 15px; border-radius: 5px; font-weight: bold; background: #eee; }
        .success { background: #d4edda; color: #155724; }
    </style>
</head>
<body>
    <h2>Prueba de Conexión WebSocket (Python en Render)</h2>
    <div id="status">⏳ Conectando...</div>
    <ul id="messages"></ul>

    <script>
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/ws';
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            document.getElementById('status').innerText = '✅ ¡ÉXITO! Conectado al servidor en Render.';
            document.getElementById('status').className = 'success';
            ws.send('Hola FastAPI');
        };
        ws.onmessage = (event) => {
            const li = document.createElement('li');
            li.innerText = '🤖 ' + event.data;
            document.getElementById('messages').appendChild(li);
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_test)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("¡Conexión bidireccional lista en Python!")
    while True:
        data = await websocket.receive_text()
        print(f"Recibido: {data}")
        await websocket.send_text("Recibí tu mensaje correctamente.")

# Render inyecta el puerto automáticamente
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
