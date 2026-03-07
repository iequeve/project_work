import asyncio

from ricezione_dati.server import start_all_servers


# file da avviare per far partire tutto il centro stella, logica server in server.py

# dati in devices.json sono in locale per test, poi mettiamo gli ip veri

async def main():
    await start_all_servers()


async def stop():
    print("\n\nArresto del centro stella in corso\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(stop())
    except Exception as e:
        print(f"\n\nErrore: {e}")