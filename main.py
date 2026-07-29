from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response, HTMLResponse
import uvicorn
import json
import os

app = FastAPI()

# 1. Pantalla de inicio para comprobar que funciona
@app.get("/")
async def inicio():
    return HTMLResponse("🚀 Servidor de Voz Activo (Twilio + Gemini)")

# 2. La "recepcionista" que le da instrucciones a Twilio
@app.post("/llamada")
@app.get("/llamada")
async def contestar_llamada(request: Request):
    host = request.url.hostname
    # Generamos el XML (TwiML) que Twilio necesita
    twiml = f"""
    
        Conectando con inteligencia artificial.
        
            
        
    """
    return Response(content=twiml, media_type="application/xml")

# 3. El túnel de WebSockets para el audio en tiempo real
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Conexión WebSocket establecida con Twilio.")
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data['event'] == "connected":
                print("📞 Llamada conectada.")
            elif data['event'] == "start":
                print("▶️ Iniciando stream de audio.")
            elif data['event'] == "stop":
                print("🛑 Llamada terminada por el usuario.")
                break
    except Exception as e:
        print(f"⚠️ Conexión cerrada o error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
