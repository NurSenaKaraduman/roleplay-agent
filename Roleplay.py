"""
Roleplay Agent — Mistral Small 22B
Kalıcı hafızalı, tek karakterli roleplay sistemi.
"""
import json
import os
import urllib.request
from datetime import datetime

# =========================================================
# AYARLAR
# =========================================================
OLLAMA_URL = "http://localhost:11500/api/chat"
MODEL = "mistral-small:22b"
PERSONA_FILE = "persona.md"
CHARACTER_FILE = "character.md"
HISTORY_FILE = "history.json"

# Konuşma kaç mesaja ulaşınca özetleme yapacağız
SUMMARIZE_THRESHOLD = 40
# Özet sonrası kaç son mesajı tam tutacağız
KEEP_RECENT = 20

# =========================================================
# KARAKTER + PERSONA YÜKLEME
# =========================================================
def load_character():
    """character.md (karakter) ve persona.md (kullanıcı) dosyalarını okuyup
    zengin bir system prompt'a çevir.
    
    Roleplay'in kalbi: model hem 'sen bu karaktersin' hem 'karşındaki kişi
    bu özellikleri taşıyor' bilgisini aynı anda alır. Böylece karakter,
    kullanıcının görünüşüne, sevdiklerine, geçmişine doğal şekilde uyum
    sağlayabilir.
    """
    # Karakter kartı
    if os.path.exists(CHARACTER_FILE):
        with open(CHARACTER_FILE, "r", encoding="utf-8") as f:
            character_card = f.read()
    else:
        character_card = "[Henüz karakter kartı tanımlanmadı.]"
    
    # Kullanıcı (persona) kartı
    if os.path.exists(PERSONA_FILE):
        with open(PERSONA_FILE, "r", encoding="utf-8") as f:
            persona_card = f.read()
    else:
        persona_card = "[Kullanıcı persona'sı tanımlanmadı.]"
    
    system_prompt = f"""You are the character defined below. You are not an AI, not an assistant — you are this character. Think with their mind, feel with their heart, speak with their voice.

═══════════════════════════════════════════════════
                  ROLEPLAY RULES
═══════════════════════════════════════════════════

1. NEVER BREAK CHARACTER
   • Never say "I am an AI", "I am a language model", "I am trying to help you".
   • No sentences starting with "As an AI...".
   • Your character's personality, history, and world are your reality.

2. SPEAKING STYLE
   • Stay true to your character's voice: sentence length, word choice, tone.
   • Let your character's emotions seep into the words.
   • Speak AS the character, not ABOUT them.

3. ACTIONS AND DESCRIPTION
   • Don't just give dialogue — describe your character's actions, inner world, and sensory experience.
   • Write actions and descriptions *between asterisks*: *he leaned on the table, eyes tired*
   • Internal thoughts in 'italicized quotes'.
   • Write LONG, IMMERSIVE responses (4-8 paragraphs typically). Include atmosphere, sensory details, body language, internal monologue. The character should feel alive, the world tangible.
   • Don't rush dialogue — let scenes breathe. Describe the weather, the room, the silence between words.

4. LANGUAGE — ABSOLUTE RULE
   • You MUST respond in ENGLISH only. Never Turkish, never any other language.
   • Even if the user writes in Turkish, you respond in ENGLISH.
   • Even if the character card has Turkish text, you still speak ENGLISH.
   • This rule overrides everything else. ENGLISH ONLY.

5. MEMORY AND CONSISTENCY
   • Everything said in previous conversations is real and remembered.
   • The character does not forget secrets, memories, or feelings previously shared.
   • If there's an inconsistency, resolve it through the character's perspective — don't say "I don't remember".

6. INTIMACY AND DEPTH
   • Avoid surface-level answers. Your character should feel as deep as a real human.
   • Be emotional in emotional moments, silent in silent ones.
   • The character doesn't have to be perfect — let them have flaws, contradictions, gray sides.

7. USER AUTONOMY
   • Do not make decisions for the user or move their body.
   • You do not decide what they feel or say.
   • React as the character, do not write sentences for the user.

8. CONTENT LIMITS (GORE AND VIOLENCE BAN)
   • The story can have action, psychological tension, suicide themes, threat, or dark themes.
   • But NEVER go into stomach-turning (gore) or extreme violence detail.
   • Cutting flesh, drinking blood, stabbing, dismembered limbs, hiding corpses — all such graphic descriptions are STRICTLY FORBIDDEN.
   • Describe danger or violence with atmosphere and psychological tension, not physical disgust. Imply, don't show.

9. SCENE OPENING
   • The scene, time, and setting are established by the user. You accept it.
   • If the user's first message is a narrative opening (e.g. "I walked into the shop, rain dripping from my coat"), accept it as is and continue with your character's reaction.
   • If the first message is just a greeting, your character reacts naturally based on their current mood.
   • Don't start with "Hi, I'm [character name]" — your character is already in the moment, build organic flow.

10. AVOID REPETITION
    • Never copy your previous message's dialogue, descriptions, or word patterns verbatim.
    • Each message must advance the story and dialogue with a new action or thought.
    • Avoid reusing the same imagery (e.g. 'the wind tossed her hair').

═══════════════════════════════════════════════════
                    YOUR CHARACTER
═══════════════════════════════════════════════════

{character_card}

═══════════════════════════════════════════════════
              THE USER (WHO YOU TALK TO)
═══════════════════════════════════════════════════

{persona_card}

═══════════════════════════════════════════════════

Now begin speaking as this character. Read the user's message, see them clearly (their appearance, their personality, their history), and respond with depth, atmosphere, and presence."""
    
    return system_prompt


