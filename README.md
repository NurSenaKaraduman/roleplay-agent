# Roleplay Agent — Kalıcı Hafızalı Yerel Karakter Sistemi

Yerel olarak çalışan, tek karakterli, kalıcı hafızalı bir roleplay aracı. 
Ollama + Mistral Small 22B üzerine kurulu. İnternet bağlantısı gerektirmez, 
veriler kullanıcının kendi diskinde kalır.

## Şeffaflık Notu

Bu proje, [Özal Yıldırım'ın "100 Satır Python ile Kendi Yerel AI Ajanınızı Yazın"](https://www.ozalyildirim.com/blog/100-satir-python-ile-kendi-yerel-ai-asistaninizi-yazin) 
yazısındaki agent.py omurgasının üzerine inşa edildi. Yazılım Mühendisliği 
1. sınıf öğrencisi olduğum için Python bilgim yazıdaki kodu sıfırdan 
genişletmeye yetmedi; bu yüzden Anthropic'in Claude modelinden destek aldım. 

Şahsi katkılarım:
- Tasarım kararları (tek karakter + persona + kalıcı hafıza mimarisi)
- Karakter ve persona kartlarının yazımı (içerikleri kendi yarattığım hikayedir)
- Sistem prompt'unun roleplay kuralları (özellikle dil kilidi, gore yasağı, 
  tekrar engelleme maddeleri — bu maddeleri Gemini önerileri ve kendi 
  testlerimle şekillendirdim)
- Karakterin ürettiği cevaplara göre prompt iterasyonları
- Test ve hata ayıklama süreçleri

Kod üretimi için Claude'dan destek alınan kısımlar: `roleplay.py` 
omurgası — özellikle hafıza yönetimi, özetleme sistemi ve ana döngü.

Bu sayfanın dürüstçe yazılması benim için önemli; çünkü kodun her satırını 
şu an yazamasam da her satırın **ne yaptığını** anlayarak ilerledim. 
Pythonum oturduğunda geri dönüp bu kodu kendim yeniden yazmayı planlıyorum.

## Sistem Mimarisi

Üç katmandan oluşuyor:

**1. Karakter Katmanı (`character.md`)**  
Modelin "kim olduğu". Kişilik, geçmiş, konuşma tarzı, dünya.

**2. Persona Katmanı (`persona.md`)**  
Modelin "konuştuğu kişi". Kullanıcının görünüşü, kişiliği, hikayesi.  
(c.ai'ın eksik bıraktığı bir şey — kullanıcı kartını da modele veriyoruz.)

**3. Hafıza Katmanı (`history.json`)**  
Konuşmalar otomatik olarak diske yazılır. Program kapanıp açıldığında 
kaldığın yerden devam eder. Konuşma 40 mesajı geçince eski mesajlar 
otomatik özetlenir — modelin context window'u dolmaz, önemli olaylar 
unutulmaz.

## Kurulum

1. [Ollama](https://ollama.com/download)'yı indir
2. Modeli çek:
ollama pull mistral-small:22b
3. Şablonları kopyala ve doldur:
cp character.md.example character.md
cp persona.md.example persona.md
4. Çalıştır:
python roleplay.py

## Komutlar

- `q` → Çıkış (hikaye kayıtlı, kaldığın yerden devam edersin)
- `reset` → Tüm konuşmayı sıfırla (onay ister)

## Roadmap

- [x] Karakter + Persona sistemi
- [x] Kalıcı hafıza
- [x] Otomatik özetleme
- [ ] Web UI (Gradio)
- [ ] Uzun süreli anı tool'u
- [ ] Karakter notları (model kullanıcı hakkında öğrendiklerini kaydeder)
- [ ] İlişki dinamiği (güven, yakınlık seviyeleri)

## Notlar

- Türkçe oynanış denendi ama Mistral Small'un Türkçesi zayıf. İngilizce 
  belirgin daha iyi sonuç veriyor. Daha iyi Türkçe için `command-r` veya 
  `gemma3:27b` denenebilir.
- Windows'ta Ollama'nın varsayılan portu (11434) Hyper-V tarafından 
  rezerve edilmiş olabilir. Çözüm: `OLLAMA_HOST=127.0.0.1:11500`.