# ⚔️ Brute Force Tool

Bu araç, HTTP, FTP ve SSH servislerinde brute force saldırıları gerçekleştirmek için tasarlanmıştır. Kullanıcı adı ve parola dosyalarından ya da tekil girişlerden brute force yöntemiyle doğrulama yapabilirsiniz. Hedefe erişim sağlamak için farklı servislerin portlarını da belirleyebilirsiniz.

## 🔧 Özellikler

- **HTTP Brute Force**: Web login formlarında brute force saldırısı yapma.
- **FTP Brute Force**: FTP servislerine giriş yapmak için brute force.
- **SSH Brute Force**: SSH servislerine giriş yapmak için brute force.
- **Çoklu Kullanıcı ve Parola Girişi**: Kullanıcı adı ve parola dosyalarını kullanarak denemeler yapabilir.
- **Verbose Modu**: Detaylı günlük kaydı almak için verbose modunu etkinleştirebilirsiniz.
- **Geçici Gecikme**: Her login denemesi arasında gecikme eklemek için `--delay` parametresini kullanabilirsiniz.
- **Paralel İşlem**: Çoklu iş parçacığı kullanarak saldırıyı hızlandırabilirsiniz.
- **Sonuç Kaydetme**: Başarılı girişleri bir dosyaya kaydedebilirsiniz.
- **Port Seçimi**: Her servis için uygun portu seçebilirsiniz (varsayılan portlar 80, 21 ve 22).

## Gereksinimler

- Python 3.x
- Aşağıdaki kütüphaneler:

  - `requests`
  - `fake_useragent`
  - `paramiko`
  - `pysftp`
  - `colorama`

## Kullanım
- `python SPC.py --http -H example.com -u admin -P passwords.txt`
- `python SPC.py --ftp -H example.com -U usernames.txt -P passwords.txt --port 21`

  **-h yap orda var herşey.**
