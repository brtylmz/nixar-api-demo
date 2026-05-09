"""
AgentRepository: Nixar SDK ile doğrudan iletişim kuran katman.
Tek sorumluluk: Nixar kütüphanesini sarmalayarak ajan oluşturma, kayıt ve
cüzdan işlemlerini gerçekleştirmek.
DIP: Service katmanı bu repository'ye bağımlıdır, doğrudan Nixar'a değil.
"""
import json
import base64
import logging

from nixar.nixar_api import Nixar, NixarError
from app.config import settings

logger = logging.getLogger(__name__)


class AgentRepository:
    """Nixar ajanlarını oluşturma ve ledger'a kaydetme sorumluluğu."""

    def create_agent(self, name: str, role: str = None) -> Nixar:
        password_cb = lambda: settings.WALLET_PASSWORD
        try:
            return Nixar(
                name, password_cb, role, None,
                settings.WALLET_TYPE, settings.DB_HOST,
                settings.DB_USERNAME, settings.DB_PASSWORD,
            )
        except NixarError as err:
            if err.code == "AgentNotRegistered":
                logger.info(f"Agent '{name}' kayıtlı değil, trustee ile kaydediliyor...")
                trustee = self.create_trustee()
                self._register_via_trustee(trustee, err.message, name, role)
                return Nixar(
                    name, password_cb, role, None,
                    settings.WALLET_TYPE, settings.DB_HOST,
                    settings.DB_USERNAME, settings.DB_PASSWORD,
                )
            raise

    def create_trustee(self) -> Nixar:
        b64_seed = base64.b64encode(settings.TRUSTEE_SEED.encode()).decode()
        password_cb = lambda: settings.WALLET_PASSWORD
        return Nixar(
            "trustee", password_cb, "TRUSTEE", b64_seed,
            settings.WALLET_TYPE, settings.DB_HOST,
            settings.DB_USERNAME, settings.DB_PASSWORD,
        )

    @staticmethod
    def _register_via_trustee(trustee: Nixar, error_message: str, name: str, role: str = None):
        reg_info = json.loads(error_message)
        reg_info["alias"] = name
        if role:
            reg_info["role"] = role
        trustee.register_agent_to_ledger(json.dumps(reg_info))
