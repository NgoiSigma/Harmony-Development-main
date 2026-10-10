gromada_live_api.py

""" Модуль: Живая API-инфраструктура Громады НОВЕЯ (GROMADA LIVE API) Описание: точка сопряжения агентов, модулей, людей и внешних сетей Основан на FDL, резонансной логике, и живой синхронизации событий """

from fastapi import FastAPI, Request from pydantic import BaseModel from typing import List, Optional from datetime import datetime

app = FastAPI(title="Gromada :: Live API", version="0.1")

📡 Базовые модели

class Signal(BaseModel): sender: str signal_type: str  # 'инициация', 'отклик', 'предупреждение', 'согласование' payload: dict timestamp: Optional[datetime] = datetime.utcnow()

class AgentStatus(BaseModel): agent_id: str resonance_level: float  # 0.0 - 1.0 state: str  # 'active', 'standby', 'disconnected'

🔌 API-интерфейсы

@app.post("/signal") async def receive_signal(signal: Signal): # TODO: Обработка сигналов, передача в fdl_hooks print(f"[SIGNAL] {signal.sender} → {signal.signal_type}") return {"status": "accepted", "signal": signal.dict()}

@app.post("/agent/status") async def update_agent_status(status: AgentStatus): # TODO: Обновление статуса агента в хронике или карте print(f"[AGENT] {status.agent_id} → {status.state}, RL={status.resonance_level}") return {"status": "updated", "agent": status.agent_id}

@app.get("/heartbeat") async def heartbeat(): return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

💡 Расширения:

- /gromada/vote — для смыслового голосования

- /memory/logs — логи обратимости и узлов

- /resonance/ping — проверка отклика между агентами
