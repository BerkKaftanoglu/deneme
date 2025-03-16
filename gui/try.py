import google.generativeai as genai

API_KEY = "AIzaSyDk6qdkDkWUnLWiR99hrGSizYd7eI5qzYs"


genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# İstem (prompt) oluştur
prompt = "Bana kısa bir fıkra anlatır mısın?"

# Yanıtı al
response = model.generate_content(prompt)

# Yanıtı yazdır
print(response.text)