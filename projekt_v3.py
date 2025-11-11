import tkinter as tk
from tkinter import Menubutton, Menu, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- PÕHIAKEN ---
root = tk.Tk()
root.title("Kandideerimismasin")
root.geometry("400x200")


# --- FUNKTSIOON: Loo kaaskirja aken ---
def kaaskiri_vorm():
    """Avab eraldi akna (Toplevel), kus saab kaaskirja väljad täita."""
    win = tk.Toplevel(root)
    win.title("Kaaskiri")
    win.geometry("700x600")

    # väljade nimed ja võtmed
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

    # --- FUNKTSIOON: Kaaskirja koostamine ---
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

        # --- Kuvame kirja uues aknas ---
        win_kiri = tk.Toplevel(win)
        win_kiri.title("Valmis kaaskiri")
        win_kiri.geometry("700x600")

        text = tk.Text(win_kiri, wrap="word", width=80, height=25)
        text.insert("1.0", kiri)
        text.pack(padx=10, pady=10, fill="both", expand=True)

        # --- TXT ja PDF salvestus ---
        def salvesta_txt():
            with open("kaaskiri.txt", "w", encoding="utf-8") as f:
                f.write(kiri)
            messagebox.showinfo("Salvestatud", "Kaaskiri salvestati faili 'kaaskiri.txt'.")

        def salvesta_pdf():
            pdf_fail = "kaaskiri.pdf"
            c = canvas.Canvas(pdf_fail, pagesize=A4)
            textobject = c.beginText(50, 800)
            for line in kiri.splitlines():
                textobject.textLine(line)
            c.drawText(textobject)
            c.save()
            messagebox.showinfo("Salvestatud", f"Kaaskiri salvestatud faili '{pdf_fail}'.")

        ttk.Button(win_kiri, text="💾 Salvesta TXT", command=salvesta_txt).pack(pady=5)
        ttk.Button(win_kiri, text="📄 Salvesta PDF", command=salvesta_pdf).pack(pady=5)

    # --- Nupp kirja koostamiseks ---
    ttk.Button(win, text="Koosta kiri", command=koosta_kiri).grid(
        row=len(fields), column=0, columnspan=2, pady=15
    )

    # võrgu laiendused
    win.grid_columnconfigure(1, weight=1)


# --- MENUBUTTON + MENU ---
mb = Menubutton(root, text="Vali tegevus", relief="raised", width=20)
mb.grid(row=0, column=0, padx=20, pady=50)

menu = Menu(mb, tearoff=0)
mb.config(menu=menu)
menu.add_command(label="Loo kaaskiri", command=kaaskiri_vorm)

root.mainloop()