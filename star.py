import asyncio


from ricezione_dati.server import start_all_servers




async def main():
    try:
        await start_all_servers()
    except KeyboardInterrupt:
        print("\n\nServer interrotto.")
    except Exception as e:
        print(f"\n\nErrore: {e}")


if __name__ == "__main__":
    asyncio.run(main())



# file da avviare per far partire tutto il centro stella, logica server in server.py

# dati in devices.json sono in locale per test, poi mettiamo gli ip veri

