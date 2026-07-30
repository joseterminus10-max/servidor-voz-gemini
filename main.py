import os
import json
import base64
import asyncio
import audioop
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response, HTMLResponse
import uvicorn

app = FastAPI()

# Leemos tu llave secreta de Google desde la caja fuerte de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_WS_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"

@app.get("/")
async def inicio():
    return HTMLResponse("🚀 Servidor de Voz Activo (Twilio + Gemini)")

@app.post("/llamada")
@app.get("/llamada")
async def contestar_llamada(request: Request):
    host = request.url.hostname
    twiml = f'Conectando con inteligencia artificial.'
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/ws")
async def websocket_endpoint(twilio_ws: WebSocket):
    await twilio_ws.accept()
    print("✅ Conexión con Twilio establecida.")

    # Conectamos con el cerebro de Gemini Multimodal Live
    async with websockets.connect(GEMINI_WS_URL) as gemini_ws:
        print("🧠 Conectado a Gemini.")
        
        # 1. Configuración de personalidad y voz
        setup_msg = {
            "setup": {
                "model": "models/gemini-2.0-flash-exp",
                "systemInstruction": {
                    "parts": [{"text": "Eres un asistente telefónico amable. Responde siempre en español, de forma muy concisa, como en una charla telefónica real. No uses formatos de texto."}]
                },
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": "Aoede" # Voz clara y neutral
                            }
                        }
                    }
                }
            }
        }
        await gemini_ws.send(json.dumps(setup_msg))
        await gemini_ws.recv() # Confirmación de Gemini
        
        stream_sid = None

        # 2. Tarea: Escuchar a Twilio y traducir el audio a Gemini
        async def twilio_to_gemini():
            nonlocal stream_sid
            try:
                while True:
                    msg = await twilio_ws.receive_text()
                    data = json.loads(msg)
                    
                    if data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print("▶️ La persona empezó a hablar.")
                        
                    elif data['event'] == 'media':
                        # Extraer audio telefónico y convertir a 16kHz
                        audio_data = base64.b64decode(data['media']['payload'])
                        pcm_data = audioop.ulaw2lin(audio_data, 2)
                        pcm_16khz, _ = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)
                        
                        # Enviar audio a Gemini
                        gemini_msg = {
                            "realtimeInput": {
                                "mediaChunks": [{
                                    "mimeType": "audio/pcm;rate=16000",
                                    "data": base64.b64encode(pcm_16khz).decode("utf-8")
                                }]
                            }
                        }
                        await gemini_ws.send(json.dumps(gemini_msg))
                        
                    elif data['event'] == 'stop':
                        print("🛑 El usuario colgó la llamada.")
                        break
            except Exception as e:
                print(f"Fin de audio Twilio: {e}")

        # 3. Tarea: Escuchar a Gemini y traducir el audio al Teléfono (Twilio)
        async def gemini_to_twilio():
            try:
                while True:
                    msg = await gemini_ws.recv()
                    response = json.loads(msg)
                    
                    if "serverContent" in response:
                        model_turn = response["serverContent"].get("modelTurn")
                        if model_turn:
                            for part in model_turn["parts"]:
                                if "inlineData" in part:
                                    # Extraer audio de Gemini y convertir a calidad telefónica (8kHz)
                                    audio_b64 = part["inlineData"]["data"]
                                    pcm_audio = base64.b64decode(audio_b64)
                                    pcm_8khz, _ = audioop.ratecv(pcm_audio, 2, 1, 24000, 8000, None)
                                    mulaw_audio = audioop.lin2ulaw(pcm_8khz, 2)
                                    
                                    # Enviar por el auricular del teléfono
                                    if stream_sid:
                                        twilio_msg = {
                                            "event": "media",
                                            "streamSid": stream_sid,
                                            "media": {
                                                "payload": base64.b64encode(mulaw_audio).decode("utf-8")
                                            }
                                        }
                                        await twilio_ws.send_text(json.dumps(twilio_msg))
            except Exception as e:
                print(f"Fin de respuesta Gemini: {e}")

        # Ejecutar ambos canales de audio simultáneamente
        await asyncio.gather(twilio_to_gemini(), gemini_to_twilio())
