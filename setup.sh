#!/bin/bash

# Gerekli Python kütüphanelerini kur
pip install requests stem fake_useragent pytesseract beautifulsoup4

# Tesseract OCR'yi kurmak için gerekli komutlar (Debian/Ubuntu tabanlı sistemler için)
if ! command -v tesseract &> /dev/null
then
    echo "Tesseract kurulmamış, şimdi kuruluyor..."
    sudo apt-get update
    sudo apt-get install tesseract-ocr -y
else
    echo "Tesseract zaten kurulu."
fi

echo "Gerekli tüm kütüphaneler ve araçlar yüklendi."
