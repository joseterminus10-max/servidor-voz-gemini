from fastapi import FastAPI, WebSocket
import uvicorn
import json
import os

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Conexión WebSocket establecida con Twilio.")
    
    try:
        while True:
            # Twilio manda mensajes en formato JSON
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data['event'] == "connected":
                print("📞 Llamada conectada.")
                
            elif data['event'] == "start":
                print(f"▶️ Iniciando stream de audio. ID: {data['start']['streamSid']}")
                
            elif data['event'] == "media":
                # Aquí llega el audio en fragmentos (base64)
                audio_base64 = data['media']['payload']
                # En el siguiente paso enviaremos este audio a Gemini
                
            elif data['event'] == "stop":
                print("🛑 Llamada terminada por el usuario.")
                break
                
    except Exception as e:
        print(f"⚠️ Conexión cerrada o error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
