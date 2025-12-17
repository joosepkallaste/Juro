"""
*Senine koostöö on sujunud meil hästi. Kindlaid rolle meil pole. Tuleb mõni hea idee, mida teha siis pakub välja. Oleneb kummal antud hetkel rohkem aega on, see tegeleb.
*Projektile on kulun hetkeseisuga ligikaudu 10 tundi. Põhiliselt planeerimise ja erinevate vahendite ning teekide uurimisele, mida võiks projekti jaoks kasutada.
*Plaanime menüüd täiendada, lisada kujunduse, luua võimaluse valida eesti ja inglise keele vahel, mõte lisada võimalus lihtsalt sisestada link kuulutusele ning programm
võtab sealt automaatselt nõuded, et teha protsess kiiremaks. Saad salvestada oma andmeid, et ei peaks neid iga kord sisestama.
"""




import tkinter as tk
from tkinter import Menubutton, Menu, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import sqlite3
from datetime import datetime

DB_PATH = "kandideerimismasin.db"


"""Andmebaas kaaskirjade salvestamiseks, otsin töötab nime alusel. Otsing: Nimi --> Ettevõte --> Loodud kaaskirjad. 
    Vajadusel saab sama nime ja ettevõtte kombinatsiooni puhul olemasolevat kirja uuendada ehk asendada uue versiooniga. 
    Kasutasin sqlite3 kuna see ei vaja eraldi serverit, töötab ühe failina, sobib hästi desktop rakenduse andmete hoidmiseks """
    
"""Funktsioon loob andmebaasi kui seda veel ei ole"""
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nimi TEXT NOT NULL,
            ettevõte TEXT NOT NULL,
            kirja_text TEXT NOT NULL,
            loodud_at TEXT NOT NULL,
            UNIQUE(nimi, ettevõte)
        )
        """)


"""Salvestamis funktsioon: salvestab kaaskirja andmebaasi nime + ettevõtte võtme järgi."""
def salvesta_kiri(nimi: str, ettevõte: str, kirja_text: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO letters(nimi, ettevõte, kirja_text, loodud_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(nimi, ettevõte)
            DO UPDATE SET kirja_text=excluded.kirja_text, loodud_at=excluded.loodud_at
        """, (nimi, ettevõte, kirja_text, datetime.now().isoformat(timespec="seconds")))


"""list_nimi func: tagastab andmebaasist kõik unikaalsed nimed"""
def list_nimi():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT DISTINCT nimi FROM letters ORDER BY nimi")
        return [r[0] for r in cur.fetchall()]
    
    
"""list_ettevõte func: kui kasutaja on valinud nime, siis see funktsioon toob kõik ettevõtted, 
    mille alla selle nimega on kirju salvestatud"""
def list_ettevõte(nimi: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            SELECT ettevõte FROM letters
            WHERE nimi=?
            ORDER BY ettevõte
        """, (nimi,))
        return [r[0] for r in cur.fetchall()]


"""list_kiri func: toob andmebaasist konkreetse kaaskirja teksti, mis vastab valitud nimele ja ettevõttele."""
def list_kiri(nimi: str, ettevõte: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            SELECT kirja_text FROM letters
            WHERE nimi=? AND ettevõte=?
        """, (nimi, ettevõte))
        row = cur.fetchone()
        return row[0] if row else None


"""Põhiaken"""
root = tk.Tk()
root.title("Kandideerimismasin")
root.geometry("400x200")

