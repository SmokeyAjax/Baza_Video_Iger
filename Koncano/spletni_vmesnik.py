import json
import random
import bottle
from sqlite3 import IntegrityError
from model import LoginError,  Uporabnik, Igre, Podjetje, Platforma


NASTAVITVE = 'nastavitve.json' 
# Želi odpreti nastavitve.json, če ne obstajajao ga naredi
try: 
    with open(NASTAVITVE) as f:
        nastavitve = json.load(f)
        SKRIVNOST = nastavitve['skrivnost']
except FileNotFoundError:
    SKRIVNOST = "".join(chr(random.randrange(32, 128)) for _ in range(32))
    with open(NASTAVITVE, "w") as f:
        json.dump({'skrivnost': SKRIVNOST}, f)


def zahtevaj_prijavo():
    if bottle.request.get_cookie('uporabnik', secret = SKRIVNOST) != 'admin':
        return False
    return True



def zahtevaj_odjavo():
    if bottle.request.get_cookie('uporabnik', secret=SKRIVNOST):
        bottle.redirect('/')


def prijavi_uporabnika(uporabnik):
    bottle.response.set_cookie('uporabnik', uporabnik.ime, path='/', secret=SKRIVNOST)
    bottle.response.set_cookie('uid', str(uporabnik.id), path='/', secret=SKRIVNOST)
    bottle.redirect('/')

@bottle.route('/prijava/')
def prijava():
    zahtevaj_odjavo()
    return bottle.template(
        'html/prijava.html',
        napaka = None, ime = ""
    )

@bottle.post('/prijava/')
def prijava_post():
    zahtevaj_odjavo()
    ime = bottle.request.forms['uporabnisko_ime']
    geslo = bottle.request.forms['geslo']
    try:
        prijavi_uporabnika(Uporabnik.prijava(ime, geslo))
    except LoginError:
        return bottle.template(
            'html/prijava.html',
            napaka = 'Uporabniško ime in geslo se ne ujemata!',
            ime = ime
        )


@bottle.get('/vpis/')
def vpis():
    zahtevaj_odjavo()
    return bottle.template(
        'html/vpis.html',
        napaka = None, ime = ""
    )


@bottle.post('/vpis/')
def vpis_post():
    zahtevaj_odjavo()
    ime = bottle.request.forms['uporabnisko_ime']
    geslo1 = bottle.request.forms['geslo1']
    geslo2 = bottle.request.forms['geslo2']
    if geslo1 != geslo2:
        return bottle.template(
            'html/vpis.html',
            napaka='Gesli se ne ujemata!',
            ime=ime
        )
    try:
        uporabnik = Uporabnik(ime)
        uporabnik.dodaj_v_bazo(geslo1)
        prijavi_uporabnika(uporabnik)
    except IntegrityError:
        return bottle.template(
            'html/vpis.html',
            napaka='Uporabniško ime že obstaja!',
            ime = ime
        )


@bottle.get('/odjava/')
def odjava():
    bottle.response.delete_cookie('uporabnik', path='/')
    bottle.response.delete_cookie('uid', path='/')
    bottle.redirect('/')

# ------------------------------------------------------------------
# Glavna Stran
@bottle.route('/')
def glavna_stran():
    return bottle.template(
        'html/glavna_stran.html',
        admin = zahtevaj_prijavo(),
        najnovejse_igre = Igre.najnovejse_igre(),
        ime = bottle.request.get_cookie('uporabnik', secret=SKRIVNOST)
    )

# Prikaz igre
@bottle.get('/<igra>/')
def igra(igra):
    return bottle.template(
        'html/igra.html',
        admin = zahtevaj_prijavo(),
        igra = igra,
        podatki_o_igri = Igre.podatki_o_igri(igra)
    )

# Dodajanje platforme igri
@bottle.get('/dodaj_platformo/<igra>/')
def dodaj_platformo(igra):
    zahtevaj_prijavo()
    return bottle.template(
        'html/dodaj_igri_platformo.html',
        napaka = None,
        ime_igre = igra, platforma = ""
    )

