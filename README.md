# Roleplay Agent — Kalıcı Hafızalı Yerel Karakter Sistemi

Yerel olarak çalışan, tek karakterli, kalıcı hafızalı bir roleplay aracı. 
Ollama + Mistral Small 22B üzerine kurulu. İnternet bağlantısı gerektirmez, 
veriler kullanıcının kendi diskinde kalır.

## Sistem Mimarisi

Üç katmandan oluşuyor:

**1. Karakter Katmanı (`character.md`)**  
Modelin "kim olduğu". Kişilik, geçmiş, konuşma tarzı, dünya.

**2. Persona Katmanı (`persona.md`)**  
Modelin "konuştuğu kişi". Kullanıcının görünüşü, kişiliği, hikayesi. 
Çoğu roleplay arayüzünde olmayan, ama olması gerektiğini düşündüğüm bir 
parça — karakter karşısındaki kişiyi "görsün" istedim.

**3. Hafıza Katmanı (`history.json`)**  
Konuşmalar otomatik olarak diske yazılır. Program kapanıp açıldığında 
kaldığın yerden devam edersin. Konuşma 40 mesajı geçince eski mesajlar 
otomatik özetlenir — modelin context window'u dolmaz, önemli olaylar 
unutulmaz.

## Mimari Kararlar

Birkaç tercihin gerekçesi:

**Neden tek karakter?** Çok sayıda yüzeysel karakter yerine tek bir 
karakteri derinlemesine kişiselleştirmeyi seçtim. 200 kelimelik kart 
yerine 5000 kelimelik kart, ayrı lore dosyası, ilişki dinamiği — hepsi 
mümkün hâle geliyor.

**Neden yerel?** Mahremiyet. Roleplay konuşmaları kişisel olabiliyor; 
bunların kullanıcının makinesinden ayrılmaması gerektiğini düşündüm.

**Neden JSON?** Veritabanı bu ölçek için aşırı, düz metin ise yapı 
sunmuyor. JSON ikisinin arasında: hafif, okunabilir, standart kütüphane 
ile çalışıyor, kullanıcı dosyayı elle açıp inceleyebiliyor.

## Kurulum

1. [Ollama](https://ollama.com/download)'yı kur.
2. Modeli çek (~13 GB):
ollama pull mistral-small:22b
3. Şablonları kopyala ve karakterini/persona'nı yaz:
cp character.md.example character.md
cp persona.md.example persona.md
4. Çalıştır:
python roleplay.py

## Kullanım

Programı başlatınca terminal bir karşılama ekranı gösterir. Konuşmaya 
başlamak için karakterinle nasıl tanışmak istediğini yaz — bir selamla 
veya bir sahne kurarak.

Komutlar:
- `q` → çıkış (hikaye kaydedilir, kaldığın yerden devam edersin)
- `reset` → tüm konuşmayı sıfırla (onay ister)

## Dil Notu

Mistral Small Türkçeyi kabul ediyor ama İngilizcedeki kadar akıcı değil. 
İlk testlerde Türkçe denedim, model bazen tökezledi. İngilizceye geçince 
kalite belirgin arttı — atmosfer, nüans, edebi dokunuş. Türkçe oynanabilir 
ama projenin asıl karakterini İngilizcede görüyorsun.

Daha güçlü Türkçe için `command-r` veya `gemma3:27b` test edilebilir.

## Roadmap

- [x] Karakter + Persona sistemi
- [x] Kalıcı hafıza
- [x] Otomatik özetleme
- [ ] Web UI (Gradio)
- [ ] Uzun süreli anı katmanı
- [ ] Karakter notları (model kullanıcı hakkında öğrendiklerini kaydeder)
- [ ] İlişki dinamiği (güven, yakınlık seviyeleri)

## Notlar

Windows'ta Ollama'nın varsayılan portu (11434) Hyper-V tarafından rezerve 
edilmiş olabilir. Çözüm:
setx OLLAMA_HOST "127.0.0.1:11500"
Yeni terminal aç, `ollama serve` ile başlat. `roleplay.py` içindeki URL'yi 
de aynı porta güncelle.

## Acknowledgments

Geliştirme sürecinde AI kod asistanlarından destek alınmıştır.

## Lisans

MIT.