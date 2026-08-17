# core_engines/stylometric_engine.py
from google import genai
from pydantic import BaseModel
from typing import List
from config.settings import GEMINI_API_KEY, MODEL_NAME


# Eleştiri raporunun tam olarak hangi bilgileri içereceğini netleştiriyoruz
class StyleAnalysis(BaseModel):
    atmosphere_score: int
    dialogue_score: int
    pacing_score: int
    critique: str
    suggestions: List[str]


class StylometricEngine:
    @staticmethod
    def analyze_style(content: str):
        # Taze bir client ayağa kaldırıyoruz
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = (
            f"Aşağıdaki roman sahnesi metnini edebi açıdan derinlemesine incele:\n\n"
            f"\"{content}\"\n\n"
            f"GÖREVİN:\n"
            f"1. Sahnenin atmosferini ve betimleme kalitesini incele, 0-100 arası bir skor ver (atmosphere_score).\n"
            f"2. Eğer sahnede diyalog varsa doğallığını ve karakter seslerini incele, yoksa anlatıcının dilini puanla (dialogue_score).\n"
            f"3. Sahnenin temposunu, olayların akış hızını incele ve 0-100 arası bir skor ver (pacing_score).\n"
            f"4. Yazarın üslubunu geliştirebilmesi için dürüst, yapıcı ve edebi bir eleştiri yaz (critique). Kelime tekrarları, 'Göstermek yerine söylemek' (Show don't tell) hataları veya zayıf tasvirler varsa acımasızca ama yapıcı şekilde belirt.\n"
            f"5. Sahneyi daha vurucu, daha edebi hale getirecek en az 2 adet net ve somut öneriyi 'suggestions' listesine ekle."
        )

        try:
            # Gemini'ye katı şema uygulayarak eleştiri yapmasını zorunlu kılıyoruz
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "system_instruction": "Sen usta bir yayın evi editörü ve edebi stil analistisin. Yazara karşı dürüst, seçici ve derinlemesine edebi eleştiriler sunarsın.",
                    "response_mime_type": "application/json",
                    "response_schema": StyleAnalysis,
                }
            )

            # Gelen veriyi çözüyoruz
            result = response.parsed
            return {
                "atmosphere_score": result.atmosphere_score,
                "dialogue_score": result.dialogue_score,
                "pacing_score": result.pacing_score,
                "critique": result.critique,
                "suggestions": result.suggestions
            }

        except Exception as e:
            return {
                "atmosphere_score": 50,
                "dialogue_score": 50,
                "pacing_score": 50,
                "critique": f"Edebi analiz motorunda anlık bir sorun oluştu: {str(e)}",
                "suggestions": ["Analizi daha sonra tekrar deneyebilirsiniz."]
            }

