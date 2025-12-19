from __future__ import annotations
import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Controller API (Mock)", version="0.1")

TOKEN = os.getenv("CONTROLLER_API_TOKEN", "dev-token-please-change")

# In-memory state (lab)
STATE: Dict[str, Any] = {
    "firewall_policy": {
        "target_web_allowed_inbound_ports": [8080]
    },
    "monitoring_policy": {
        "web_latency_ms_warn": 250,
        "web_latency_ms_crit": 600,
    }
}

def require_auth(authorization: Optional[str]) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")
    token = authorization.split(" ", 1)[1].strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/health")
def health():
    return {"ok": True, "service": "controller_api"}

@app.get("/state")
def get_state(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    return STATE

class DesiredState(BaseModel):
    firewall_policy: Dict[str, Any] = Field(default_factory=dict)
    monitoring_policy: Dict[str, Any] = Field(default_factory=dict)

@app.post("/state")
def set_state(body: DesiredState, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    # simple merge update (lab)
    if body.firewall_policy:
        STATE["firewall_policy"] = body.firewall_policy
    if body.monitoring_policy:
        STATE["monitoring_policy"] = body.monitoring_policy
    return {"ok": True, "state": STATE}
