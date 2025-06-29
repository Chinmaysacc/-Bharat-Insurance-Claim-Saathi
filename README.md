# 🇮🇳 Bharat Insurance Claim Saathi

**AI-Powered Multilingual Insurance Claim Assistant for Indian Policies**

This project is a user-friendly insurance assistant that simplifies **Motor**, **Health**, and **Crop Insurance** claims in **English** and **Hindi**. It provides step-by-step guidance, validates user input based on context, and even speaks the response using voice assistance.

---

## 🧠 What This Project Does

- ✅ Validates if the user-selected insurance type matches their description.
- 📜 Provides **step-by-step guidance** based on user input.
- 🎙️ Converts guidance into **spoken audio** using text-to-speech.
- 🗣️ Supports **English** and **Hindi**, adapting both UI and output.
- 🤖 Chatbot handles follow-up queries related to insurance types.

---

## 🔁 Project Workflow

1. **User selects language** – English or Hindi.
2. **Chooses Insurance Type** – Motor, Health, or Crop.
3. **Enters description** of the incident and **justification**.
4. **System validates** whether the description matches the insurance type.
   - If mismatched, user is prompted to correct the selection.
5. If valid, the **prompt is sent to the Hugging Face GenAI model**.
6. GenAI responds with **custom instructions** tailored to the user’s scenario.
7. The response is **cleaned**, and **voice output is generated**.
8. A **chatbot** allows users to ask more questions regarding insurance.

---

## 🖼️ Use Case Examples

### 🔹 Motor Insurance – English
- **Describe your incident**: My car was hit by another vehicle while parked outside my office.  
- **Why are you claiming insurance?**: I want to cover the repair costs.

### 🔸 फसल बीमा – Hindi
- **अपनी घटना का वर्णन करें**: भारी बारिश से मेरी पूरी फसल बर्बाद हो गई।  
- **आप बीमा क्लेम क्यों कर रहे हैं?**: नुकसान की भरपाई के लिए।

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Gradio** | UI development |
| **Python** | Core programming language |
| **gTTS** | Text-to-speech (audio guidance) |
| **Hugging Face API** | GenAI model (Mixtral-8x7B-Instruct) |
| **dotenv** | Secure token storage via `.env` |

---

## 🗝️ How to Generate a Hugging Face Access Token

👉 **Generate your token here:** [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Steps:
1. Login or Sign up at Hugging Face.
2. Go to [Access Tokens](https://huggingface.co/settings/tokens).
3. Click on **"New Token"**.
4. Choose **"Read"** role and create it.
5. Copy the token.
6. Create a `.env` file and paste:

## NOTE: 
1. DO GENERATE YOUR OWN KEY USING ABOVE STEPS BEFORE RUNNING THE CODE.
2. 2.SOMETIME THE SITE GIVES A JSON ERROR. IF IT HAPPENS, REFRESH THE SITE.
