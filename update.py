
import requests
import json
import re
from datetime import datetime

print("🏎️ Buscando dados da API OpenF1...")

# Busca sessões de 2026
sessions = requests.get("https://api.openf1.org/v1/sessions?year=2026&session_type=Race").json()

if not sessions:
    print("Nenhuma sessão encontrada, encerrando.")
    exit()

last = sessions[-1]
session_key = last["session_key"]
country = last.get("country_name", "—")
date = last.get("date_start", "")[:10]

print(f"Última corrida: {country} · {date} · session_key={session_key}")

# Busca pilotos
drivers = requests.get(f"https://api.openf1.org/v1/drivers?session_key={session_key}").json()
driver_map = {str(d["driver_number"]): d for d in drivers}

# Busca posições finais
positions = requests.get(f"https://api.openf1.org/v1/position?session_key={session_key}").json()

# Pega última posição de cada piloto
final_pos = {}
for p in positions:
    num = str(p["driver_number"])
    final_pos[num] = p["position"]

# Monta top 3
top3 = sorted(final_pos.items(), key=lambda x: x[1])[:3]
podium = []
for num, pos in top3:
    d = driver_map.get(num, {})
    podium.append({
        "driver": d.get("last_name", f"#{num}"),
        "team": (d.get("team_name") or "—").replace("Formula 1 Team", "").strip(),
        "pos": pos
    })

print(f"Pódio: {[p['driver'] for p in podium]}")

# Atualiza o updateRound no HTML
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

round_num = len(sessions)
new_round = f"Rd {round_num} · {country}"
html = re.sub(r'(<span id="updateRound">)[^<]*(</span>)', f'\\g<1>{new_round}\\g<2>', html)

now = datetime.now().strftime("%d/%m/%Y %H:%M")
html = re.sub(r'(<strong id="updateDate">)[^<]*(</strong>)', f'\\g<1>Atualizado {now}\\g<2>', html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard atualizado — {new_round}")
