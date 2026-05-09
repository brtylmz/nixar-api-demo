"""
SchemaService: Schema ve Credential Definition iş mantığı.
SRP: Yalnızca şema oluşturma, sorgulama ve cred-def yönetimi.
"""
import logging
from datetime import datetime

from nixar.nixar_api import Nixar, CredDefIssuanceType
from app.config import settings

logger = logging.getLogger(__name__)


class SchemaService:
    def create_schema(self, issuer: Nixar, schema_name: str, attributes: list[str]) -> str:
        schemas = issuer.issuer_get_schemas()
        for schema in schemas:
            if schema["name"] == schema_name:
                return schema["id"]
        # ZMQ pool bağlantısı boşta kalınca donabiliyor; ledger write öncesi yeniliyoruz.
        issuer.reconnect()
        schema_id = issuer.issuer_create_schema(schema_name, attributes, "2.0")
        logger.info(f"Schema created: {schema_id}")
        return schema_id

    def get_schemas(self, issuer: Nixar) -> list:
        return issuer.issuer_get_schemas()

    def get_schema(self, issuer: Nixar, schema_id: str) -> dict:
        return issuer.issuer_get_schema(schema_id)

    def create_credential_definition(
        self, issuer: Nixar, schema_id: str, is_revocable: bool,
    ) -> str:
        tag = datetime.now().strftime("%Y%m%d%H%M")
        # ZMQ pool bağlantısı boşta kalınca donabiliyor; ledger write öncesi yeniliyoruz.
        issuer.reconnect()
        cred_def_id = issuer.issuer_create_credential_definition(
            schema_id, is_revocable, tag,
            CredDefIssuanceType.ISSUANCE_BY_DEFAULT,
            settings.MAX_CRED_NUM,
        )
        logger.info(f"CredDef created: {cred_def_id}")
        return cred_def_id

    def get_credential_definitions(self, issuer: Nixar) -> list:
        return issuer.issuer_get_credential_definitions()

    def get_credential_definition(self, issuer: Nixar, cred_def_id: str) -> dict:
        return issuer.issuer_get_credential_definition(cred_def_id)