@bottle.post('/dodaj_platformo/<igra>/')
def dodaj_podporo(igra):
    platforma = bottle.request.forms.getunicode('platforma')
    ime_igre = igra
    podatki = Igre.podatki_o_igri(ime_igre)

    for podatek in podatki:
        tab = podatek.ostalo[1]
    print(tab)

    if len(platforma) == 0:
        return bottle.template(
            'html/dodaj_igri_platformo.html',
            napaka='Ime platforme ne sme biti prazen',
            ime_igre = ime_igre, platforma = platforma
        )

    elif platforma not in Platforma.imena_platform():
        return bottle.template(
            'html/dodaj_igri_platformo.html',
            napaka='Platforma ne obstaja!',
            ime_igre = ime_igre, platforma = platforma
        )

    elif platforma in tab:
        return bottle.template(
            'html/dodaj_igri_platformo.html',
            napaka='Igra že ime to platformo!',
            ime_igre = ime_igre, platforma = platforma
        )
    else:
        igrca = Igre(ime_igre, None, None, None, None, None, None, None, None, platforma)
        igrca.dodajplatformo()
        bottle.redirect('/' + str(ime_igre) + '/')


# Dodajanje distributerja igri
@bottle.get('/dodaj_distributerja/<igra>/')
def dodaj_distributerja(igra):
    zahtevaj_prijavo()

    return bottle.template(
        'html/dodaj_igri_distributerja.html',
        napaka = None,
        ime_igre = igra, distributer = ""
    )

@bottle.post('/dodaj_distributerja/<igra>/')
def dodaj_igri_distributerja(igra):
    distributer = bottle.request.forms.getunicode('distributer')
    ime_igre = igra
    podatki = Igre.podatki_o_igri(ime_igre)
    for podatek in podatki:
        tab = podatek.ostalo[0]

    if len(distributer) == 0:
        return bottle.template(
            'html/dodaj_igri_distributerja.html',
            napaka='Ime založnika ne sme biti prazen',
            ime_igre = ime_igre, distributer = distributer
        )

    elif distributer not in Podjetje.imena_podjetij():
        return bottle.template(
            'html/dodaj_igri_distributerja.html',
            napaka='Založnik ne obstaja!',
            ime_igre = ime_igre, distributer = distributer
        )

    elif distributer in tab:
        return bottle.template(
            'html/dodaj_igri_distributerja.html',
            napaka='Igra že ime tega založnika!',
            ime_igre = ime_igre, distributer = distributer
        )
    else:
        igrca = Igre(ime_igre, None, None, None, None, None, None, None, distributer, None)
        igrca.dodajdistributerja()
        bottle.redirect('/' + str(ime_igre) + '/')

# Prikaz Podjetja
@bottle.get('/podjetje/<podjetje>/')
def podjetje(podjetje):
    return bottle.template(
        'html/podjetje.html',
        podjetje = podjetje,
        podatki_o_podjetju = Podjetje.podatki_o_podjetju(podjetje)
    )

# Prikaz Platforme
@bottle.get('/platforme/<platforma>/')
def platforma(platforma):
    return bottle.template(
        'html/platforma.html',
        platforma = platforma,
        podatki_o_platformi = Platforma.podatki_o_platformi(platforma)
    )

# Iskanje stran
@bottle.get('/isci/')
def iskanje():
    iskalni_niz = bottle.request.query.getunicode('iskalni_niz')
    igre = Igre.poisci(iskalni_niz)
    return bottle.template(
        'html/iskanje.html',
        iskalni_niz = iskalni_niz,
        igre = igre
    )

# Glej vse igre stran, + vse verjante
@bottle.get('/glej_vse_igre/')
def glej_vse_igre():
    return bottle.template(
        'html/glej_vse_igre.html',
        glej_vse_igre=Igre.glej_vse_igre()
    )

