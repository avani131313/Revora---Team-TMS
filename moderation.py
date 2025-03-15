import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDzZaW-lhjkolxgg0RgV-hfBHaqel1t3Wk"
genai.configure(api_key=GEMINI_API_KEY)

def is_content_appropriate(content):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Use the Gemini model
    prompt = f"Check if the following text is appropriate for a cancer support community. \
               Respond only with 'Yes' or 'No'.\n\nText: {content}"

    response = model.generate_content(prompt)
    return "yes" in response.text.lower()
