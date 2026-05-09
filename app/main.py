from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import app.utils as test_utils
from nixar.nixar_api import CredDefIssuanceType
from app.utils import (
    create_schema_if_not_exist, create_credential_definition, get_timestamp_tag,
    get_presentation_request
)
from app.services.nixar_service import get_pg_wallet_agent, AGENTS, STATE

app = FastAPI(
    title="Nixar API Swagger (Dockerized & PostgreSQL)",
    description="Nixar SSID yapıları, PostgreSQL Cüzdan Entegrasyonu ile API servisi.",
    version="1.0.0"
)

# --- MODELS ---
class SchemaRequest(BaseModel):
    schema_name: str = "DockerSchema_v0.1"
    attributes: list[str] = ["name", "surname", "age", "gender"]

class CredDefRequest(BaseModel):
    schema_id: str
    is_revocable: bool = True

class CredentialRequest(BaseModel):
    cred_def_id: str
    values: dict = {"name": "Ahmet", "surname": "Yılmaz", "age": "30", "gender": "M"}

class VerificationRequest(BaseModel):
    schema_id: str
    cred_def_id: str


@app.post("/agent/initialize", tags=["1. Agent & Wallet (PostgreSQL)"])
def initialize_agents():
    try:
        # Kurum (Issuer)
        issuer = get_pg_wallet_agent("api_issuer", "ENDORSER")
        # Vatandaş (Prover) - Roller null olabilir
        prover = get_pg_wallet_agent("api_prover", None)
        # Banka (Verifier) - Doğrulayıcı olduğu için rol null ok
        verifier = get_pg_wallet_agent("api_verifier", None)
        
        AGENTS["issuer"] = issuer
        AGENTS["prover"] = prover
        AGENTS["verifier"] = verifier
        
        return {
            "status": "success", 
            "message": "Cüzdanlar PostgreSQL'e bağlandı, ajanlar ledger'da kaydoldu ve ayağa kalktı.",
            "issuer_did": issuer.get_public_did()["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schema", tags=["2. Schema & CredDef"])
def create_schema(req: SchemaRequest):
    if "issuer" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        schema_id = create_schema_if_not_exist(AGENTS["issuer"], req.schema_name, req.attributes)
        STATE["schema_id"] = schema_id
        return {"status": "success", "schema_id": schema_id}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/cred-def", tags=["2. Schema & CredDef"])
def create_cred_def(req: CredDefRequest):
    if "issuer" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        tag = get_timestamp_tag()
        cred_def_id = create_credential_definition(
            AGENTS["issuer"], req.schema_id, req.is_revocable, tag, CredDefIssuanceType.ISSUANCE_BY_DEFAULT
        )
        return {"status": "success", "cred_def_id": cred_def_id}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemas", tags=["2. Schema & CredDef"])
def get_schemas():
    if "issuer" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        schemas = AGENTS["issuer"].issuer_get_schemas()
        return {"status": "success", "schemas": schemas}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema/{schema_id}", tags=["2. Schema & CredDef"])
def get_schema(schema_id: str):
    if "issuer" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        schema_data = AGENTS["issuer"].issuer_get_schema(schema_id)
        return {"status": "success", "schema": schema_data}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/cred-defs", tags=["2. Schema & CredDef"])
def get_cred_defs():
    if "issuer" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        cred_defs = AGENTS["issuer"].issuer_get_credential_definitions()
        return {"status": "success", "cred_defs": cred_defs}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/cred-def/{cred_def_id}", tags=["2. Schema & CredDef"])
def get_cred_def(cred_def_id: str):
    if "issuer" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        cred_def = AGENTS["issuer"].issuer_get_credential_definition(cred_def_id)
        return {"status": "success", "cred_def": cred_def}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/credential/issue", tags=["3. Issuance & Verification"])
def issue_credential(req: CredentialRequest):
    if "issuer" not in AGENTS or "prover" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        issuer, prover = AGENTS["issuer"], AGENTS["prover"]
        issuer_nonce = str(random.getrandbits(80))
        
        cred_offer = issuer.issuer_create_credential_offer(req.cred_def_id, issuer_nonce)
        cred_req = prover.prover_create_credential_request(cred_offer)
        
        cred_info = issuer.issuer_create_credential(cred_req, req.values, issuer_nonce)
        cred = cred_info["credential"]
        
        store_cred_id = prover.prover_store_credential(None, cred, cred_req['nonce'])
        
        return {"status": "success", "store_cred_id": store_cred_id, "data": req.values}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/credentials", tags=["3. Issuance & Verification"])
def get_credentials():
    if "prover" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        creds = AGENTS["prover"].prover_get_credentials()
        return {"status": "success", "credentials": creds}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/credential/{cred_id}", tags=["3. Issuance & Verification"])
def get_credential(cred_id: str):
    if "prover" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        cred = AGENTS["prover"].prover_get_credential(cred_id)
        return {"status": "success", "credential": cred}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/verification/verify", tags=["3. Issuance & Verification"])
def verify_credential(req: VerificationRequest):
    if "prover" not in AGENTS or "verifier" not in AGENTS: raise HTTPException(status_code=400, detail="Önce ajanları başlatın")
    try:
        prover, verifier = AGENTS["prover"], AGENTS["verifier"]
        
        pres_req = get_presentation_request(req.schema_id, req.cred_def_id)
        pres = prover.prover_create_presentation(pres_req, {"self_attested_referent": "self-test"})
        v_result = verifier.verifier_verify_presentation(pres_req, pres)
        
        return {"status": "success", "is_valid": v_result}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