@bottle.get('/glej_vse_igre/po_imenih/')
def glej_vse_igre_imena():
    return bottle.template(
        'html/glej_vse_igre_po_imenih.html',
        glej_vse_igre_imena=Igre.glej_vse_igre_imena()
    )

@bottle.get('/glej_vse_igre/po_datumu/')
def glej_vse_igre_datum():
    return bottle.template(
        'html/glej_vse_igre_po_datumu.html',
        glej_vse_igre_datum=Igre.glej_vse_igre_datum()
    )

@bottle.get('/glej_vse_igre/po_ceni/')
def glej_vse_igre_cena():
    return bottle.template(
        'html/glej_vse_igre_po_ceni.html',
        glej_vse_igre_cena=Igre.glej_vse_igre_cena()
    )

@bottle.get('/glej_vse_igre/po_oceni/')
def glej_vse_igre_ocena():
    return bottle.template(
        'html/glej_vse_igre_po_oceni.html',
        glej_vse_igre_ocena=Igre.glej_vse_igre_ocena()
    )

# Dodajanje igre
@bottle.get('/dodaj_igro/')
def dodaj_igro():
    zahtevaj_prijavo()
    return bottle.template(
        'html/dodaj_igro.html',
        napaka = None, ime_igre = "",
        datum_izdaje = "", cena = "",
        vsebuje = "", razvija = "",
        povprecno_igranje = "",mediana = "",
        ocena = "", podjetje= "", platforma= ""
    )

@bottle.post('/dodaj_igro/')
def dodaj_igro_post():
    ime_igre = bottle.request.forms.getunicode('ime_igre')
    datum_izdaje = bottle.request.forms.getunicode('datum_izdaje')
    cena = bottle.request.forms.getunicode('cena')
    vsebuje = bottle.request.forms.getunicode('vsebuje')
    razvija = bottle.request.forms.getunicode('razvija')
    povprecno_igranje = bottle.request.forms.getunicode('povprecno_igranje')
    mediana = bottle.request.forms.getunicode('mediana')
    ocena = bottle.request.forms.getunicode('ocena')
    podjetje = bottle.request.forms.getunicode('podjetje')
    platforma = bottle.request.forms.getunicode('platforma')


    if len(ime_igre) == 0:
        return bottle.template(
            'html/dodaj_igro.html',
            napaka='Ime igre ne sme bit prazen!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, razvija=razvija,
            povprecno_igranje=povprecno_igranje, mediana=mediana,
            ocena=ocena, podjetje=podjetje, platforma=platforma
        )
    
    elif ime_igre in Igre.imena_iger():
        return bottle.template(
            'html/dodaj_igro.html',
            napaka='Ime igre že obstaja!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, razvija=razvija,
            povprecno_igranje=povprecno_igranje, mediana=mediana,
            ocena=ocena, podjetje=podjetje, platforma=platforma
        )
    
    elif len(datum_izdaje) == 0:
        return bottle.template(
            'html/dodaj_igro.html',
            napaka='Datum ne sme biti prazen!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, razvija=razvija,
            povprecno_igranje=povprecno_igranje, mediana=mediana,
            ocena=ocena, podjetje=podjetje, platforma=platforma
        )
    
    elif razvija not in Podjetje.imena_podjetij():
        return bottle.template(
            'html/dodaj_igro.html',
            napaka='Razvijalec ne obstaja!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, razvija=razvija,
            povprecno_igranje=povprecno_igranje, mediana=mediana,
            ocena=ocena, podjetje=podjetje, platforma=platforma
        )
    
    elif podjetje not in Podjetje.imena_podjetij():
        return bottle.template(
            'html/dodaj_igro.html',
            napaka='Založnik ne obstaja!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, razvija=razvija,
            povprecno_igranje=povprecno_igranje, mediana=mediana,
            ocena=ocena, podjetje=podjetje, platforma=platforma
        )
    
    elif platforma not in Platforma.imena_platform():
        return bottle.template(
            'html/dodaj_igro.html',
            napaka='Platforma ne obstaja!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, razvija=razvija,
            povprecno_igranje=povprecno_igranje, mediana=mediana,
            ocena=ocena, podjetje=podjetje, platforma=platforma
        )

    else:
        igra = Igre(ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena, podjetje, platforma)
        igra.dodaj_v_bazo()
        bottle.redirect('/')

