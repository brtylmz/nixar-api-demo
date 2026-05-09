"""
CredentialService: Credential issuance iş mantığı.
SRP: Yalnızca kimlik bilgisi (credential) oluşturma, saklama ve sorgulama.
"""
import hashlib
import random
import logging

from nixar.nixar_api import Nixar

logger = logging.getLogger(__name__)


def _encode_attr(value: str) -> str:
    """Indy protokolünün beklediği sayısal kodlamayı üretir.
    Tam sayılar olduğu gibi, dizeler SHA-256 büyük tam sayısına dönüştürülür."""
    try:
        return str(int(value))
    except (ValueError, TypeError):
        return str(int(hashlib.sha256(str(value).encode()).hexdigest(), 16))


def _to_indy_values(values: dict) -> dict:
    """Düz dict'i Indy AttributeValues formatına çevirir:
    {"attr": "val"} → {"attr": {"raw": "val", "encoded": "<encoded>"}}
    Zaten doğru formattaysa (raw/encoded anahtar içeriyorsa) olduğu gibi döndürür."""
    if not values:
        return values
    first_val = next(iter(values.values()))
    if isinstance(first_val, dict) and "raw" in first_val:
        return values
    return {k: {"raw": str(v), "encoded": _encode_attr(str(v))} for k, v in values.items()}


class CredentialService:
    def issue_credential(
        self, issuer: Nixar, prover: Nixar, cred_def_id: str, values: dict,
    ) -> dict:
        issuer_nonce = str(random.getrandbits(80))
        indy_values = _to_indy_values(values)

        cred_offer = issuer.issuer_create_credential_offer(cred_def_id, issuer_nonce)
        cred_req = prover.prover_create_credential_request(cred_offer)

        cred_info = issuer.issuer_create_credential(cred_req, indy_values, issuer_nonce)
        cred = cred_info["credential"]

        store_cred_id = prover.prover_store_credential(None, cred, cred_req["nonce"])

        return {"store_cred_id": store_cred_id, "data": values}

    def get_credentials(self, prover: Nixar) -> list:
        return prover.prover_get_credentials()

    def get_credential(self, prover: Nixar, cred_id: str) -> dict:
        return prover.prover_get_credential(cred_id)