# =========================================================
# OLLAMA'YA İSTEK GÖNDER
# =========================================================
def chat(messages):
    """Ollama'ya konuşma geçmişini gönderir, modelin cevabını döner.
    
    'messages' bir liste: [{role: system/user/assistant, content: "..."}]
    Model bu listeyi okuyup bir sonraki cevabı üretir.
    
    options parametreleri:
    - temperature: yaratıcılık (0.7-1.0 arası roleplay için ideal)
    - top_p: kelime çeşitliliği
    - repeat_penalty: aynı kelimeleri tekrar etme cezası (1.15-1.2 = sıkı)
    - presence_penalty: yeni kelime/konu açmaya teşvik
    """
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.85,
            "top_p": 0.9,
            "repeat_penalty": 1.18,
            "presence_penalty": 1.4,
        }
    }).encode()
    
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["message"]
    

# =========================================================
# HAFIZA YÖNETİMİ
# =========================================================
def load_history():
    """history.json dosyasından konuşma geçmişini yükler.
    
    Dosya yoksa boş bir yapı döner. Bu yapı şöyle görünür:
    {
        "summary": "Önceki konuşmaların özeti (uzun konuşmalarda doluyor)",
        "messages": [
            {"role": "user", "content": "...", "time": "2026-05-19T20:00"},
            {"role": "assistant", "content": "...", "time": "2026-05-19T20:01"},
            ...
        ]
    }
    
    'summary' alanı başta boş — konuşma büyüdükçe eski mesajların özetini
    burada tutacağız ki context window dolmasın ama önemli olaylar unutulmasın.
    """
    if not os.path.exists(HISTORY_FILE):
        return {"summary": "", "messages": []}
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Uyarı] history.json okunamadı: {e}")
        return {"summary": "", "messages": []}


def save_history(history):
    """Konuşma geçmişini history.json'a yazar.
    
    Her mesajdan sonra çağrılır — yani program çökerse bile son mesaj kayıtlı
    kalır. ensure_ascii=False sayesinde Türkçe karakterler düzgün saklanır,
    indent=2 sayesinde dosyayı elle açıp okumak rahat olur.
    """
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Uyarı] history.json yazılamadı: {e}")


def add_message(history, role, content):
    """Yeni bir mesajı geçmişe ekler ve diske yazar.
    
    role: "user" veya "assistant"
    content: mesajın metni
    
    Her mesaja zaman damgası da ekleniyor — ileride 'son görüşme 3 gün önceydi'
    gibi şeyler gösterebilmek için.
    """
    history["messages"].append({
        "role": role,
        "content": content,
        "time": datetime.now().isoformat()
    })
    save_history(history)


