import gradio as gr
from gtts import gTTS
import os
import requests
import json
from dotenv import load_dotenv

# Load Hugging Face Token
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

class GenAIAssistant:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }

    def validate_claim(self, insurance_type, incident_description, language):
        keywords = {
            "Motor Insurance": {
                "en": ["car", "vehicle", "accident", "theft", "damage", "bike", "scooter"],
                "hi": ["कार", "वाहन", "दुर्घटना", "चोरी", "क्षति", "बाइक", "स्कूटर"]
            },
            "Health Insurance": {
                "en": ["hospital", "treatment", "medical", "illness", "surgery", "doctor"],
                "hi": ["अस्पताल", "उपचार", "चिकित्सा", "बीमारी", "सर्जरी", "डॉक्टर"]
            },
            "Crop Insurance": {
                "en": ["crop", "farmer", "drought", "flood", "pest", "harvest", "yield"],
                "hi": ["फसल", "किसान", "सूखा", "बाढ़", "कीट", "फसल कटाई", "उपज"]
            }
        }

        lang_code = "hi" if language == "Hindi" else "en"
        lower_desc = incident_description.lower()

        matched_keywords = [kw for kw in keywords[insurance_type][lang_code] if kw.lower() in lower_desc]
        if matched_keywords:
            return True, "Valid claim"

        for other_type, langs in keywords.items():
            if other_type == insurance_type:
                continue
            if any(kw.lower() in lower_desc for kw in langs[lang_code]):
                return False, (
                    f"आपके द्वारा दी गई जानकारी '{other_type}' से संबंधित लगती है। कृपया बीमा प्रकार '{other_type}' चुनें।"
                    if language == "Hindi"
                    else f"Your description seems related to '{other_type}'. Please select that insurance type instead."
                )

        return False, (
            "आपका विवरण किसी भी बीमा प्रकार से मेल नहीं खाता। कृपया अधिक स्पष्ट विवरण दें।"
            if language == "Hindi"
            else "Your description doesn't clearly match any insurance type. Please provide more specific details."
        )

    def query_genai(self, prompt):
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt}
            )
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"]
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            elif isinstance(result, dict) and "choices" in result:
                return result["choices"][0]["text"]
            else:
                return f"⚠️ Unexpected response: {result}"
        except Exception as e:
            return f"⚠️ GenAI error: {str(e)}"

    def clean_output(self, raw_response):
        lines = raw_response.strip().splitlines()
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if any(phrase in line.lower() for phrase in [
                "you are", "user:", "assistant:", "describe the incident", "claiming insurance",
                "please help", "write in", "step-by-step", "instructions", "please explain",
                "act as", "question:"
            ]):
                continue
            if len(line) > 0:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def generate_personalized_guidance(self, language, insurance_type, incident, justification):
        is_valid, validation_msg = self.validate_claim(insurance_type, incident, language)
        if not is_valid:
            return validation_msg

        prompt = f"""You are an Indian insurance advisor. A user has selected "{insurance_type}".
They describe the incident as: "{incident}"
They are claiming insurance because: "{justification}"

Please help the user by explaining in simple, step-by-step instructions:
- What to do first
- Which documents are needed
- Where and how to submit the claim
- Approximate processing time
- Tips to avoid delays

Please write in {language} in clear and easy language. Avoid legal terms or technical jargon.
**Do not repeat or include this instruction in your response. Follow the instructions, but don’t echo them.**
"""
        raw_response = self.query_genai(prompt)
        return self.clean_output(raw_response)

# === UI Configuration ===

insurance_data = {
    "English": {
        "types": ["Motor Insurance", "Health Insurance", "Crop Insurance"],
        "labels": {
            "select_language": "Select Language",
            "insurance_info": "Insurance Information (India Specific)",
            "select_insurance": "Select Insurance Type",
            "describe_incident": "Describe your incident",
            "incident_placeholder": "e.g., My car was damaged in an accident...",
            "justify_claim": "Why are you claiming insurance?",
            "justify_placeholder": "e.g., I need repair costs covered...",
            "submit": "Get AI Guidance",
            "ai_guidance": "AI-Powered Guidance (Indian Context)",
            "voice_guidance": "Voice Guidance"
        }
    },
    "Hindi": {
        "types": ["मोटर बीमा", "स्वास्थ्य बीमा", "फसल बीमा"],
        "labels": {
            "select_language": "भाषा चुनें",
            "insurance_info": "बीमा जानकारी (भारत विशिष्ट)",
            "select_insurance": "बीमा प्रकार चुनें",
            "describe_incident": "अपनी घटना का वर्णन करें",
            "incident_placeholder": "उदाहरण: मेरी कार एक दुर्घटना में क्षतिग्रस्त हो गई...",
            "justify_claim": "आप बीमा क्लेम क्यों कर रहे हैं?",
            "justify_placeholder": "उदाहरण: मुझे मरम्मत की लागत चाहिए...",
            "submit": "AI मार्गदर्शन प्राप्त करें",
            "ai_guidance": "AI-संचालित मार्गदर्शन (भारतीय संदर्भ)",
            "voice_guidance": "आवाज़ मार्गदर्शन"
        }
    }
}

