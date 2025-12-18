"""
Projekt: Kandideerimismasin
Autorid: Henry Hiire, Joosep-Gre Kallaste
Kirjeldus:
    Programm kaaskirjade koostamiseks, haldamiseks ja salvestamiseks.
    Toetab eesti- ja inglise keelt ning kasutab SQLite andmebaasi.
    Võimalik salvestada kaaskirja PDF-failina.

Kasutatud allikad:
    - Python dokumentatsioon (tkinter, sqlite3)
    - ReportLab dokumentatsioon
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

# =========================
# KEELED
# =========================
LANGUAGES = {
    "et": {
        "title_main": "Kandideerimismasin",
        "menu_action": "Vali tegevus",
        "menu_create": "Loo kaaskiri",
        "menu_saved": "Salvestatud kaaskirjad",
        "btn_refresh": "Värskenda",
        "btn_open": "Ava",
        "btn_create": "Koosta kiri",
        "btn_save": "Salvesta",
        "error": "Viga",
        "fill_all": "Palun täida kõik väljad.",
        "saved": "Salvestatud",
        "saved_db": "Kaaskiri salvestatud: {nimi} → {ettevote}",
        "label_name": "Nimi",
        "label_company": "Ettevõte",
        "labels": {
            "nimi": "Täisnimi",
            "ettevote": "Ettevõte",
            "esindajaAmetikoht": "Esindaja ametikoht",
            "esindajaNimi": "Esindaja nimi",
            "ametikoht": "Ametikoht (kuhu kandideerid)",
            "noudedKandidaadile": "Nõuded kandidaadile",
            "miksMina": "Miks sobid",
            "gmail": "E-mail",
            "tel": "Telefon",
        }
    },
    "en": {
        "title_main": "Cover Letter Generator",
        "menu_action": "Choose action",
        "menu_create": "Create cover letter",
        "menu_saved": "Saved letters",
        "btn_refresh": "Refresh",
        "btn_open": "Open",
        "btn_create": "Generate letter",
        "btn_save": "Save",
        "error": "Error",
        "fill_all": "Please fill in all fields.",
        "saved": "Saved",
        "saved_db": "Cover letter saved: {nimi} → {ettevote}",
        "label_name": "Name",
        "label_company": "Company",
        "labels": {
            "nimi": "Full name",
            "ettevote": "Company",
            "esindajaAmetikoht": "Representative position",
            "esindajaNimi": "Representative name",
            "ametikoht": "Position applied for",
            "noudedKandidaadile": "Job requirements",
            "miksMina": "Why you are suitable",
            "gmail": "E-mail",
            "tel": "Phone",
        }
    }
}

current_lang = "et"

def set_lang(lang):
    """Määrab aktiivse keele ja uuendab kasutajaliidest."""
    global current_lang
    current_lang = lang
    refresh_ui()

def t(key):
    """Tagastab aktiivse keele põhjal vastava kasutajaliidese teksti."""
    return LANGUAGES[current_lang][key]

def tl(key):
    """Tagastab vormiväljade sildid aktiivses keeles."""
    return LANGUAGES[current_lang]["labels"][key]

# =========================
# ANDMEBAAS
# =========================
def init_db():
    """Loob SQLite andmebaasi ja tabeli kaaskirjade salvestamiseks, kui neid veel ei eksisteeri."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nimi TEXT,
            ettevõte TEXT,
            kirja_text TEXT,
            loodud_at TEXT,
            UNIQUE(nimi, ettevõte)
        )
        """)

def salvesta_kiri(nimi, ettevõte, kirja_text):
    """Salvestab kaaskirja andmebaasi või uuendab olemasolevat kirja, kui sama nime ja ettevõtte kombinatsioon on juba olemas."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO letters(nimi, ettevõte, kirja_text, loodud_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(nimi, ettevõte)
            DO UPDATE SET kirja_text=excluded.kirja_text, loodud_at=excluded.loodud_at
        """, (nimi, ettevõte, kirja_text, datetime.now().isoformat()))

def list_nimi():
    """Tagastab nimekirja kõigist andmebaasis olevatest unikaalsetest nimedest."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT DISTINCT nimi FROM letters")
        return [r[0] for r in cur.fetchall()]