def vaata_salvestatud_kaaskirju():
    win = tk.Toplevel(root)
    win.title("Salvestatud kaaskirjad")
    win.geometry("800x600")

    ttk.Label(win, text="Nimi:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
    nimi_cb = ttk.Combobox(win, width=40, values=list_nimi(), state="readonly")
    nimi_cb.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

    ttk.Label(win, text="Ettevõte:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
    ettevote_cb = ttk.Combobox(win, width=40, values=[], state="readonly")
    ettevote_cb.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

    text = tk.Text(win, wrap="word", height=25)
    text.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
    """Uuendab kirja"""
    def värskenda_ettevõte(event=None):
        person = nimi_cb.get()
        companies = list_ettevõte(person) if person else []
        ettevote_cb["values"] = companies
        ettevote_cb.set("")
        text.delete("1.0", tk.END)
    """Avab kirja"""
    def ava_kiri(event=None):
        person = nimi_cb.get()
        company = ettevote_cb.get()
        if not (person and company):
            return
        letter = list_kiri(person, company)
        text.delete("1.0", tk.END)
        text.insert("1.0", letter or "")

    nimi_cb.bind("<<ComboboxSelected>>", värskenda_ettevõte)
    ettevote_cb.bind("<<ComboboxSelected>>", ava_kiri)

    ttk.Button(win, text="🔄 Värskenda", command=lambda: nimi_cb.configure(values=list_nimi())).grid(row=0, column=2, padx=8)
    ttk.Button(win, text="📂 Ava", command=ava_kiri).grid(row=1, column=2, padx=8)

    win.grid_columnconfigure(1, weight=1)
    win.grid_rowconfigure(2, weight=1)


"""FUNKTSIOON: Loo kaaskirja aken"""
def kaaskiri_vorm():
    """Avab eraldi akna (Toplevel), kus saab kaaskirja väljad täita."""
    win = tk.Toplevel(root)
    win.title("Kaaskiri")
    win.geometry("700x600")

    """väljade nimed ja võtmed"""
    fields = [
        ("Täisnimi", "nimi", "entry"),
        ("Ettevõte", "ettevote", "entry"),
        ("Esindaja ametikoht", "esindajaAmetikoht", "entry"),
        ("Esindaja nimi", "esindajaNimi", "entry"),
        ("Ametikoht (kuhu kandideerid)", "ametikoht", "entry"),
        ("Nõuded kandidaadile", "noudedKandidaadile", "text"),
        ("Miks sobid", "miksMina", "text"),
        ("E-mail", "gmail", "entry"),
        ("Telefon (+372…)", "tel", "entry"),
    ]

    entries = {}

    for r, (label, key, field_type) in enumerate(fields):
        tk.Label(win, text=label + ":").grid(row=r, column=0, sticky="w", padx=8, pady=4)

        if field_type == "entry":
            e = ttk.Entry(win, width=50)
            e.grid(row=r, column=1, padx=8, pady=4, sticky="ew")
            entries[key] = e
        else:
            frame = ttk.Frame(win)
            frame.grid(row=r, column=1, padx=8, pady=4, sticky="ew")
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side="right", fill="y")
            t = tk.Text(frame, width=50, height=5, wrap="word", yscrollcommand=scrollbar.set)
            t.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=t.yview)
            entries[key] = t

    """FUNKTSIOON: Kaaskirja koostamine"""
    def koosta_kiri():
        # loe väärtused
        def get_value(key):
            widget = entries[key]
            if isinstance(widget, tk.Text):
                return widget.get("1.0", tk.END).strip()
            else:
                return widget.get().strip()

        nimi = get_value("nimi")
        ettevote = get_value("ettevote")
        esindajaAmetikoht = get_value("esindajaAmetikoht")
        esindajaNimi = get_value("esindajaNimi")
        ametikoht = get_value("ametikoht")
        noudedKandidaadile = get_value("noudedKandidaadile")
        miksMina = get_value("miksMina")
        gmail = get_value("gmail")
        tel = get_value("tel")

        # Lihtne kontroll, et kõik oleks täidetud
        if not all([nimi, ettevote, esindajaAmetikoht, esindajaNimi,
                    ametikoht, noudedKandidaadile, miksMina, gmail, tel]):
            messagebox.showerror("Viga", "Palun täida kõik väljad.")
            return

        kiri = f"""Lugupeetud {ettevote} {esindajaAmetikoht} {esindajaNimi}

Soovin kandideerida Teie väljakuulutatud {ametikoht} ametikohale.

Kuigi kirjale lisatud CV annab ülevaate minu varasemast töökogemusest,
haridusest, täiendõppest ja tööks vajalikest oskustest, tõin välja
töökuulutuses olevad nõudmised ja vastavad oskused nendel aladel:

• {noudedKandidaadile}

Leian, et lisaks töökuulutuses toodud nõuete täitmisele olen sellele
ametikohale sobiv kandidaat, sest {miksMina}.

Olen meeleldi nõus vastama tekkivatele küsimustele Teile sobival ajal e-maili
{gmail} või telefoni {tel} teel! Ootan Teiega kohtumist, et rääkida põhjalikumalt
pakutavast ametikohast ja põhjustest, miks leian, et olen Teie ettevõttesse
sobiv inimene.

Lugupidamisega,
{nimi}"""

        """Kuvame kirja uues aknas"""
        win_kiri = tk.Toplevel(win)
        win_kiri.title("Valmis kaaskiri")
        win_kiri.geometry("700x600")

        text = tk.Text(win_kiri, wrap="word", width=80, height=25)
        text.insert("1.0", kiri)
        text.pack(padx=10, pady=10, fill="both", expand=True)
        def salvesta_db():
            salvesta_kiri(nimi, ettevote, kiri)
            messagebox.showinfo("Salvestatud", f"Kaaskiri salvestatud: {nimi} → {ettevote}")

        ttk.Button(win_kiri, text="🗄️ Salvesta andmebaasi", command=salvesta_db).pack(pady=5)

        """TXT ja PDF salvestus"""
        def salvesta_txt():
            with open(f"{ettevote}.txt", "w", encoding="utf-8") as f:
                f.write(kiri)
            messagebox.showinfo("Salvestatud", f"Kaaskiri salvestati faili {ettevote}.txt.")

        def salvesta_pdf():
            pdf_fail = f"{ettevote}.pdf"

            # Registreerib fondi, try/except hoiab ära topelt registreerimise
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
            except:
                pass

            c = canvas.Canvas(pdf_fail, pagesize=A4)
            c.setFont("DejaVu", 11)

            width, height = A4
            x = 50
            y = height - 50
            line_height = 14

            for line in kiri.splitlines():
                c.drawString(x, y, line)
                y -= line_height

                # lihtne lehevahetus, kui leht täis
                if y < 50:
                    c.showPage()
                    c.setFont("DejaVu", 11)
                    y = height - 50

            c.save()
            messagebox.showinfo("Salvestatud", f"Kaaskiri salvestatud faili '{pdf_fail}'.")

        ttk.Button(win_kiri, text="💾 Salvesta TXT", command=salvesta_txt).pack(pady=5)
        ttk.Button(win_kiri, text="📄 Salvesta PDF", command=salvesta_pdf).pack(pady=5)

    """Nupp kirja koostamiseks"""
    ttk.Button(win, text="Koosta kiri", command=koosta_kiri).grid(
        row=len(fields), column=0, columnspan=2, pady=15
    )

    """võrgu laiendused"""
    win.grid_columnconfigure(1, weight=1)


"""MENUBUTTON + MENU"""
mb = Menubutton(root, text="Vali tegevus", relief="raised", width=20)
mb.grid(row=0, column=0, padx=20, pady=50)

menu = Menu(mb, tearoff=0)
mb.config(menu=menu)
menu.add_command(label="Loo kaaskiri", command=kaaskiri_vorm)
menu.add_command(label="Salvestatud kaaskirjad", command=vaata_salvestatud_kaaskirju)

init_db()

root.mainloop()
