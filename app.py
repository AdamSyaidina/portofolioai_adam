from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from openai import OpenAI
from dotenv import load_dotenv
from flask_mail import Mail, Message
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# =========================
# OPENROUTER CONFIG
# =========================
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# =========================
# MAIL CONFIG
# =========================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASS")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("EMAIL_USER")

mail = Mail(app)

# =========================
# PROFILE DATA FOR CANNT
# =========================
profile_data = """
Nama lengkap: Muhammad Adam Syaidina
Nama panggilan: Adam

Deskripsi singkat:
Adam adalah mahasiswa S1 Teknik Telekomunikasi semester 6 di Telkom University Purwokerto dengan IPK 3.90.
Ia memiliki minat pada IoT, Web Development, Machine Learning, teknologi telekomunikasi, dan pengembangan sistem yang bermanfaat bagi masyarakat.

Fokus pengembangan:
- Internet of Things (IoT)
- Web Development
- Machine Learning
- Telekomunikasi
- Elektronika
- SDR dan Radio Frequency

Keahlian teknis:
- Python
- MATLAB
- Quartus
- GNU Radio
- RTL SDR
- IoT dasar
- Elektronika
- Sistem Digital
- Fiber Optic Installation
- Fiber Optic Troubleshooting
- TinkerCAD
- EagleCAD
- AutoCAD

Keahlian non-teknis:
- Komunikasi
- Kerja sama tim
- Kepemimpinan
- Tanggung jawab
- Adaptif
- Teliti
- Koordinasi
- Problem solving

Pengalaman kerja:
- Teknisi Lapangan / Jointer di PT Telkom Akses
- Fokus pada instalasi dan troubleshooting fiber optic

Pengalaman organisasi:
- Bendahara Umum Himpunan Mahasiswa Teknik Telekomunikasi
- Wakil Koordinator Asisten Praktikum
- Sekretaris Umum Grup Riset Hexacomm
- Ketua Umum UKM Manggala
- Project Leader NGO Sankara Regional Purwokerto

Pengalaman akademik:
- Asisten Praktikum Elektronika
- Asisten Praktikum Sistem Digital
- Asisten Praktikum RF
- Asisten Praktikum Bengkel Elektronika
- Membimbing lebih dari 25 praktikan

Sertifikasi:
- BNSP Jointer Fiber Optic Installation
- BNSP Radio Frequency Engineer

Karakter kerja:
Adam dikenal sebagai pribadi yang disiplin, bertanggung jawab, adaptif, komunikatif, teliti, dan mampu bekerja dalam tim.

Tujuan pengembangan:
Adam ingin terus mengembangkan kemampuan teknis sekaligus membangun karya yang bermanfaat, khususnya di bidang IoT, web, dan machine learning.
"""

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/experience")
def experience():
    return render_template("experience.html")

@app.route("/skill")
def skill():
    return render_template("skill.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# =========================
# CONTACT FORM
# =========================
@app.route("/send-message", methods=["POST"])
def send_message():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message_text = request.form.get("message", "").strip()

    if not name or not email or not subject or not message_text:
        flash("Semua field wajib diisi.", "error")
        return redirect(url_for("contact"))

    try:
        msg = Message(
            subject=f"[Portfolio Contact] {subject}",
            recipients=[os.getenv("RECEIVER_EMAIL", os.getenv("EMAIL_USER"))],
            reply_to=email
        )

        msg.body = f"""
Nama: {name}
Email: {email}
Subjek: {subject}

Pesan:
{message_text}
"""
        mail.send(msg)
        flash("Pesan berhasil dikirim.", "success")
        return redirect(url_for("contact"))

    except Exception as e:
        print("EMAIL ERROR:", e)
        flash(f"Gagal mengirim pesan: {str(e)}", "error")
        return redirect(url_for("contact"))

# =========================
# CANNT PROMPT
# =========================
def build_prompt(question):
    return f"""
Kamu adalah Cannt, asisten AI dari Muhammad Adam Syaidina.
Jika orang bertanya tentang Muhammad Adam Syaidina, sebut dia dengan nama panggilannya: Adam.

Tugas kamu adalah menjawab pertanyaan tentang Adam berdasarkan data yang tersedia.

Gaya jawaban:
- profesional
- ramah
- jujur
- natural
- singkat
- tidak berlebihan

Aturan penting:
- Jawab hanya berdasarkan data yang tersedia
- Jangan mengarang informasi
- Jangan melebih-lebihkan kemampuan, pengalaman, atau pencapaian Adam
- Jika informasi tidak tersedia, katakan dengan jujur bahwa informasinya belum tersedia
- Gunakan bahasa yang singkat, jelas, dan enak dibaca
- Maksimal 50 kata, idealnya 1–3 kalimat
- Jangan membuat jawaban terlalu formal atau kaku
- Jangan memakai poin-poin kecuali benar-benar diperlukan
- Fokus menjawab inti pertanyaan user
- Jika user bertanya kelebihan Adam, jawab dengan wajar dan realistis
- Jika user bertanya kekurangan atau hal yang belum dikuasai, jawab dengan netral dan sopan
- Jika user bertanya hal di luar topik Adam, arahkan kembali secara halus ke informasi tentang Adam
- Jangan terdengar seperti robot atau template otomatis
- Jika user bertanya dalam Bahasa Indonesia, jawab dalam Bahasa Indonesia
- Jika user bertanya dalam Bahasa Inggris, jawab dalam Bahasa Inggris

Jika user menyapa atau membuka percakapan:
- balas dengan ramah, singkat, dan perkenalkan diri sebagai Cannt
- setelah menyapa sekali, untuk pertanyaan berikutnya tidak perlu menyapa lagi

Jika user bertanya sesuatu yang ambigu:
- jawab dengan interpretasi paling masuk akal berdasarkan data Adam
- jangan meminta klarifikasi kecuali memang sangat perlu

Data utama:
{profile_data}

Pertanyaan:
{question}

Jawaban:
"""

# =========================
# AI CHAT ROUTE
# =========================
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Silakan masukkan pertanyaan terlebih dahulu."})

    prompt = build_prompt(question)

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        answer = "Maaf, Cannt sedang mengalami kendala."

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)