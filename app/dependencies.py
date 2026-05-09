"""
Dependency Injection: FastAPI Depends() ile kullanılacak singleton fabrikaları.
DIP: Router'lar somut sınıflara değil, bu fabrika fonksiyonlarına bağımlıdır.
Tüm nesne ömürleri burada yönetilir.
"""
from app.repositories.agent_repository import AgentRepository
from app.services.agent_service import AgentService
from app.services.schema_service import SchemaService
from app.services.credential_service import CredentialService
from app.services.verification_service import VerificationService

# Singleton instances
_agent_repository = AgentRepository()
_agent_service = AgentService(_agent_repository)
_schema_service = SchemaService()
_credential_service = CredentialService()
_verification_service = VerificationService()


def get_agent_service() -> AgentService:
    return _agent_service


def get_schema_service() -> SchemaService:
    return _schema_service


def get_credential_service() -> CredentialService:
    return _credential_service


def get_verification_service() -> VerificationService:
    return _verification_service
