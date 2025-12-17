import tkinter as tk
from tkinter import Menubutton, Menu, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sqlite3
from datetime import datetime

DB_PATH = "kandideerimismasin.db"

# KEELED
LANGS = {
    "et": {
        "title_main": "Kandideerimismasin",
        "menu_action": "Vali tegevus",
        "menu_create": "Loo kaaskiri",
        "menu_saved": "Salvestatud kaaskirjad",
        "btn_refresh": "🔄 Värskenda",
        "btn_open": "📂 Ava",
        "btn_create": "Koosta kiri",
        "error": "Viga",
        "fill_all": "Palun täida kõik väljad.",
        "saved": "Salvestatud",
        "saved_db": "Kaaskiri salvestatud: {nimi} → {ettevote}",
        "saved_window_title": "Salvestatud kaaskirjad",
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
        "btn_refresh": "🔄 Refresh",
        "btn_open": "📂 Open",
        "btn_create": "Generate letter",
        "error": "Error",
        "fill_all": "Please fill in all fields.",
        "saved": "Saved",
        "saved_db": "Cover letter saved: {nimi} → {ettevote}",
        "saved_window_title": "Saved cover letters",
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
    global current_lang
    current_lang = lang
    refresh_ui()

def t(key):
    return LANGS[current_lang][key]

def tl(key):
    return LANGS[current_lang]["labels"][key]

# ANDMEBAAS
def init_db():
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
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO letters(nimi, ettevõte, kirja_text, loodud_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(nimi, ettevõte)
            DO UPDATE SET kirja_text=excluded.kirja_text, loodud_at=excluded.loodud_at
        """, (nimi, ettevõte, kirja_text, datetime.now().isoformat()))

def list_nimi():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT DISTINCT nimi FROM letters")
        return [r[0] for r in cur.fetchall()]

def list_ettevõte(nimi):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT ettevõte FROM letters WHERE nimi=?", (nimi,))
        return [r[0] for r in cur.fetchall()]

def list_kiri(nimi, ettevõte):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT kirja_text FROM letters WHERE nimi=? AND ettevõte=?", (nimi, ettevõte))
        row = cur.fetchone()
        return row[0] if row else ""

# PÕHIAKEN
root = tk.Tk()
root.geometry("400x200")

def refresh_ui():
    root.title(t("title_main"))
    mb.config(text=t("menu_action"))
    menu.entryconfig(0, label=t("menu_create"))
    menu.entryconfig(1, label=t("menu_saved"))

# SALVESTATUD KIRJAD
def vaata_salvestatud_kaaskirju():
    win = tk.Toplevel(root)
    win.title(t("menu_saved"))
    win.geometry("800x600")

    ttk.Label(win, text=f"{t('label_name')}:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
    nimi_cb = ttk.Combobox(win, values=list_nimi(), state="readonly")
    nimi_cb.grid(row=0, column=1)

    ttk.Label(win, text=f"{t('label_company')}:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
    ettevote_cb = ttk.Combobox(win, state="readonly")
    ettevote_cb.grid(row=1, column=1)

    text = tk.Text(win, wrap="word")
    text.grid(row=2, column=0, columnspan=3, sticky="nsew")

    def värskenda(event=None):
        ettevote_cb["values"] = list_ettevõte(nimi_cb.get())

    def ava(event=None):
        text.delete("1.0", tk.END)
        text.insert("1.0", list_kiri(nimi_cb.get(), ettevote_cb.get()))

    nimi_cb.bind("<<ComboboxSelected>>", värskenda)
    ettevote_cb.bind("<<ComboboxSelected>>", ava)


# KAASKIRI
def kaaskiri_vorm():
    win = tk.Toplevel(root)
    win.geometry("700x600")
    win.title(t("menu_create"))

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
        ttk.Label(win, text=tl(key)).grid(row=i, column=0, sticky="w")
        if ftype == "entry":
            e = ttk.Entry(win)
            e.grid(row=i, column=1, sticky="ew")
            entries[key] = e
        else:
            tbox = tk.Text(win, height=4)
            tbox.grid(row=i, column=1, sticky="ew")
            entries[key] = tbox

    def koosta():
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
        txt = tk.Text(top)
        txt.insert("1.0", kiri)
        txt.pack(fill="both", expand=True)

        def save():
            salvesta_kiri(values["nimi"], values["ettevote"], kiri)
            messagebox.showinfo(t("saved"), t("saved_db").format(**values))

        ttk.Button(top, text="💾 Save", command=save).pack()

    ttk.Button(win, text=t("btn_create"), command=koosta).grid(row=len(fields), column=0, columnspan=2)

# MENÜÜ
mb = Menubutton(root, relief="raised", width=20)
mb.grid(pady=50)

menu = Menu(mb, tearoff=0)
mb.config(menu=menu)

menu.add_command(command=kaaskiri_vorm)
menu.add_command(command=vaata_salvestatud_kaaskirju)

lang_menu = Menu(menu, tearoff=0)
lang_menu.add_command(label="Eesti", command=lambda: set_lang("et"))
lang_menu.add_command(label="English", command=lambda: set_lang("en"))
menu.add_cascade(label="🌍 Language", menu=lang_menu)

init_db()
refresh_ui()
root.mainloop()
