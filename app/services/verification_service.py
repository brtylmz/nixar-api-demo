"""
VerificationService: Presentation & doğrulama iş mantığı.
SRP: Yalnızca sunum (presentation) oluşturma ve doğrulama.
"""
import random
from nixar.nixar_api import Nixar


class VerificationService:
    @staticmethod
    def _build_presentation_request(schema_id: str, cred_def_id: str, attr_names: list[str]) -> dict:
        """Verilen attribute listesine göre dinamik presentation request oluşturur."""
        restrictions = [{"schema_id": schema_id}, {"cred_def_id": cred_def_id}]
        requested_attrs = {
            f"attr{i}_referent": {
                "name": name,
                "restrictions": {"$and": restrictions},
            }
            for i, name in enumerate(attr_names, 1)
        }
        return {
            "name": "IdentityPR",
            "version": "2.0",
            "nonce": str(random.getrandbits(64)),
            "requestedAttributes": requested_attrs,
            "requestedPredicates": {},
        }

    def verify(
        self, prover: Nixar, verifier: Nixar,
        schema_id: str, cred_def_id: str,
    ) -> bool:
        # Prover cüzdanındaki credential'dan attribute isimlerini al
        credentials = prover.prover_get_credentials()
        cred = next(
            (c for c in credentials if c.get("cred_def_id") == cred_def_id),
            None,
        )
        if cred is None:
            raise ValueError(f"Prover cüzdanında '{cred_def_id}' için credential bulunamadı.")

        attr_names = list(cred.get("values", {}).keys())
        pres_req = self._build_presentation_request(schema_id, cred_def_id, attr_names)
        pres = prover.prover_create_presentation(pres_req, {})
        return verifier.verifier_verify_presentation(pres_req, pres)
