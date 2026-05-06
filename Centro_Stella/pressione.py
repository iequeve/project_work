import requests
import json

# Configurazione Master
IP_MASTER = "192.168.4.10"
URL = f"http://{IP_MASTER}/"

def hex_to_signed_int(hex_str):
    """Converte stringa hex a 16-bit signed integer (Big Endian)."""
    return int.from_bytes(bytes.fromhex(hex_str), byteorder='big', signed=True)

def get_iolink_data(port_number):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "code": "request",
        "cid": 1,
        "adr": f"/iolinkmaster/port[{port_number}]/iolinkdevice/pdin/getdata",
        "data": None
    }
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- FUNZIONI DI DECODIFICA ---

def decode_port_1(hex_val):
    """Porta 1: SFAH Flow (14-bit + Offset -10)."""
    raw_int = int(hex_val, 16)
    word_0 = (raw_int >> ((len(hex_val)-4)*4)) & 0xFFFF
    flow_raw = word_0 & 0x3FFF
    flow_real = (flow_raw * 0.001220777635) - 10
    word_2 = raw_int & 0xFF
    return {
        "Tipo": "Flusso (SFAH)",
        "Flusso": round(flow_real, 3), "Unità": "L/min",
        "Digitali": {"OUTA": bool(word_2 & 0x01), "OUTB": bool(word_2 & 0x02), "Puls": bool(word_2 & 0x04)}
    }

def decode_port_2(hex_val):
    """Porta 2: Pressione (14-bit in Word 0)."""
    word_0 = int(hex_val[0:4], 16)
    press_raw = (word_0 >> 2) & 0x3FFF
    press_real = press_raw * 0.000610388818
    return {
        "Tipo": "Pressione",
        "Valore": round(press_real, 4), "Unità": "bar",
        "Digitali": {"OUTA": bool(word_0 & 0x01), "OUTB": bool(word_0 & 0x02)}
    }

def decode_port_3(hex_val):
    """Porta 3: Flusso + Temp (Gradiente 0.0166)."""
    f_raw = hex_to_signed_int(hex_val[0:4])
    t_raw = hex_to_signed_int(hex_val[8:12])
    w2 = int(hex_val[4:8], 16)
    return {
        "Tipo": "Flusso/Temp",
        "Flusso": round(f_raw * 0.01666666667, 3) if f_raw <= 32000 else "Error",
        "Temp": round(t_raw * 0.1, 1) if t_raw <= 32000 else "Error",
        "Digitali": {"Flow_OUTA": bool(w2 & 0x01), "Flow_Puls": bool(w2 & 0x04)}
    }

def decode_port_4(hex_val):
    """Porta 4: Flusso + Temp (Gradiente 0.00166)."""
    f_raw = hex_to_signed_int(hex_val[0:4])
    t_raw = hex_to_signed_int(hex_val[8:12])
    w2 = int(hex_val[4:8], 16)
    w6 = int(hex_val[12:16], 16)
    return {
        "Tipo": "Flusso/Temp (P4)",
        "Flusso": round(f_raw * 0.001666666667, 3) if f_raw <= 32000 else "Error",
        "Temp": round(t_raw * 0.1, 1) if t_raw <= 32000 else "Error",
        "Digitali": {"Flow_OUTA": bool(w2 & 0x01), "Temp_OUTA": bool(w6 & 0x01)}
    }

# --- MAIN LOOP ---

def main():
    funzioni = {1: decode_port_1, 2: decode_port_2, 3: decode_port_3, 4: decode_port_4}
    report = {}

    print(f"Richiesta dati a ifm AL1350 ({IP_MASTER})...\n")

    for p_id, func in funzioni.items():
        res = get_iolink_data(p_id)
        if res.get("code") == 200:
            hex_data = res["data"]["value"]
            report[f"Porta_{p_id}"] = func(hex_data)
        else:
            report[f"Porta_{p_id}"] = f"Errore {res.get('code')} (Sensore non presente?)"

    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()