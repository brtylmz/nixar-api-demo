"""
Verification Router: Doğrulama endpoint'i.
SRP: Yalnızca HTTP katmanı.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import VerificationRequest
from app.services.agent_service import AgentService
from app.services.verification_service import VerificationService
from app.dependencies import get_agent_service, get_verification_service

router = APIRouter(tags=["4. Verification"])


@router.post("/verification/verify")
def verify_credential(
    req: VerificationRequest,
    agent_svc: AgentService = Depends(get_agent_service),
    ver_svc: VerificationService = Depends(get_verification_service),
):
    try:
        prover = agent_svc.get_agent("prover")
        verifier = agent_svc.get_agent("verifier")
        is_valid = ver_svc.verify(prover, verifier, req.schema_id, req.cred_def_id)
        return {"status": "success", "is_valid": is_valid}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