def list_ettevõte(nimi):
    """Tagastab ettevõtete nimekirja, millele antud nimi on kaaskirja loonud."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT ettevõte FROM letters WHERE nimi=?", (nimi,))
        return [r[0] for r in cur.fetchall()]

def list_kiri(nimi, ettevõte):
    """Tagastab konkreetse kaaskirja teksti nime ja ettevõtte alusel."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT kirja_text FROM letters WHERE nimi=? AND ettevõte=?", (nimi, ettevõte))
        row = cur.fetchone()
        return row[0] if row else ""

# =========================
# PÕHIAKEN + STIIL
# =========================
root = tk.Tk()
root.geometry("420x260")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6)
style.configure("TLabel", padding=4)
style.configure("TEntry", padding=4)

container = ttk.Frame(root, padding=20)
container.pack(expand=True)

title_lbl = ttk.Label(container, font=("Segoe UI", 16, "bold"))
title_lbl.pack(pady=(0, 15))

mb = Menubutton(container, relief="raised", width=25)
mb.pack(pady=10)

menu = Menu(mb, tearoff=0)
mb.config(menu=menu)

def refresh_ui():
    """Uuendab põhivaate tekste vastavalt valitud keelele."""
    root.title(t("title_main"))
    title_lbl.config(text=t("title_main"))
    mb.config(text=t("menu_action"))
    menu.entryconfig(0, label=t("menu_create"))
    menu.entryconfig(1, label=t("menu_saved"))

