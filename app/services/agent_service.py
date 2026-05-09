"""
AgentService: Ajan yaşam döngüsü yönetimi.
SRP: Yalnızca ajanların başlatılması ve erişilmesi.
DIP: AgentRepository'ye bağımlı, doğrudan Nixar'a değil.
"""
import logging
from app.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, agent_repository: AgentRepository):
        self._repo = agent_repository
        self._agents: dict = {}

    @property
    def agents(self) -> dict:
        return self._agents

    def get_agent(self, key: str):
        agent = self._agents.get(key)
        if agent is None:
            raise RuntimeError("Önce ajanları başlatın (/agent/initialize)")
        return agent

    def initialize_agents(self) -> dict:
        issuer = self._repo.create_agent("api_issuer", "ENDORSER")
        prover = self._repo.create_agent("api_prover", None)
        verifier = self._repo.create_agent("api_verifier", None)

        self._agents["issuer"] = issuer
        self._agents["prover"] = prover
        self._agents["verifier"] = verifier

        return {
            "status": "success",
            "message": "Cüzdanlar PostgreSQL'e bağlandı, ajanlar ledger'da kaydoldu.",
            "issuer_did": issuer.get_public_did()["id"],
        }
