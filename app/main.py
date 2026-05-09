import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import agent, schema, credential, verification

app = FastAPI(
    title="Nixar SSI API",
    description="Nixar Self-Sovereign Identity API — PostgreSQL Wallet & Hyperledger Indy Ledger",
    version="1.0.0",
)

app.include_router(agent.router)
app.include_router(schema.router)
app.include_router(credential.router)
app.include_router(verification.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

