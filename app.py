from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Veritabanı oluştur
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/anket", methods=["GET", "POST"])
def anket():
    if request.method == "POST":
        toplam = 0
        for i in range(1, 11):
            toplam += int(request.form.get(f"q{i}", 0))

        # Veritabanına kaydet
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO results (score) VALUES (?)", (toplam,))
        conn.commit()
        conn.close()

        # Değerlendirme
        if toplam <= 10:
            durum = "İşitme açısından belirgin bir sorun görünmüyor."
            renk = "green"
        elif toplam <= 20:
            durum = "Hafif düzeyde işitme problemi olabilir. Takip önerilir."
            renk = "orange"
        else:
            durum = "⚠️ İşitme kaybı riski yüksek! Uzman hekime başvurmanız önerilir."
            renk = "red"

        return render_template("tesekkur.html", skor=toplam, durum=durum, renk=renk)

    return render_template("anket.html")

@app.route("/bilgilendirme")
def bilgilendirme():
    return render_template("bilgilendirme.html")


@app.route("/sss")
def sss():
    return render_template("sss.html")

@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*), AVG(score) FROM results")
    count, avg = c.fetchone()

    c.execute("SELECT COUNT(*) FROM results WHERE score <= 10")
    green = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM results WHERE score BETWEEN 11 AND 20")
    yellow = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM results WHERE score >= 21")
    red = c.fetchone()[0]

    conn.close()

    return render_template("admin_panel.html",
                           count=count or 0,
                           avg=round(avg, 2) if avg else 0,
                           green=green,
                           yellow=yellow,
                           red=red)

if __name__ == "__main__":
    app.run(debug=True)
