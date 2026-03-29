import requests
import re
from datetime import datetime

print("Buscando dados da API OpenF1...")

sessions = requests.get("https://api.openf1.org/v1/sessions?year=2026&session_type=Race").json()

if not sessions:
    print("Nenhuma sessao encontrada.")
    exit()

last = sessions[-1]
session_key = last["session_key"]
country = last.get("country_name", "---")
round_num = len(sessions)

print(f"Ultima corrida: {country} - session_key={session_key}")

drivers_raw = requests.get(f"https://api.openf1.org/v1/drivers?session_key={session_key}").json()
driver_map = {}
if isinstance(drivers_raw, list):
    for d in drivers_raw:
        if isinstance(d, dict):
            num = str(d.get("driver_number",""))
            driver_map[num] = d

positions_raw = requests.get(f"https://api.openf1.org/v1/position?session_key={session_key}").json()
final_pos = {}
if isinstance(positions_raw, list):
    for p in positions_raw:
        if isinstance(p, dict):
            num = str(p.get("driver_number",""))
            final_pos[num] = p.get("position", 99)

top3 = sorted(final_pos.items(), key=lambda x: x[1])[:3]
print(f"Top 3: {[driver_map.get(n,{}).get('last_name','#'+n) for n,_ in top3]}")

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

new_round = f"Rd {round_num} - {country}"
now = datetime.now().strftime("%d/%m/%Y")

html = re.sub(r'(<span id="updateRound">)[^<]*(</span>)', f'\\g<1>{new_round}\\g<2>', html)
html = re.sub(r'(<strong id="updateDate">)[^<]*(</strong>)', f'\\g<1>{now}\\g<2>', html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Dashboard atualizado - {new_round}")
