import baza
import sqlite3
from pomozne_funkcije import Seznam
from geslo import sifriraj_geslo, preveri_geslo

conn = sqlite3.connect('igre.db')
baza.ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

uporabnik, podjetje, igra, platforma, distributira, podpira = baza.pripravi_tabele(conn)


class LoginError(Exception):
    """
    Napaka ob napačnem uporabniškem imenu ali geslu.
    """
    pass


class Uporabnik:
    """
    Razred za uporabnika.
    """

    def __init__(self, ime, *, id=None):
        """
        Konstruktor uporabnika.
        """
        self.id = id
        self.ime = ime

    def __str__(self):
        """
        Znakovna predstavitev uporabnika.
        Vrne uporabniško ime.
        """
        return self.ime


    @staticmethod
    def prijava(ime, geslo):
        """
        Preveri, ali sta uporabniško ime geslo pravilna.
        """
        sql = """
            SELECT id, zgostitev, sol FROM uporabnik
            WHERE ime = ?
        """
        try:
            id, zgostitev, sol = conn.execute(sql, [ime]).fetchone()
            if preveri_geslo(geslo, zgostitev, sol):
                return Uporabnik(ime, id=id)
        except TypeError:
            pass
        raise LoginError(ime)

    def dodaj_v_bazo(self, geslo):
        """
        V bazo doda uporabnika s podanim geslom.
        """
        assert self.id is None
        zgostitev, sol = sifriraj_geslo(geslo)
        with conn:
            self.id = uporabnik.dodaj_vrstico(ime=self.ime, zgostitev=zgostitev, sol=sol)


class Igre:
    """
    Razred za igre.
    """

    def __init__(self, ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje
        , mediana, ocena, *ostalo, id=None):
        """
        Konstruktor igre.
        """
        self.id = id
        self.ime_igre = ime_igre
        self.datum_izdaje = datum_izdaje
        self.cena = cena
        self.vsebuje = vsebuje
        self.razvija = razvija
        self.povprecno_igranje = povprecno_igranje
        self.mediana = mediana
        self.ocena = ocena
        self.ostalo = ostalo

    @staticmethod
    def najnovejse_igre():
        """
        Vrne najboljših 10 filmov v danem letu.
        """
        sql = """
            SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
            FROM igra
            ORDER BY datum_izdaje DESC
            LIMIT 10
        """
        for ime_igre, datum_izdaje, *ostalo in conn.execute(sql):
            yield Igre(ime_igre, datum_izdaje, *ostalo)

    @staticmethod
    def podatki_o_igri(igra):
        """
        Vrne vse podatke o igri.
        """
        sql = """
            SELECT igra.ime_igre, igra.datum_izdaje, cena, vsebuje, razvijalec.ime, povprecno_igranje, mediana, ocena,
             podjetje.ime, platforma.ime
            FROM igra LEFT JOIN podpira ON (igra.id = podpira.ime_igre)
                      LEFT JOIN platforma ON (podpira.platforma = platforma.id)
                      LEFT JOIN distributira ON (igra.id = distributira.ime_igre)
                      LEFT JOIN podjetje ON (distributira.podjetje = podjetje.id)
                      LEFT JOIN podjetje AS razvijalec ON (igra.razvija = razvijalec.id)
            WHERE igra.ime_igre == ?
        """
        for ime_igre, datum_izdaje, cena, st_prodanih, razvijalec, cas_igranja, meadina_igranja, ocena, distibuter, platforma in conn.execute(sql, [igra]):
            yield Igre(ime_igre, datum_izdaje, cena, st_prodanih, razvijalec, cas_igranja, meadina_igranja, ocena, distibuter, platforma)

    @staticmethod
    def poisci(niz):
        """
        Vrne vse igre, ki v imenu vsebujejo dani niz.
        """
        sql = """
            SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
            FROM igra
            WHERE ime_igre LIKE ?
        """
        for ime_igre, *ostalo in conn.execute(sql, ['%' + niz + '%']):
            yield Igre(ime_igre, *ostalo)

    @staticmethod
    def glej_vse_igre():
        """
        Vrne vse podatke o igri.
        """
        sql = """
                SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
                FROM igra DESC
            """
        for ime_igre, datum_izdaje, cena, ocena, *ostalo  in conn.execute(sql):
            yield Igre(ime_igre, datum_izdaje, cena, ocena, *ostalo)

    @staticmethod
    def glej_vse_igre_imena():
        """
        Vrne vse podatke o igri razvrščeno po imenu.
        """
        sql = """
                SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
                FROM igra
                ORDER BY ime_igre
            """
        for ime_igre, datum_izdaje, cena, ocena, *ostalo  in conn.execute(sql):
            yield Igre(ime_igre, datum_izdaje, cena, ocena, *ostalo)

    @staticmethod
    def glej_vse_igre_datum():
        """
        Vrne vse podatke o igri po datumu.
        """
        sql = """
                SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
                FROM igra
                ORDER BY datum_izdaje DESC
            """
        for ime_igre, datum_izdaje, cena, ocena, *ostalo  in conn.execute(sql):
            yield Igre(ime_igre, datum_izdaje, cena, ocena, *ostalo)
    
    
    @staticmethod
    def glej_vse_igre_cena():
        """
        Vrne vse podatke o igri po ceni.
        """
        sql = """
                SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
                FROM igra
                ORDER BY cena DESC NULLS LAST
            """
        for ime_igre, datum_izdaje, cena, ocena, *ostalo  in conn.execute(sql):
            yield Igre(ime_igre, datum_izdaje, cena, ocena, *ostalo)

    @staticmethod
    def glej_vse_igre_ocena():
        """
        Vrne vse podatke o igri po oceni.
        """
        sql = """
                SELECT ime_igre, datum_izdaje, cena, vsebuje, razvija, povprecno_igranje, mediana, ocena
                FROM igra
                ORDER BY ocena DESC NULLS LAST
            """
        for ime_igre, datum_izdaje, cena, ocena, *ostalo  in conn.execute(sql):
            yield Igre(ime_igre, datum_izdaje, cena, ocena, *ostalo)


    def dodaj_v_bazo(self):
        """
        V bazo doda igro.
        """
        assert self.id is None
        with conn:
            self.id = igra.dodaj_vrstico(ime_igre=self.ime_igre, datum_izdaje=self.datum_izdaje, cena=self.cena,vsebuje=self.vsebuje,
            razvija=self.razvija,povprecno_igranje=self.povprecno_igranje, mediana=self.mediana, ocena=self.ocena
                                         )


