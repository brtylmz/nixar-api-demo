from pydantic import BaseModel, field_validator


class SchemaRequest(BaseModel):
    schema_name: str = "DockerSchema_v0.1"
    attributes: list[str] = ["name", "surname", "age", "gender"]


class CredDefRequest(BaseModel):
    schema_id: str
    is_revocable: bool = True

    @field_validator("schema_id")
    @classmethod
    def schema_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("schema_id boş olamaz. Önce schema oluşturun.")
        return v


class CredentialRequest(BaseModel):
    cred_def_id: str
    values: dict = {"name": "Ahmet", "surname": "Yılmaz", "age": "30", "gender": "M"}

    @field_validator("cred_def_id")
    @classmethod
    def cred_def_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("cred_def_id boş olamaz. Önce credential definition oluşturun.")
        return v


class VerificationRequest(BaseModel):
    schema_id: str
    cred_def_id: str

    @field_validator("schema_id", "cred_def_id")
    @classmethod
    def ids_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("schema_id ve cred_def_id boş olamaz.")
        return v
