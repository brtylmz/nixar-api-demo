"""
Schema Router: Schema ve Credential Definition endpoint'leri.
SRP: Yalnızca HTTP katmanı.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import SchemaRequest, CredDefRequest
from app.services.agent_service import AgentService
from app.services.schema_service import SchemaService
from app.dependencies import get_agent_service, get_schema_service

router = APIRouter(tags=["2. Schema & CredDef"])


@router.post("/schema")
def create_schema(
    req: SchemaRequest,
    agent_svc: AgentService = Depends(get_agent_service),
    schema_svc: SchemaService = Depends(get_schema_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        schema_id = schema_svc.create_schema(issuer, req.schema_name, req.attributes)
        return {"status": "success", "schema_id": schema_id}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemas")
def get_schemas(
    agent_svc: AgentService = Depends(get_agent_service),
    schema_svc: SchemaService = Depends(get_schema_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        return {"status": "success", "schemas": schema_svc.get_schemas(issuer)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/{schema_id}")
def get_schema(
    schema_id: str,
    agent_svc: AgentService = Depends(get_agent_service),
    schema_svc: SchemaService = Depends(get_schema_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        return {"status": "success", "schema": schema_svc.get_schema(issuer, schema_id)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cred-def")
def create_cred_def(
    req: CredDefRequest,
    agent_svc: AgentService = Depends(get_agent_service),
    schema_svc: SchemaService = Depends(get_schema_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        cred_def_id = schema_svc.create_credential_definition(issuer, req.schema_id, req.is_revocable)
        return {"status": "success", "cred_def_id": cred_def_id}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cred-defs")
def get_cred_defs(
    agent_svc: AgentService = Depends(get_agent_service),
    schema_svc: SchemaService = Depends(get_schema_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        return {"status": "success", "cred_defs": schema_svc.get_credential_definitions(issuer)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cred-def/{cred_def_id}")
def get_cred_def(
    cred_def_id: str,
    agent_svc: AgentService = Depends(get_agent_service),
    schema_svc: SchemaService = Depends(get_schema_service),
):
    try:
        issuer = agent_svc.get_agent("issuer")
        return {"status": "success", "cred_def": schema_svc.get_credential_definition(issuer, cred_def_id)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
