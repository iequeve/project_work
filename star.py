import asyncio
import websockets
import json

async def handle_receiver(websocket):
    print(f"Client connesso da: {websocket.remote_address}")
    
    try:
        async for message in websocket:
            # Decodifica il JSON ricevuto
            data = json.loads(message)
            
            # Estrae i valori per la conferma
            timestamp = data.get("timestamp", "N/A")
            numero = data.get("random_value", "N/A")
            
            print(f" Ricevuto dato: {numero} (Inviato il: {timestamp})")
            
            # Invia una risposta di conferma al client
            risposta = {"status": "ok", "message": "Dati ricevuti con successo!"}
            await websocket.send(json.dumps(risposta))
            
    except websockets.exceptions.ConnectionClosed:
        print("Il client ha chiuso la connessione.")

async def main():
    # In ascolto su tutte le interfacce (0.0.0.0) sulla porta 8765
    async with websockets.serve(handle_receiver, "localhost", 8765):
        print("Server WebSocket avviato su ws://localhost:8765")
        print("In attesa di dati...")
        await asyncio.Future()  # Mantiene il server in esecuzione per sempre

if __name__ == "__main__":
    asyncio.run(main())