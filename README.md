[Türkçe](#turkce) | [English](#english)

<a id="turkce"></a>

# FiveM Backdoor Blocklist

FiveM / FXServer ortamları için hazırlanmış, topluluk tarafından derlenen bir alan adı engelleme listesidir. Amaç, listedeki arka kapı, zararlı yazılım ve komuta-kontrol (C2) alan adlarına yapılan bağlantıları Windows `hosts` dosyası üzerinden yerel makineye yönlendirmektir.

> **Önemli:** Bu liste tek başına tam koruma sağlamaz. Bilinen alan adı ve C2 bağlantılarını engellemek için ek bir güvenlik katmanıdır; sunucudaki zararlı dosyaları bulmaz veya temizlemez.

## Nasıl çalışır?

- [`hosts.txt`](hosts.txt) dosyasındaki her satır `127.0.0.1 alan-adi.example` biçimindedir. Bu eşleme, ilgili alan adının normal DNS çözümlemesi yerine yerel makineye yönlendirilmesini sağlar.
- `main.py` alan adlarını doğrular, tekrarları temizler ve Windows'un `C:\Windows\System32\drivers\etc\hosts` dosyasına kendi işaretli bölümünü ekler.
- Diğer `hosts` kayıtlarını korur; sonraki çalıştırmalarda yalnızca kendi bölümünü günceller. Yedek dosyası oluşturmaz.
- Araç internete bağlanmaz, yeni alan adlarını kendiliğinden keşfetmez ve arka planda sürekli çalışmaz.

## Gereksinimler

- Windows ve Python 3.10 veya üzeri. Ek Python paketi gerekmez.
- Sistem `hosts` dosyasını değiştirmek için yönetici izni. Araç gerektiğinde Windows izin penceresini açar.

## Kurulum

PowerShell'i proje klasöründe açıp şu komutu çalıştırın:

```powershell
py -3 main.py install
```

Windows yönetici izni isterse onaylayın. Kurulumdan sonra durumu kontrol edin:

```powershell
py -3 main.py status
```

`up to date` çıktısı, sistemdeki işaretli bölümün mevcut `hosts.txt` listesiyle aynı olduğunu gösterir. Liste değiştiğinde `install` komutunu tekrar çalıştırmak yeterlidir. Değişiklik yoksa dosya yeniden yazılmaz.

`py main.py` komutu da `install` işlemini doğrudan başlatır.

## Komutlar

| Komut | İşlev |
| --- | --- |
| `py -3 main.py install` | Listeyi kurar veya günceller. |
| `py -3 main.py status` | Kurulum durumunu gösterir: `not installed`, `up to date` veya `out of date`. |
| `py -3 main.py remove` | Yalnızca bu projenin eklediği bölümü kaldırır. |

## Listeyi güncelleme

Yeni bir alan adını [`hosts.txt`](hosts.txt) dosyasına `127.0.0.1 alan-adi.example` biçiminde ekleyin ve `install` komutunu yeniden çalıştırın. Araç hatalı satır varsa sistem dosyasına yazmadan durur. Alan adını listeye eklemeden önce zararlı kullanıma ilişkin kanıtı kontrol edin; yanlış bir kayıt meşru hizmetleri de etkileyebilir.

## Kaldırma

Listeyi kaldırmak için `remove` komutunu kullanın. Bu komut yalnızca bu projenin işaretli bölümünü siler; başka uygulamaların `hosts` kayıtlarına dokunmaz. Araç kurulumda, güncellemede veya kaldırmada yedek dosyası oluşturmaz.

## Kapsam ve sınırlar

`hosts` eşlemeleri yalnızca dosyada yazılı alan adları için geçerlidir; alt alan adlarını kendiliğinden kapsamaz. Doğrudan IP adresine bağlanan veya işletim sisteminin `hosts` çözümlemesini kullanmayan yazılımlar bu yöntemden etkilenmeyebilir. Listedeki alan adlarının güncelliği ve zararlı olup olmadığı araç tarafından otomatik doğrulanmaz.

---

<a id="english"></a>

# FiveM Backdoor Blocklist

A community-curated domain blocklist for FiveM / FXServer environments. It aims to redirect connections to listed backdoor, malware, and command-and-control (C2) domains to the local machine through the Windows `hosts` file.

> **Important:** This list does not provide complete protection on its own. It adds a layer of protection against known domain and C2 connections; it does not find or remove malicious files from your server.

## How does it work?

- Each line in [`hosts.txt`](hosts.txt) follows the format `127.0.0.1 domain.example`. This mapping redirects the specified domain to the local machine instead of its normal DNS result.
- `main.py` validates domains, removes duplicates, and adds a marked section to the Windows `C:\Windows\System32\drivers\etc\hosts` file.
- It preserves other `hosts` entries and updates only its own section on later runs. It does not create backup files.
- The tool does not connect to the internet, discover new domains automatically, or run continuously in the background.

## Requirements

- Windows and Python 3.10 or newer. No additional Python packages are required.
- Administrator permission to modify the system `hosts` file. The tool opens the Windows permission prompt when needed.

## Installation

Open PowerShell in the project directory and run:

```powershell
py -3 main.py install
```

Approve the Windows administrator prompt if it appears. Then check the installation status:

```powershell
py -3 main.py status
```

`up to date` means the marked section in the system file matches the current `hosts.txt` list. Run `install` again after the list changes. If there is no change, the system file is not rewritten.

Running `py main.py` also starts the `install` operation directly.

## Commands

| Command | Purpose |
| --- | --- |
| `py -3 main.py install` | Install or update the list. |
| `py -3 main.py status` | Show `not installed`, `up to date`, or `out of date`. |
| `py -3 main.py remove` | Remove only the section added by this project. |

## Updating the list

Add a domain to [`hosts.txt`](hosts.txt) in the format `127.0.0.1 domain.example`, then run `install` again. If a line is invalid, the tool stops before changing the system file. Check the evidence of malicious use before adding a domain; an incorrect entry can also affect legitimate services.

## Removal

Use `remove` to uninstall the list. It removes only this project's marked section and leaves `hosts` entries added by other applications untouched. The tool does not create backup files during installation, updates, or removal.

## Scope and limitations

`hosts` mappings apply only to the exact domain names in the file; they do not automatically cover subdomains. Software that connects directly to an IP address or does not use the operating system's `hosts` resolution may not be affected. The tool does not automatically verify whether listed domains are still active or malicious.
