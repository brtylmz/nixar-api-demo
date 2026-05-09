# Nixar SSI API

**Nixar SSI API**, [Hyperledger Indy](https://www.hyperledger.org/projects/hyperledger-indy) tabanlı bir dağıtık kimlik ledger'ı üzerinde çalışan, **Self-Sovereign Identity (SSI)** iş akışlarını REST API olarak sunan bir Python/FastAPI uygulamasıdır. Cüzdan (wallet) yönetimi için PostgreSQL kullanır ve Nixar C kütüphanesini (`libnixar_core.so`) `cffi` aracılığıyla sarar.

---

## İçindekiler

- [Ne işe yarar?](#ne-ise-yarar)
- [Nasıl çalışır?](#nasil-calisir)
- [Gereksinimler](#gereksinimler)
- [Kurulum ve Çalıştırma](#kurulum-ve-calistirma-docker)
- [Ortam Değişkenleri](#ortam-degiskenleri)
- [API Referansı](#api-referansi)
- [Dashboard UI](#dashboard-ui)
- [Proje Yapısı](#proje-yapisi)

---

## Ne işe yarar?

Bu servis, merkeziyetsiz kimlik (SSI/DID) altyapısını kullanarak aşağıdaki işlemleri REST API üzerinden gerçekleştirir:

| İşlem | Açıklama |
|---|---|
| **Ajan Yönetimi** | Issuer, Prover ve Verifier ajanlarını oluşturur, ledger'a kaydeder, cüzdanlarını PostgreSQL'de saklar |
| **Schema Oluşturma** | Hyperledger Indy ledger'ına kimlik belgesi şeması yazar (ör. "Diploma", "Ehliyet") |
| **Credential Definition** | Schema üzerine kriptografik CL imza anahtarları türeterek cred-def oluşturur |
| **Credential Verme** | Issuer, bir Prover'a imzalı Verifiable Credential verir |
| **Doğrulama** | Verifier, Prover'ın sunduğu credential'ı sıfır bilgi ispatı (ZKP) ile doğrular |

---

## Nasıl çalışır?

### Mimari

Uygulama SOLID prensiplerine göre katmanlı tasarlanmıştır:

```
+---------------------------------------------+
|              HTTP (FastAPI)                 |  <-- app/routers/
+---------------------------------------------+
|           İş Mantığı (Services)             |  <-- app/services/
+---------------------------------------------+
|         SDK Erişimi (Repository)            |  <-- app/repositories/
+---------------------------------------------+
|       Nixar Native Kütüphane (cffi)         |  <-- nixar/nixar_api.py
+----------------------+----------------------+
|   PostgreSQL Wallet  |   Indy Ledger (ZMQ)  |
+----------------------+----------------------+
```

| Katman | Sorumluluk |
|---|---|
| **Routers** | HTTP istek/yanıt dönüşümü |
| **Services** | İş mantığı — schema, credential, doğrulama, ajan yaşam döngüsü |
| **Repository** | `AgentRepository` — Nixar SDK'yı saran, cüzdan / ledger işlemlerini yöneten katman |
| **nixar/** | `cffi` ile `libnixar_core.so`'yu saran Python wrapper. FFI singleton ile process başına bir kez yüklenir. |

### SSI İş Akışı

```
1. POST /agent/initialize
      └── Trustee ile api_issuer, api_prover, api_verifier oluşturulur,
          ledger'a kaydedilir, cüzdanlar PostgreSQL'e yazılır.

2. POST /schema
      └── api_issuer ledger'a schema yazar
          Yanıt: schema_id = "EcN3...:2:Diploma:1.0"

3. POST /cred-def
      └── api_issuer CL imza anahtarlarını türetir ve ledger'a yazar
          Yanıt: cred_def_id = "EcN3...:3:CL:27:tag"

4. POST /credential/issue
      └── api_issuer  → credential offer oluşturur
          api_prover  → credential request üretir
          api_issuer  → credential'ı imzalar
          api_prover  → cüzdanına kaydeder
          Yanıt: store_cred_id = "uuid"

5. POST /verification/verify
      └── api_verifier → ZKP presentation request üretir
          api_prover   → credential ifşa etmeden presentation oluşturur
          api_verifier → presentation'ı doğrular
          Yanıt: { "is_valid": true }
```

---

## Gereksinimler

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, macOS veya Linux)
- Ulaşılabilir bir **Hyperledger Indy / VON Network** ledger'ı
- Ledger'ın `genesis.txn` dosyası

> **Not:** Linux native kütüphaneleri (`nixar_api_linux/`) proje klasöründe bulunmalıdır.
> macOS için `nixar_api_apple_silicon/` altındaki dylib da mevcuttur.

---

## Kurulum ve Çalıştırma (Docker)

### 1. Genesis dosyasını yerleştirin

Kullanacağınız ledger'ın `genesis.txn` dosyasını proje kök dizinine kopyalayın:

```bash
cp /path/to/genesis.txn ./genesis.txn
```

### 2. (İsteğe bağlı) Ortam değişkenlerini özelleştirin

Varsayılan değerler çoğu kurulum için yeterlidir. Değiştirmek isterseniz
`docker-compose.yml` içindeki `environment` bloğunu düzenleyin.

### 3. Servisleri başlatın

```bash
docker compose up --build
```

İlk çalıştırmada:
1. PostgreSQL konteyneri ayağa kalkar ve `init-db.sql` ile `trustee`, `api_issuer`, `api_prover`, `api_verifier` veritabanlarını oluşturur.
2. API konteyneri derlenir ve `http://localhost:8000` adresinde dinlemeye başlar.

### 4. Kontrol edin

| URL | Açıklama |
|---|---|
| `http://localhost:8000` | Dashboard UI |
| `http://localhost:8000/docs` | Swagger/OpenAPI |

### 5. Ajanları başlatın

Konteynerler çalışır hale gelince **bir kez** çağırın:

```bash
curl -X POST http://localhost:8000/agent/initialize
```

Bu adım tüm ajanları oluşturur, ledger'a kaydeder ve cüzdanları PostgreSQL'e yazar.

> **Yeniden başlatma:** Konteyner yeniden başlatılırsa cüzdanlar PostgreSQL'de kaldığından bu adım tekrar hatasız çalışır; var olan cüzdanlar otomatik açılır.

---

## Ortam Değişkenleri

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `DB_HOST` | `localhost` | PostgreSQL adresi (docker-compose'da `db`) |
| `DB_USERNAME` | `postgres` | PostgreSQL kullanıcı adı |
| `DB_PASSWORD` | `postgres` | PostgreSQL parolası |
| `WALLET_TYPE` | `pgsql` | Cüzdan türü: `pgsql`, `sqlite` veya `json` |
| `WALLET_PASSWORD` | `123456` | Cüzdan şifreleme parolası |
| `TRUSTEE_SEED` | `000000000000000000000000Trustee1` | Trustee seed (ledger ile eşleşmeli) |
| `MAX_CRED_NUM` | `1000` | Revocation registry kapasitesi |

---

## API Referansı

Tam Swagger/OpenAPI: `http://localhost:8000/docs`

### Ajan

| Method | Endpoint | Açıklama |
|---|---|---|
| `POST` | `/agent/initialize` | Issuer, Prover ve Verifier ajanlarını oluşturur / açar |

### Schema

| Method | Endpoint | Açıklama |
|---|---|---|
| `POST` | `/schema` | Ledger'a yeni schema yazar |
| `GET` | `/schemas` | Tüm şemaları listeler |
| `GET` | `/schema/{schema_id}` | Tek şema döndürür |

**POST /schema — örnek:**
```json
{
  "schema_name": "Diploma",
  "attributes": ["ad", "soyad", "okul", "mezuniyet_yili"]
}
```

### Credential Definition

| Method | Endpoint | Açıklama |
|---|---|---|
| `POST` | `/cred-def` | Credential definition oluşturur |
| `GET` | `/cred-defs` | Tüm cred-def'leri listeler |
| `GET` | `/cred-def/{cred_def_id}` | Tek cred-def döndürür |

**POST /cred-def — örnek:**
```json
{
  "schema_id": "EcN3scFwKiJS2mMZffbNhv:2:Diploma:1.0",
  "is_revocable": false
}
```

### Credential

| Method | Endpoint | Açıklama |
|---|---|---|
| `POST` | `/credential/issue` | Credential verir ve prover cüzdanına kaydeder |
| `GET` | `/credentials` | Tüm credential'ları listeler |
| `GET` | `/credential/{cred_id}` | Tek credential döndürür |

**POST /credential/issue — örnek:**
```json
{
  "cred_def_id": "EcN3scFwKiJS2mMZffbNhv:3:CL:27:20260509",
  "values": {
    "ad": "Ahmet",
    "soyad": "Yilmaz",
    "okul": "ODTU",
    "mezuniyet_yili": "2024"
  }
}
```

> **Not:** `values` alanındaki değerler düz string olarak verilebilir; servis Indy protokolünün gerektirdiği `{"raw": ..., "encoded": ...}` formatına otomatik dönüştürür.

### Doğrulama

| Method | Endpoint | Açıklama |
|---|---|---|
| `POST` | `/verification/verify` | ZKP ile credential doğrulaması yapar |

**POST /verification/verify — örnek:**
```json
{
  "schema_id": "EcN3scFwKiJS2mMZffbNhv:2:Diploma:1.0",
  "cred_def_id": "EcN3scFwKiJS2mMZffbNhv:3:CL:27:20260509"
}
```

**Başarılı yanıt:**
```json
{
  "status": "success",
  "is_valid": true
}
```

---

## Dashboard UI

`http://localhost:8000` adresindeki arayüzde tüm SSI akışı adım adım çalıştırılabilir:

| Adım | İşlem |
|---|---|
| 1 | **Ajan Başlat** — Ajanları oluşturur ve ledger'a kaydeder |
| 2 | **Schema Oluştur** — Attribute listesiyle ledger'a schema yazar |
| 3 | **CredDef Oluştur** — Schema üzerinden credential definition oluşturur |
| 4 | **Kimlik Ver** — JSON değerleriyle credential yayınlar |
| 5 | **Doğrula** — ZKP tabanlı presentation ile credential doğrular |
| 6 | **Sorgula** — Kayıtlı schema, cred-def ve credential'ları listeler |

Adımlar arasında `schema_id` ve `cred_def_id` otomatik aktarılır; sağ panelde canlı log akışı görüntülenir.

---

## Proje Yapısı

```
nixar_api_python/
├── app/
│   ├── main.py                    # FastAPI giriş noktası
│   ├── config.py                  # Ortam değişkenleri (Settings singleton)
│   ├── dependencies.py            # FastAPI Depends() fabrika fonksiyonları
│   ├── models/schemas.py          # Pydantic istek modelleri
│   ├── routers/
│   │   ├── agent.py               # POST /agent/initialize
│   │   ├── schema.py              # /schema, /schemas, /cred-def, /cred-defs
│   │   ├── credential.py          # /credential/issue, /credentials
│   │   └── verification.py        # /verification/verify
│   ├── services/
│   │   ├── agent_service.py       # Ajan yaşam döngüsü yönetimi
│   │   ├── schema_service.py      # Schema & CredDef iş mantığı
│   │   ├── credential_service.py  # Credential issuance iş mantığı
│   │   └── verification_service.py# ZKP presentation & doğrulama
│   ├── repositories/
│   │   └── agent_repository.py    # Nixar SDK sarmalayıcı
│   └── static/index.html          # Dashboard UI
├── nixar/
│   ├── nixar_api.py               # cffi ile libnixar_core.so wrapper
│   ├── nixar_api.h                # C başlık dosyası (cffi cdef kaynağı)
│   ├── nixar_error.py             # NixarError sınıfı
│   └── nixar_logging.py           # SDK log callback
├── nixar_api_linux/
│   ├── ubuntu_20/                 # Ubuntu 20.04 native kütüphaneleri
│   └── x86_64-unknown-linux-gnu/  # Generic Linux x86_64 kütüphaneleri
├── nixar_api_apple_silicon/       # macOS Apple Silicon dylib
├── genesis.txn                    # Ledger genesis dosyası (kullanıcı sağlar)
├── init-db.sql                    # PostgreSQL veritabanı init scripti
├── docker-compose.yml             # API + PostgreSQL servis tanımı
├── Dockerfile                     # Python 3.9-slim tabanlı Docker imajı
└── requirements.txt               # Python bağımlılıkları
```