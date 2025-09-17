import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()
app = Flask(__name__)

# โหลด FAQ JSON
with open("faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# เก็บ history ของบทสนทนา
chat_history = []

def find_relevant_faq(user_text):
    """ค้นหา FAQ ที่เกี่ยวข้อง"""
    user_text_lower = user_text.lower()
    relevant_answers = []
    for item in faq_data:
        if any(word in user_text_lower for word in item["question"].lower().split()):
            relevant_answers.extend(item["answer"])
    return relevant_answers

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def message():
    user_input = request.json.get("text")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    relevant_answers = find_relevant_faq(user_input)
    context_text = "\n".join(relevant_answers) if relevant_answers else "ไม่มีข้อมูลตรง"

    # สร้าง prompt ให้ Gemini ตอบแบบสั้น ๆ เป็นบทสนทนา
    prompt = f"""
คุณคือ “ที่ปรึกษากิจการนิสิตมหาวิทยาลัยนเรศวร”
ตอบคำถามนิสิตอย่างเป็นมิตร ชัดเจน เหมือนเจ้าหน้าที่จริง
ตอบแต่ละข้อความไม่เกิน 2-3 ประโยค ตอบสั้น ๆ กระชับ
ถ้ามีหลายขั้นตอน ให้แยกเป็นข้อ ๆ
ถ้าคำถามไม่เกี่ยวกับกิจการนิสิต ให้ตอบว่า "ขออภัย ไม่สามารถตอบได้"
ข้อมูลอ้างอิงที่คุณมี: {context_text}
นี่คือบทสนทนาก่อนหน้า: {chat_history}
User: {user_input}
ตอบเป็นภาษาไทยเหมือนสนทนาและเหมือนเจ้าหน้าที่:
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply = response.text.strip()
        # เพิ่มลง history
        chat_history.append({"user": user_input, "assistant": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "ขออภัย เกิดข้อผิดพลาด: " + str(e)})

if __name__ == "__main__":
    app.run(debug=True)