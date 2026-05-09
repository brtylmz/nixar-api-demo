"""
Credential Router: Credential issuance ve sorgulama endpoint'leri.
SRP: Yalnızca HTTP katmanı.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import CredentialRequest
from app.services.agent_service import AgentService
from app.services.credential_service import CredentialService
from app.dependencies import get_agent_service, get_credential_service

router = APIRouter(tags=["3. Credential"])


@router.post("/credential/issue")
def issue_credential(
    req: CredentialRequest,
    agent_svc: AgentService = Depends(get_agent_service),
    cred_svc: CredentialService = Depends(get_credential_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        prover = agent_svc.get_agent("prover")
        result = cred_svc.issue_credential(issuer, prover, req.cred_def_id, req.values)
        return {"status": "success", **result}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credentials")
def get_credentials(
    agent_svc: AgentService = Depends(get_agent_service),
    cred_svc: CredentialService = Depends(get_credential_service),
):
    try:
        prover = agent_svc.get_agent("prover")
        return {"status": "success", "credentials": cred_svc.get_credentials(prover)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credential/{cred_id}")
def get_credential(
    cred_id: str,
    agent_svc: AgentService = Depends(get_agent_service),
    cred_svc: CredentialService = Depends(get_credential_service),
):
    try:
        prover = agent_svc.get_agent("prover")
        return {"status": "success", "credential": cred_svc.get_credential(prover, cred_id)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
