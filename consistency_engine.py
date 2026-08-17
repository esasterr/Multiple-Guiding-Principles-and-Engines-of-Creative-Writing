from google import genai
from pydantic import BaseModel
from typing import List
from config.settings import GEMINI_API_KEY, MODEL_NAME


# Yapay zekanın vereceği cevabın şablonunu (Pydantic ile) kilitliyoruz
class ConsistencyAnalysis(BaseModel):
    anomalies: List[str]
    new_debts: List[str]
    scene_time: str


class ConsistencyEngine:
    @staticmethod
    def analyze_scene(current_scene, global_debts, raw_chars, raw_lore, past_timeline):
        # Her analizde taze bir client ayağa kaldırıyoruz
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 1. Aktif soru ve gizemleri temiz metne çeviriyoruz
        active_debts_str = "\n".join([f"- {d.description}" for d in global_debts if not d.is_resolved])

        # 2. Karakter nesnelerini yapay zekanın okuyabileceği yapıya dönüştürüyoruz
        chars_list = []
        if raw_chars:
            for c in raw_chars:
                name = c.name if hasattr(c, 'name') else c.get('name', 'Bilinmeyen')
                traits = c.traits if hasattr(c, 'traits') else c.get('traits', [])
                secrets = c.secrets if hasattr(c, 'secrets') else c.get('secrets', [])
                chars_list.append(f"• İsim: {name} | Kişilik: {', '.join(traits)} | Karanlık Sırları: {', '.join(secrets)}")
        chars_str = "\n".join(chars_list) if chars_list else "Karakter verisi girilmemiş."

        # 3. Evren kurallarını (Lore) temiz metne çeviriyoruz
        lore_list = []
        if raw_lore:
            for l in raw_lore:
                desc = l.description if hasattr(l, 'description') else l.get('description', '')
                lore_list.append(f"- {desc}")
        lore_str = "\n".join(lore_list) if lore_list else "Evren kuralı girilmemiş."

        # 4. Geçmiş zaman çizelgesini okunabilir yapıyoruz
        timeline_str = ", ".join(past_timeline) if past_timeline else "Bu evrendeki ilk sahne."

        prompt = (
            f"--- YENİ YAZILAN SAHNE ---\n"
            f"Başlık: {current_scene.title}\n"
            f"İçerik:\n\"{current_scene.content}\"\n\n"
            f"--- MEVCUT EVREN BİLGİLERİ ---\n"
            f"Geçmiş Sahne Sıralaması: {timeline_str}\n\n"
            f"Aktif Soru/Gizemler (Yanıtlanması Gerekenler):\n{active_debts_str}\n\n"
            f"Karakterler ve Karanlık Geçmişleri:\n{chars_str}\n\n"
            f"Evren Kuralları (Lore):\n{lore_str}\n\n"
            f"GÖREVİN:\n"
            f"1. Yeni yazılan sahneyi evren kuralları, karakter özellikleri, gizli sırları ve geçmişle kıyasla. Eğer yazar karakterin psikolojisine veya evren kurallarına bariz bir çelişki yazdıysa bunu 'anomalies' listesine ekle. Yoksa boş bırak.\n"
            f"2. Hikayede ucu açık bırakılan, okuyucunun ileride merak edeceği yeni gizemleri/soruları tespit et ve 'new_debts' listesine ekle.\n"
            f"3. Sahne metninden yola çıkarak zamanı/mekanı tahmin et (Örn: 'Gece', 'Ertesi Gün Sabah') ve 'scene_time' alanına yaz."
        )

        try:
            # Gemini'ye katı şema zorunluluğu uyguluyoruz
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "system_instruction": "Sen hikayedeki mantık hatalarını, karakter çelişkilerini bulan ve yeni gizem soruları üreten keskin gözlü bir MGPE editörüsün.",
                    "response_mime_type": "application/json",
                    "response_schema": ConsistencyAnalysis,
                }
            )

            # Şemaya göre otomatik olarak ayrıştırılan veri
            result = response.parsed

            # main.py sırasıyla 4 değer bekliyor: anomalies, rel_updates, new_debts, scene_time
            return result.anomalies, {}, result.new_debts, result.scene_time

        except Exception as e:
            print(f"\n⚠️ [MGPE Sistem Uyarısı]: API bağlantısında anlık bir aksama oldu: {str(e)}")
            return ["⚠️ Sunucu yoğunluğu veya format uyuşmazlığı nedeniyle analiz atlandı."], {}, [], "Belirtilmedi"