# Uredimo igro
@bottle.get('/uredi/<igra>/')
def uredi_igro(igra):
    zahtevaj_prijavo()
    return bottle.template(
        'html/uredi_igro.html',
        napaka = None, igra = igra,
        podatki_o_igri = Igre.podatki_o_igri(igra),
        cena = "", vsebuje = "", razvija = "",
        povprecno_igranje = "",mediana = "",
        ocena = "", podjetje= "", platforma= ""  
    )

@bottle.post('/uredi/<igra>/')
def spremeni_igro(igra):

    ime_igre = igra
    datum_izdaje = bottle.request.forms.getunicode('datum_izdaje')
    cena = bottle.request.forms.getunicode('cena')
    vsebuje = bottle.request.forms.getunicode('vsebuje')
    povprecno_igranje = bottle.request.forms.getunicode('povprecno_igranje')
    mediana = bottle.request.forms.getunicode('mediana')
    ocena = bottle.request.forms.getunicode('ocena')

    if len(datum_izdaje) == 0:
        return bottle.template(
            'html/uredi_igro.html',
            napaka='Datum ne sme biti prazen!',
            ime_igre = ime_igre,
            datum_izdaje=datum_izdaje, cena=cena,
            vsebuje=vsebuje, povprecno_igranje=povprecno_igranje,
            mediana=mediana, ocena=ocena,
            podatki_o_igri = Igre.podatki_o_igri(igra)
        )

    else:
        spremeni = Igre(ime_igre, datum_izdaje, cena, vsebuje, None, povprecno_igranje, mediana, ocena)
        spremeni.spremeni_podatke()
        bottle.redirect('/' + str(ime_igre) + '/')

# Dodajanje Podjetja
@bottle.get('/dodaj_podjetje/')
def dodaj_podjetje():
    zahtevaj_prijavo()
    return bottle.template(
        'html/dodaj_podjetje.html',
        napaka = None,
        ime = "", drzava = "", datum_ustanovitve = "", opis=""
    )

@bottle.post('/dodaj_podjetje/')
def dodaj_podjetje_post():
    zahtevaj_prijavo()
    ime = bottle.request.forms.getunicode('ime')
    drzava = bottle.request.forms.getunicode('drzava')
    datum_ustanovitve = bottle.request.forms.getunicode('datum_ustanovitve')
    opis = bottle.request.forms.getunicode('opis')

    if len(ime) == 0:
        return bottle.template(
            'html/dodaj_podjetje.html',
            napaka='Ime podjetja ne sme biti prazen!',
            ime = ime, drzava = drzava,
            datum_ustanovitve = datum_ustanovitve,
            opis = opis
        )

    elif ime in Podjetje.imena_podjetij():
        return bottle.template(
            'html/dodaj_podjetje.html',
            napaka='To podjetje že obstaja!',
            ime = ime, drzava = drzava,
            datum_ustanovitve = datum_ustanovitve,
            opis = opis
        )

    elif len(datum_ustanovitve) == 0:
        return bottle.template(
            'html/dodaj_podjetje.html',
            napaka='Datum ne sme biti prazen!',
            ime = ime, drzava = drzava,
            datum_ustanovitve = datum_ustanovitve,
            opis = opis
        )
    else:
        podjetje = Podjetje(ime, drzava, datum_ustanovitve, opis)
        podjetje.dodaj_v_bazo()
        bottle.redirect('/')


bottle.run(reloader=True, debug = True)
