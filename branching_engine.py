import json
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY, MODEL_NAME
from .models import NarrativeNode

# Google GenAI SDK Client bağlantısı
client = genai.Client(api_key=GEMINI_API_KEY)


class BranchingEngine:
    """Yazarın alternatif kurgu yolları (Ya Şöyle Olsaydı) denemesini sağlayan Dallanma Motoru"""

    @staticmethod
    def simulate_branch(current_node: NarrativeNode, alternative_choice: str, raw_chars: list = None, raw_lore: list = None) -> dict:
        """Yazarın seçtiği alternatif yolun evrene, karakter günahlarına ve sirlarina etkisini simüle eder"""

        # Karakter ve Evren kurallarını metne dönüştürüp Gemini'a vereceğiz
        char_context = ""
        if raw_chars:
            char_context = "\n--- EVRENDEKİ AKTİF KARAKTERLER VE SIRLARI ---\n"
            for c in raw_chars:
                # Modellerde hem nesne hem dict gelebileceği için esnek yapı
                name = c.name if hasattr(c, 'name') else c.get('name', 'Bilinmeyen')
                traits = c.traits if hasattr(c, 'traits') else c.get('traits', [])
                secrets = c.secrets if hasattr(c, 'secrets') else c.get('secrets', [])
                char_context += f"• Karakter: {name} | Kişilik: {', '.join(traits)} | Karanlık Geçmişi/Sırları: {', '.join(secrets)}\n"

        lore_context = ""
        if raw_lore:
            lore_context = "\n--- EVRENİN KATI KURALLARI VE MİTOLOJİSİ ---\n"
            for l in raw_lore:
                desc = l.description if hasattr(l, 'description') else l.get('description', '')
                lore_context += f"• Kurul: {desc}\n"

        system_instruction = (
            "Sen MGPE projesinin Kreatif Anlatı Dallanma Motorusun.\n"
            "Görevin, yazarın ana kurguya alternatif olarak sunduğu kararı/yolu incelemektir.\n"
            "Bunu yaparken, karakterlerin 'Karanlık Geçmişi ve Sırları' ile 'Evren Kuralları' dökümünü mutlaka dikkate almalısın.\n"
            "Karakterler kendi zaaflarına, günahlarına ve psikolojilerine uygun tepkiler vermelidir.\n"
            "Yapay zeka olarak metin yazma, sadece olasılık düğümleri üret.\n\n"
            "Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir metin yazma:\n"
            "{\n"
            "  \"impact_analysis\": \"Bu alternatif seçimin karakterlerin psikolojik sırlarıyla çelişip çelişmediği ve kurgu üzerindeki genel etkisi.\",\n"
            "  \"metric_changes\": {\n"
            "    \"karakter_ilişkileri\": \"Seviye değişimi (Örn: +20 Güven veya -10 Bağlılık gibi açıklayıcı bir not)\",\n"
            "    \"kaos_seviyesi\": \"Değişim notu\"\n"
            "  },\n"
            "  \"possible_future_events\": [\"Bu seçim yapılırsa gelecekte tetiklenebilecek olası 1. olay\", \"2. olay\"]\n"
            "}"
        )

        prompt = (
            f"Mevcut Sahne Başlığı: {current_node.title}\n"
            f"Mevcut Sahne İçeriği: {current_node.content}\n"
            f"{char_context}"
            f"{lore_context}\n"
            f"Yazarın Denemek İstediği Alternatif Yol: {alternative_choice}\n"
        )

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            )

            return json.loads(response.text.strip())

        except Exception as e:
            return {
                "impact_analysis": f"⚠️ Simülasyon esnasında bir hata oluştu: {str(e)}",
                "metric_changes": {"karakter_ilişkileri": "Değişmedi", "kaos_seviyesi": "Değişmedi"},
                "possible_future_events": ["Hata nedeniyle gelecek senaryoları üretilemedi."]
            }