genai_assistant = GenAIAssistant()

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang='hi' if lang == "Hindi" else 'en', slow=False)
        filename = "guidance_output.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        return None

def process_claim(language, insurance_type, incident, justification):
    if not all([language, insurance_type, incident, justification]):
        return (
            "⚠️ कृपया सभी फ़ील्ड भरें" if language == "Hindi" else "⚠️ Please fill all fields",
            None
        )
    try:
        type_mapping = {
            "मोटर बीमा": "Motor Insurance",
            "स्वास्थ्य बीमा": "Health Insurance",
            "फसल बीमा": "Crop Insurance"
        }
        processed_type = type_mapping.get(insurance_type, insurance_type)

        ai_guidance = genai_assistant.generate_personalized_guidance(
            language, processed_type, incident, justification
        )

        audio_path = text_to_speech(ai_guidance, language)
        return ai_guidance, audio_path
    except Exception as e:
        return (
            f"⚠️ त्रुटि हुई: {str(e)}" if language == "Hindi" else f"⚠️ Error occurred: {str(e)}",
            None
        )

# === Gradio UI ===
with gr.Blocks(title="Bharat Insurance Claim Saathi", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🇮🇳 Bharat Insurance Claim Saathi")
    gr.Markdown("### AI-Powered Multilingual Insurance Claim Assistant for Indian Policies")

    language = gr.Radio(["English", "Hindi"], label="Select Language / भाषा चुनें", value="English")

    insurance_type = gr.Dropdown(
        choices=insurance_data["English"]["types"],
        label="Select Insurance Type"
    )

    incident = gr.Textbox(
        label="Describe your incident",
        lines=4,
        placeholder="e.g., My car was damaged in an accident..."
    )

    justification = gr.Textbox(
        label="Why are you claiming insurance?",
        lines=3,
        placeholder="e.g., I need repair costs covered..."
    )

    submit_btn = gr.Button("Get AI Guidance", variant="primary", size="lg")

    with gr.Row():
        with gr.Column():
            output_text = gr.Textbox(
                label="🤖 AI-Powered Guidance (Indian Context)",
                lines=15,
                interactive=False
            )
        with gr.Column():
            audio_output = gr.Audio(label="🔊 Voice Guidance")

    def update_interface(lang):
        labels = insurance_data[lang]["labels"]
        return [
            gr.Dropdown.update(choices=insurance_data[lang]["types"], label=labels["select_insurance"]),
            gr.Textbox.update(label=labels["describe_incident"], placeholder=labels["incident_placeholder"]),
            gr.Textbox.update(label=labels["justify_claim"], placeholder=labels["justify_placeholder"]),
            gr.Button.update(value=labels["submit"]),
            gr.Textbox.update(label=labels["ai_guidance"]),
            gr.Audio.update(label=labels["voice_guidance"])
        ]

    language.change(
        fn=update_interface,
        inputs=[language],
        outputs=[insurance_type, incident, justification, submit_btn, output_text, audio_output]
    )

    submit_btn.click(
        fn=process_claim,
        inputs=[language, insurance_type, incident, justification],
        outputs=[output_text, audio_output]
    )

    # === Small Chatbot Box Below ===
    gr.Markdown("### 🤝 Need Help? Chat with our AI Assistant")
    chatbot = gr.Chatbot(label="💬 BharatBot Help Assistant")
    chat_input = gr.Textbox(label="Ask your question", placeholder="e.g., What documents are needed for motor insurance?", lines=1)
    send_btn = gr.Button("Ask")

    def chatbot_reply(message, lang):
        allowed_keywords = {
            "en": ["motor", "health", "crop", "vehicle", "car", "bike", "doctor", "hospital", "treatment", "farmer", "flood", "drought"],
            "hi": ["मोटर", "स्वास्थ्य", "फसल", "कार", "बाइक", "डॉक्टर", "अस्पताल", "किसान", "बाढ़", "सूखा"]
        }
        lang_code = "hi" if lang == "Hindi" else "en"
        if not any(keyword in message.lower() for keyword in allowed_keywords[lang_code]):
            return [(message, "⚠️ केवल मोटर, स्वास्थ्य या फसल बीमा से संबंधित प्रश्न पूछें।" if lang == "Hindi"
                    else "⚠️ Please ask only about Motor, Health, or Crop insurance.")]

        prompt = f"""You are an Indian insurance assistant.
Only answer questions related to insurance in India (Motor, Health, Crop only).
User asked in {lang}.
Answer in {lang} only in clear and helpful way.
Question: {message}"""

        raw_response = genai_assistant.query_genai(prompt)
        response = genai_assistant.clean_output(raw_response)
        return [(message, response)]

    send_btn.click(
        fn=chatbot_reply,
        inputs=[chat_input, language],
        outputs=chatbot
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)