# Nixar API Dockerized on Windows

Bu dokümantasyon, projenizi Nixar-Core Linux kütüphaneleriyle birlikte PostgreSQL cüzdanı kullanarak Docker üzerinde herhangi bir makinede (Windows/Ubuntu/Mac) ayağa kaldırmanız için gereken adımları açıklamaktadır.

## Proje Yapısı

Kodlarınız artık kök dizinde değil, profesyonel standartlara uygun olarak `app/` dizini altında mikroservis tarzında bölünmüştür. Cüzdan operasyonları ve ajan üretimi `app/services/nixar_service.py` üzerindeyken yönlendirmeler (router'lar) ve swagger API `app/main.py` içerisindedir. 

Proje şöyledir:
* `requirements.txt`: İhtiyaç duyulan bağımlılıklar
* `Dockerfile`: Container'ı başlatmak için Linux imajının derlenmesi (`libsodium`, `libzmq` ve `libpq` vb. bulunur)
* `docker-compose.yml`: API'nizi ve PostgreSQL veritabanını aynı network'te eşzamanlı ayağa kaldırır
* `init-db.sql`: Veritabanı ilk başladığında Nixar'ın wallet için duyduğu agent-veritabanlarını (şemaları) oluşturur ("trustee", "api_issuer" vb.)

---

## 🚀 Adım Adım Çalıştırma

### Adım 1: Nixar Linux (x86_64) Kütüphanesi
Uygulama Docker üzerinde çalışacağından Linux kütüphanesine (`.so` uzantılı) ihtiyacınız vardır. Gerekli linux dosyalarını halihazırda `nixar_api_linux/` klasörü altına yerleştirdiğiniz için `Dockerfile` bu kütüphaneleri otomatik olarak okuyacak ve kullanacaktır. Ekstra indirme yapmanıza gerek yoktur.

> **NOT:** Cüzdanları PostgreSQL kullanarak konfigüre ettiğimiz için Nixar PostgreSQL bindings için `libpq-dev` gereksinimi duymaktadır. Sizin için yazdığım `Dockerfile` halihazırda bu paketi linux ortamına yüklemeyi içermektedir.

### Adım 2: Genesis Dosyası
`genesis.txn` (ağla konuşmanız için gereken remote IP adreslerinin barındığı dosya) dosyasını projenin ana dizininden silmeyin!

### Adım 3: Docker-Compose'u Ayağa Kaldırma
Windows Powershell, CMD vb. terminalinizi açın ve proje dizininde çalıştırın:

```cmd
docker-compose up --build -d
```

* `--build` parametresi ilk kez yeni kütüphanelerin eklenerek imajın derlenmesini sağlar.
* `-d` parametresi arka planda çalışmasını sağlar. Konteynerın kendi terminal çıktılarını görmek isterseniz `docker-compose logs -f api` diyebilirsiniz.

### Adım 4: Kullanım Başlangıcı
Uygulama başarıyla veritabanına bağlanıp ayağı kalktıktan sonra yine tarayıcınızdan:

[http://localhost:8000/docs](http://localhost:8000/docs)

adresine gidebilirsiniz. İlk işlem olarak `/agent/initialize` endpoint'ine tıkladığınızda;
1. Öncelikli olarak "trustee" adıyla bir veritabanı cüzdanı oluşacaktır.
2. Diğer üç ajan (Issuer, Prover, Verifier) otomatik olarak *PostgreSQL* cüzdan (JSON yerine) kullanılarak oluşturulup veritabanındaki yerlerini alacaklardır.
3. Bundan sonraki tüm akışlar `PostgreSQL` veri depolama birimlerinde kriptografik olarak kaydedilecektir. Kapatıp açtığınızda agent'ın DID'leri vb. veritabanından kalıcı okunacaktır. 
