
def main():
    nimi = input("Palun sisestage oma täisnimi: ")
    ettevote = input("Sisestage ettevõtte nimi: ")
    esindajaAmetikoht = input("Sisestage esindaja ametikoht: ")
    esindajaNimi = input("Sisestage ettevõte esindaja nimi: ")
    ametikoht = input("Palun sisestage ametikoht kuhu kandideerite: ")
    noudedKandidaadile = input("Palun sisestage nõuded kandidaadile: ")
    miksMina = input("Palun sisestage miks sobite sellele töökohale: ")
    gmail = input("Palun sisestage oma gmail: ")
    tel = input("Palun sisestage oma telefoninumber (lisage ka +372): ")

    kiri = (
        f"Lugupeetud {ettevote} {esindajaAmetikoht} {esindajaNimi}\n\n"
        f"Soovin kandideerida Teie väljakuulutatud {ametikoht} ametikohale.\n\n"
        "Kuigi kirjale lisatud CV annab ülevaate minu varasemast töökogemusest, "
        "haridusest, täiendõppest ja tööks vajalikest oskustest, tõin välja "
        "töökuulutuses olevad nõudmised ja vastavad oskused nendel aladel:\n\n"
        f"• {noudedKandidaadile}\n\n"
        "Leian, et lisaks töökuulutuses toodud nõuete täitmisele, olen sellele "
        f"ametikohale sobiv kandidaat, sest {miksMina}\n\n"
        "Olen meeleldi nõus vastama tekkivatele küsimustele Teile sobival ajal "
        "e-maili {gmail} või telefoni {tel} teel! "
        "Ootan Teiega kohtumist, et rääkida põhjalikumalt pakutavast ametikohast "
        "ja põhjustest, miks leian, et olen Teie ettevõttesse sobiv inimene.\n\n"
        "Lugupidamisega\n"
        "{nimi}"
    )

    print(kiri)


if __name__ == "__main__":
    main()