# =========================
# SALVESTATUD KIRJAD
# =========================
def vaata_salvestatud_kaaskirju():
    """Avab akna salvestatud kaaskirjade vaatamiseks ja sirvimiseks."""
    win = tk.Toplevel(root)
    win.title(t("menu_saved"))
    win.geometry("800x600")

    win.columnconfigure(1, weight=1)

    ttk.Label(win, text=f"{t('label_name')}:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
    nimi_cb = ttk.Combobox(win, values=list_nimi(), state="readonly")
    nimi_cb.grid(row=0, column=1, sticky="ew")

    ttk.Label(win, text=f"{t('label_company')}:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
    ettevote_cb = ttk.Combobox(win, state="readonly")
    ettevote_cb.grid(row=1, column=1, sticky="ew")

    text = tk.Text(win, wrap="word")
    text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)

    def värskenda(event=None):
        ettevote_cb["values"] = list_ettevõte(nimi_cb.get())

    def ava(event=None):
        text.delete("1.0", tk.END)
        text.insert("1.0", list_kiri(nimi_cb.get(), ettevote_cb.get()))

    nimi_cb.bind("<<ComboboxSelected>>", värskenda)
    ettevote_cb.bind("<<ComboboxSelected>>", ava)

    ttk.Button(win, text=t("btn_refresh"),
               command=lambda: nimi_cb.configure(values=list_nimi())).grid(row=0, column=2, padx=8)
    ttk.Button(win, text=t("btn_open"),
               command=ava).grid(row=1, column=2, padx=8)

# =========================
# KAASKIRI
# =========================
def kaaskiri_vorm():
    """Avab kaaskirja koostamise vormi ning võimaldab kirja genereerida,
    salvestada andmebaasi ja PDF-failina."""
    win = tk.Toplevel(root)
    win.geometry("720x620")
    win.title(t("menu_create"))
    win.columnconfigure(1, weight=1)

    fields = [
        ("nimi", "entry"),
        ("ettevote", "entry"),
        ("esindajaAmetikoht", "entry"),
        ("esindajaNimi", "entry"),
        ("ametikoht", "entry"),
        ("noudedKandidaadile", "text"),
        ("miksMina", "text"),
        ("gmail", "entry"),
        ("tel", "entry"),
    ]

    entries = {}

    for i, (key, ftype) in enumerate(fields):
        ttk.Label(win, text=tl(key)).grid(row=i, column=0, sticky="w", padx=10, pady=4)
        if ftype == "entry":
            e = ttk.Entry(win)
            e.grid(row=i, column=1, sticky="ew", padx=10, pady=4)
            entries[key] = e
        else:
            tbox = tk.Text(win, height=4)
            tbox.grid(row=i, column=1, sticky="ew", padx=10, pady=4)
            entries[key] = tbox

    btn_frame = ttk.Frame(win)
    btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def koosta():
        """Koostab kaaskirja vastavalt kasutaja sisestatud andmetele
        ning avab eelvaate akna."""
        values = {}
        for k, w in entries.items():
            values[k] = w.get("1.0", tk.END).strip() if isinstance(w, tk.Text) else w.get().strip()

        if not all(values.values()):
            messagebox.showerror(t("error"), t("fill_all"))
            return

        if current_lang == "et":
            kiri = f"""Lugupeetud {values['ettevote']} {values['esindajaAmetikoht']} {values['esindajaNimi']}

Soovin kandideerida Teie väljakuulutatud {values['ametikoht']} ametikohale.

Kuigi kirjale lisatud CV annab ülevaate minu varasemast töökogemusest,
haridusest, täiendõppest ja tööks vajalikest oskustest, tõin välja
töökuulutuses olevad nõudmised ja vastavad oskused nendel aladel:

• {values['noudedKandidaadile']}

Leian, et lisaks töökuulutuses toodud nõuete täitmisele olen sellele
ametikohale sobiv kandidaat, sest {values['miksMina']}.

Olen meeleldi nõus vastama tekkivatele küsimustele Teile sobival ajal e-maili
{values['gmail']} või telefoni {values['tel']} teel! Ootan Teiega kohtumist, et
rääkida põhjalikumalt pakutavast ametikohast ja põhjustest, miks leian, et
olen Teie ettevõttesse sobiv inimene.

Lugupidamisega,
{values['nimi']}"""
        else:
            kiri = f"""Dear {values['esindajaAmetikoht']} {values['esindajaNimi']},

I am writing to apply for the position of {values['ametikoht']} at {values['ettevote']}.

Although my CV provides an overview of my previous work experience, education,
and skills, I would like to highlight how my qualifications align with the
requirements listed in your job advertisement:

• {values['noudedKandidaadile']}

I believe I am a strong candidate for this position because {values['miksMina']}.

I would be happy to provide additional information or answer any questions at
your convenience via email at {values['gmail']} or by phone at {values['tel']}.
I look forward to the opportunity to discuss how my skills and experience
could benefit your company.

Kind regards,
{values['nimi']}"""

        top = tk.Toplevel(win)
        top.title(t("menu_create"))
        top.geometry("700x600")

        txt = tk.Text(top, wrap="word")
        txt.insert("1.0", kiri)
        txt.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(top, text=t("btn_save"),
                   command=lambda: salvesta_kiri(values["nimi"], values["ettevote"], kiri)).pack(pady=10)
        ttk.Button(
            top,
            text="Salvesta PDF",
            command=lambda: salvesta_pdf(values["nimi"], values["ettevote"], kiri)
        ).pack(pady=5)


    ttk.Button(btn_frame, text=t("btn_create"), width=20, command=koosta).pack()
    
    
# =========================
# PDF-salvestus
#==========================
def salvesta_pdf(nimi, ettevote, kiri):
    """Salvestab genereeritud kaaskirja PDF-failina kasutades ReportLab teeki."""
    failinimi = f"{nimi}_{ettevote}_kaaskiri.pdf".replace(" ", "_")

    c = canvas.Canvas(failinimi, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 11)

    x = 50
    y = height - 50
    reavahe = 14

    for rida in kiri.split("\n"):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50
        c.drawString(x, y, rida)
        y -= reavahe

    c.save()

    messagebox.showinfo(
        "PDF salvestatud",
        f"PDF-fail loodud:\n{failinimi}"
    )

# =========================
# MENÜÜ
# =========================
menu.add_command(command=kaaskiri_vorm)
menu.add_command(command=vaata_salvestatud_kaaskirju)

lang_menu = Menu(menu, tearoff=0)
lang_menu.add_command(label="Eesti", command=lambda: set_lang("et"))
lang_menu.add_command(label="English", command=lambda: set_lang("en"))
menu.add_cascade(label="Language", menu=lang_menu)

init_db()
refresh_ui()
root.mainloop()
