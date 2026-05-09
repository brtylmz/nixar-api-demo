"""
Agent Router: Ajan başlatma endpoint'i.
SRP: Yalnızca HTTP request/response dönüşümü — iş mantığı service'de.
DIP: AgentService'e Depends() ile bağımlı.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.services.agent_service import AgentService
from app.dependencies import get_agent_service

router = APIRouter(prefix="/agent", tags=["1. Agent & Wallet (PostgreSQL)"])


@router.post("/initialize")
def initialize_agents(service: AgentService = Depends(get_agent_service)):
    try:
        return service.initialize_agents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