class Podjetje:
    """
    Razred za podjetja.
    """

    def __init__(self, ime, drzava, datum_ustanovitve, opis, id=None):
        """
        Konstruktor podjetja.
        """
        self.id = id
        self.ime = ime
        self.drzava = drzava
        self.datum_ustanovitve = datum_ustanovitve
        self.opis = opis

    def __str__(self):
        return self.ime

    @staticmethod
    def podatki_o_podjetju(podjetje):
        """
        Vrne vse podatke o podjetju.
        """
        sql = """
            SELECT ime, drzava, datum_ustanovitve, opis
            FROM podjetje
            WHERE ime == ?
        """
        for ime, drzava, datum_ustanovitve, opis in conn.execute(sql, [podjetje]):
            yield Podjetje(ime, drzava, datum_ustanovitve, opis)

    def dodaj_v_bazo(self):
        """
        V bazo doda podjetje.
        """
        assert self.id is None
        with conn:
            self.id = podjetje.dodaj_vrstico(
                ime=self.ime, drzava=self.drzava, datum_ustanovitve=self.datum_ustanovitve, opis=self.opis)

class Platforma:
    """
    Razred za platformo.
    """

    def __init__(self, ime, tip, datum_izdaje, opis, podjetje):
        """
        Konstruktor platformo.
        """
        self.ime = ime
        self.tip = tip
        self.datum_izdaje = datum_izdaje
        self.opis = opis
        self.podjetje = podjetje

    @staticmethod
    def podatki_o_platformi(platforma):
        """
        Vrne vse podatke o platformi.
        """
        sql = """
            SELECT ime, tip, datum_izdaje, opis, podjetje
            FROM platforma
            WHERE ime == ?
        """
        for ime, tip, datum_izdaje, opis, podjetje in conn.execute(sql, [platforma]):
            yield Platforma(ime, tip, datum_izdaje, opis, podjetje)


# class Oseba:
#     """
#     Razred za osebo.
#     """

#     def __init__(self, ime, *, id=None):
#         """
#         Konstruktor osebe.
#         """
#         self.id = id
#         self.ime = ime

#     def __str__(self):
#         """
#         Znakovna predstavitev osebe.
#         Vrne ime osebe.
#         """
#         return self.ime

#     def poisci_vloge(self):
#         """
#         Vrne vloge osebe.
#         """
#         sql = """
#             SELECT film.naslov, film.leto, vloga.tip
#             FROM film
#                 JOIN vloga ON film.id = vloga.film
#             WHERE vloga.oseba = ?
#             ORDER BY leto
#         """
#         for naslov, leto, tip_vloge in conn.execute(sql, [self.id]):
#             yield (naslov, leto, TipVloge[tip_vloge])

#     @staticmethod
#     def poisci(niz):
#         """
#         Vrne vse osebe, ki v imenu vsebujejo dani niz.
#         """
#         sql = "SELECT id, ime FROM oseba WHERE ime LIKE ?"
#         for id, ime in conn.execute(sql, ['%' + niz + '%']):
#             yield Oseba(ime=ime, id=id)

#     def dodaj_v_bazo(self):
#         """
#         Doda osebo v bazo.
#         """
#         assert self.id is None
#         with conn:
#             self.id = oseba.dodaj_vrstico(ime=self.ime)


# class TipVloge(Seznam):
#     """
#     Oznake za tip vloge.
#     """
#     I = 'igralec'
#     R = 'režiser'