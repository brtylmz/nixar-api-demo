import os
import json
import base64
from nixar.nixar_api import Nixar, NixarError

# Çevresel Değişkenler (Docker içinden veya lokalden ezilebilir)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Global Ajan Referanslarını tutacak memory (Gelişmiş mimarilerde Redis vb kullanılabilir)
AGENTS = {}
STATE = {}

def get_pg_wallet_agent(name: str, role: str = None):
    """
    Belirtilen isimle PostgreSQL cüzdanlı bir Nixar ajanı döndürür.
    Ajan ağda (ledger) daha önce kayıtlı değilse, ilk önce 'trustee' ajanı üzerinden 
    ledger'a kaydı atılır, ardından ajan oluşturulur.
    """
    password_cb = lambda: "123456"
    
    try:
        return Nixar(name, password_cb, role, None, "pgsql", DB_HOST, DB_USERNAME, DB_PASSWORD)
    except NixarError as err:
        if "AgentNotRegistered" == err.code:
            print(f"Agent '{name}' network'te henüz kayıtlı değil. Trustee üzerinden kaydediliyor...")
            # Trustee ajanını oluştur/getir
            trustee = get_trustee_agent()
            
            # Hatadan dönen metadata json formatındadır
            reg_info = json.loads(err.message)
            reg_info["alias"] = name
            if role:
                reg_info["role"] = role
            else:
                # Role zorunlu istenirse diye default ENDORSER (Vatandaşlar genelde rol almazlar gerçi)
                pass 
                
            trustee.register_agent_to_ledger(json.dumps(reg_info))
            
            # Kayıt başarılı, şimdi asıl ajanı tekrar dönebiliriz.
            return Nixar(name, password_cb, role, None, "pgsql", DB_HOST, DB_USERNAME, DB_PASSWORD)
        else:
            raise err

def get_trustee_agent():
    """Ledger üzerine yeni oyuncular (Node/Steward/Endorser) kaydetme yetkisi olan kök hesaptır."""
    seed = "000000000000000000000000Trustee1"
    b64_seed = base64.b64encode(seed.encode()).decode()
    password_cb = lambda: "123456"
    return Nixar("trustee", password_cb, "TRUSTEE", b64_seed, "pgsql", DB_HOST, DB_USERNAME, DB_PASSWORD)