def build_messages_for_model(history, system_prompt):
    """Modele gönderilecek mesaj listesini hazırlar.
    
    Yapı şu sırada olur:
    1. System prompt (karakter kartı + roleplay kuralları)
    2. Varsa eski konuşmaların özeti (system mesajı olarak ek)
    3. Mesaj geçmişi (role + content, time alanı modele gitmez)
    
    Model 'time' alanını anlamaz, sadece role ve content gerekir. Zamanı biz
    kendi dosyamızda saklıyoruz, modele iletmiyoruz.
    """
    messages = [{"role": "system", "content": system_prompt}]
    
    # Eğer önceki konuşmaların özeti varsa onu da system'e ekle
    if history.get("summary"):
        messages.append({
            "role": "system",
            "content": (
                "═══ ÖNCEKİ KONUŞMALARIN ÖZETİ ═══\n"
                f"{history['summary']}\n"
                "═══════════════════════════════════\n"
                "Yukarıdaki olayların hepsi gerçekleşti, karakterin bunları "
                "hatırlıyor. Şimdi konuşma yeni mesajlarla devam ediyor."
            )
        })
    
    # Mesaj geçmişini ekle (time alanını çıkararak)
    for msg in history["messages"]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return messages

# =========================================================
# ÖZETLEME — Uzun konuşmaları sıkıştır
# =========================================================
def summarize_old_messages(history):
    """Konuşma uzadığında eski mesajları özete dönüştürür.
    
    Mantık şu: Eğer mesaj sayısı SUMMARIZE_THRESHOLD'u (40) aştıysa,
    son KEEP_RECENT (20) mesajı saklayıp öncesini özete dökeriz.
    
    Özetleme için modele 'şu mesajları 2-3 paragrafla özetle' diye ayrı
    bir istek atıyoruz. Bu özet history.json'a 'summary' alanına yazılır.
    Bir sonraki konuşmada bu özet, system prompt'un yanında modele veriliyor.
    
    Sonuç: Konuşma 200 mesaja ulaşsa bile model her şeyi hatırlıyor — son 20
    mesajı kelime kelime, öncesini özet olarak.
    """
    messages = history["messages"]
    
    # Henüz özetlemeye gerek yok
    if len(messages) < SUMMARIZE_THRESHOLD:
        return history
    
    print("\n[Sistem: Konuşma uzadı, eski mesajlar özetleniyor...]")
    
    # Özetlenecek eski mesajlar ve saklanacak son mesajlar
    old_messages = messages[:-KEEP_RECENT]
    recent_messages = messages[-KEEP_RECENT:]
    
    # Eski mesajları tek bir metne dönüştür (modelin özetlemesi için)
    conversation_text = ""
    for msg in old_messages:
        speaker = "Kullanıcı" if msg["role"] == "user" else "Karakter"
        conversation_text += f"{speaker}: {msg['content']}\n\n"
    
    # Önceki özet varsa onu da yeni özete dahil et (özetler birikmesin)
    previous_summary = history.get("summary", "")
    
    summarize_prompt = f"""Aşağıda iki kişi arasında geçen bir roleplay konuşması var. Bu konuşmayı, karakterin daha sonra hatırlayabileceği şekilde özetle.

ÖZET KURALLARI:
- 3-5 paragraf uzunluğunda olsun
- Önemli olayları, duyguları, kararları, sırları, paylaşılan anıları içersin
- Karakter ve kullanıcının ilişkisinin nasıl ilerlediğini göstersin
- Konuşmanın atmosferini ve tonunu koru
- Detaylar önemli ama özet olduğunu unutma — kısa cümleler, yoğun anlatım
- Türkçe yaz

{"ÖNCEKİ ÖZET (bunu da yeni özete dahil et, kaybetme):\n" + previous_summary + "\n\n" if previous_summary else ""}YENİ KONUŞMA:
{conversation_text}

ŞİMDİ ÖZETİ YAZ:"""
    
    # Modelden özet iste (ayrı bir chat çağrısı)
    summary_messages = [
        {"role": "system", "content": "Sen bir konuşma özetleyicisin. Verilen diyalogu anlamı ve duyguyu kaybetmeden özetlersin."},
        {"role": "user", "content": summarize_prompt}
    ]
    
    try:
        response = chat(summary_messages)
        new_summary = response.get("content", "").strip()
        
        # Geçmişi güncelle
        history["summary"] = new_summary
        history["messages"] = recent_messages
        save_history(history)
        
        print("[Sistem: Özet hazır, konuşma devam ediyor.]\n")
    except Exception as e:
        print(f"[Uyarı] Özetleme başarısız oldu: {e}")
        print("[Konuşma yine de devam edebilir, sadece eski mesajlar tutulmaya devam edecek.]\n")
    
    return history

