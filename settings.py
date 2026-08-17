import os

# Gemini API Anahtarı
# Öncelik terminal/çevre değişkenlerinde, eğer yoksa tırnak içine doğrudan yazabilirsin.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY")

# Motorların ortaklaşa kullanacağı güçlü ve kararlı güncel Gemini modeli
MODEL_NAME = "gemini-2.5-flash"