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
Depois clica em Commit changes. Me fala quando fizer! 🏁feito11:45Agora vamos testar o robô manualmente pra ver se funciona!

Clica em Actions no menu do topo
No lado esquerdo vai aparecer "Atualizar Dashboard F1" — clica nele
Do lado direito aparece um botão "Run workflow" — clica nele
Clica em Run workflow verde que aparecer

Me manda um print do que aparecer! 👀11:47Deu erro mas é fácil de corrigir! Clica no "update" vermelho do lado esquerdo pra ver o log completo do erro — preciso ver qual linha falhou exatamente.
Me manda o print do que aparecer! 👀11:49Boa, consegui ver o erro! A API retornou os dados num formato diferente do esperado. Vamos corrigir o update.py.
Vai no repositório → clica em update.py → clica no lápis pra editar → apaga tudo e cola esse código novo:
pythonimport requests
import re
from datetime import datetime

print("🏎️ Buscando dados da API OpenF1...")

sessions = requests.get("https://api.openf1.org/v1/sessions?year=2026&session_type=Race").json()

if not sessions:
    print("Nenhuma sessão encontrada.")
    exit()

last = sessions[-1]
session_key = last["session_key"]
country = last.get("country_name", "—")
round_num = len(sessions)

print(f"Última corrida: {country} · session_key={session_key}")

# Busca pilotos
drivers_raw = requests.get(f"https://api.openf1.org/v1/drivers?session_key={session_key}").json()
driver_map = {}
if isinstance(drivers_raw, list):
    for d in drivers_raw:
        if isinstance(d, dict):
            num = str(d.get("driver_number",""))
            driver_map[num] = d

# Busca posições
positions_raw = requests.get(f"https://api.openf1.org/v1/position?session_key={session_key}").json()
final_pos = {}
if isinstance(positions_raw, list):
    for p in positions_raw:
        if isinstance(p, dict):
            num = str(p.get("driver_number",""))
            final_pos[num] = p.get("position", 99)

top3 = sorted(final_pos.items(), key=lambda x: x[1])[:3]
print(f"Top 3: {[driver_map.get(n,{}).get('last_name','#'+n) for n,_ in top3]}")

# Atualiza HTML
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

new_round = f"Rd {round_num} · {country}"
now = datetime.now().strftime("%d/%m/%Y")

html = re.sub(r'(<span id="updateRound">)[^<]*(</span>)', f'\\g<1>{new_round}\\g<2>', html)
html = re.sub(r'(<strong id="updateDate">)[^<]*(</strong>)', f'\\g<1>{now}\\g<2>', html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard atualizado — {new_round}")
