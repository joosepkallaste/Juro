import tkinter as tk
from tkinter import Menubutton, Menu, messagebox

# --- PÕHIAKEN ---
root = tk.Tk()                     
root.title("Kandideerimismasin")



# --- TEGEVUSED MENÜÜST ---

def kaaskiri_vorm():
    """Avab eraldi akna (Toplevel), kus saab kaaskirja väljad täita."""
    win = tk.Toplevel(root)
    win.title("Kaaskiri")

    # väljade definitsioonid: (key: value)
    fields = [
        ("Täisnimi", "nimi"),
        ("Ettevõte", "ettevote"),
        ("Esindaja ametikoht", "esindajaAmetikoht"),
        ("Esindaja nimi", "esindajaNimi"),
        ("Ametikoht (kuhu kandideerid)", "ametikoht"),
        ("Nõuded kandidaadile", "noudedKandidaadile"),
        ("Miks sobid", "miksMina"),
        ("E-mail", "gmail"),
        ("Telefon (+372…)", "tel"),
    ]

    entries = {}

    for r, (label, key) in enumerate(fields):
        tk.Label(win, text=label + ":").grid(row=r, column=0, sticky="w", padx=8, pady=4)
        e = tk.Entry(win, width=40)
        e.grid(row=r, column=1, padx=8, pady=4)
        entries[key] = e

    def koosta_kiri():
        # 1) loe igast väljast väärtus eraldi muutujasse (selge ja loetav)
        nimi               = entries["nimi"].get().strip()
        ettevote           = entries["ettevote"].get().strip()
        esindajaAmetikoht  = entries["esindajaAmetikoht"].get().strip()
        esindajaNimi       = entries["esindajaNimi"].get().strip()
        ametikoht          = entries["ametikoht"].get().strip()
        noudedKandidaadile = entries["noudedKandidaadile"].get().strip()
        miksMina           = entries["miksMina"].get().strip()
        gmail              = entries["gmail"].get().strip()
        tel                = entries["tel"].get().strip()

        # 2) väga lihtne kontroll 
        if not (nimi and ettevote and esindajaAmetikoht and esindajaNimi and
                ametikoht and noudedKandidaadile and miksMina and gmail and tel):
            messagebox.showerror("Viga", "Palun täida kõik väljad.")
            return

        # 3) üks selge kolmekordsete jutumärkidega f-string (pole + ega join vaja)
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

Lugupidamisega
{nimi}"""

        messagebox.showinfo("Koostatud kaaskiri", kiri)


    tk.Button(win, text="Koosta kiri", command=koosta_kiri)\
        .grid(row=len(fields), column=0, columnspan=2, pady=10)

# --- MENUBUTTON + MENU ---
mb = Menubutton(root, text="Vali tegevus", relief="raised", width=20)
mb.grid(row=0, column=2, padx=8, pady=8)

menu = Menu(mb, tearoff=0)
mb.config(menu=menu)

menu.add_command(label="Loo kaaskiri", command=kaaskiri_vorm)



root.mainloop()