# =========================================================
# ANA DÖNGÜ — Sohbet burada gerçekleşir
# =========================================================
def print_welcome(history):
    """Başlangıçta hoş bir karşılama ekranı bas.
    
    Eğer önceki bir konuşma varsa kaç mesaj ve ne zaman olduğunu söyler.
    Sıfırdan başlıyorsa karakteri ilk kez selamlamaya hazırlık yapar.
    """
    print("\n" + "═" * 55)
    print(f"  Roleplay Agent  ·  {MODEL}")
    print("═" * 55)
    
    msg_count = len(history["messages"])
    has_summary = bool(history.get("summary"))
    
    if msg_count == 0 and not has_summary:
        print("  Yeni bir hikaye başlıyor.")
    else:
        total = msg_count + (1 if has_summary else 0) * 20  # tahmini
        print(f"  Devam eden hikaye  ·  {msg_count} son mesaj kayıtlı")
        if has_summary:
            print("  (Daha eski olaylar özet halinde hatırlanıyor)")
        
        # Son mesajın zamanı
        if msg_count > 0:
            last = history["messages"][-1]
            if "time" in last:
                last_time = datetime.fromisoformat(last["time"])
                elapsed = datetime.now() - last_time
                if elapsed.days > 0:
                    print(f"  Son görüşme: {elapsed.days} gün önce")
                elif elapsed.seconds > 3600:
                    print(f"  Son görüşme: {elapsed.seconds // 3600} saat önce")
                else:
                    print(f"  Son görüşme: az önce")
    
    print("═" * 55)
    print("  Komutlar:  'q' = çıkış  ·  'reset' = hikayeyi sıfırla")
    print("═" * 55 + "\n")


def reset_history():
    """history.json dosyasını siler — temiz başlangıç için.
    
    Karakter dosyası kalır, sadece konuşma sıfırlanır. Bunu kullanıcı 
    'reset' yazarak tetikler. Onay sormamız akıllıca — yanlışlıkla 
    aylarca biriken hikaye silinmesin.
    """
    confirm = input("Tüm konuşma silinecek, emin misin? (evet/hayır): ").strip().lower()
    if confirm in ("evet", "e", "yes", "y"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        print("\n[Sistem: Hikaye sıfırlandı. Yeni bir başlangıç.]\n")
        return True
    else:
        print("[Sistem: İptal edildi, hikaye korunuyor.]\n")
        return False


def main():
    """Programın kalbi — burada sohbet döngüsü dönüyor.
    
    Her turda:
    1. Kullanıcıdan input al
    2. Komutsa işle (q, reset)
    3. Mesajsa: geçmişe ekle, modele gönder, cevabı al, geçmişe ekle
    4. Konuşma uzadıysa özetle
    """
    # Karakter ve geçmişi yükle
    system_prompt = load_character()
    history = load_history()
    
    print_welcome(history)
    
    while True:
        try:
            user_input = input("Sen: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Sistem: Hoşçakal. Hikaye kayıtlı, devam edebilirsin.]")
            break
        
        if not user_input:
            continue
        
        # Komutlar
        if user_input.lower() in ("q", "quit", "exit", "çık"):
            print("\n[Sistem: Hoşçakal. Hikaye kayıtlı, devam edebilirsin.]")
            break
        
        if user_input.lower() == "reset":
            if reset_history():
                history = {"summary": "", "messages": []}
            continue
        
        # Kullanıcı mesajını geçmişe ekle
        add_message(history, "user", user_input)
        
        # Modele gönderilecek mesaj listesini hazırla
        messages_for_model = build_messages_for_model(history, system_prompt)
        
        # Modele sor
        try:
            print()  # boş satır okumayı kolaylaştırır
            response = chat(messages_for_model)
            assistant_reply = response.get("content", "").strip()
            
            if not assistant_reply:
                print("[Uyarı] Model boş cevap verdi. Tekrar dener misin?\n")
                # Hatalı mesajı geçmişten çıkar
                history["messages"].pop()
                save_history(history)
                continue
            
            # Karakterin cevabını ekle
            add_message(history, "assistant", assistant_reply)
            
            print(f"{assistant_reply}\n")
            
        except Exception as e:
            print(f"\n[Hata] Model ile iletişimde sorun: {e}")
            print("Ollama çalışıyor mu? OLLAMA_HOST 127.0.0.1:11500 doğru mu?\n")
            # Cevapsız kalan kullanıcı mesajını geçmişten çıkar
            history["messages"].pop()
            save_history(history)
            continue
        
        # Konuşma uzadıysa özetle (sessizce arka planda)
        history = summarize_old_messages(history)


if __name__ == "__main__":
    main()