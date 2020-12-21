import csv
from geslo import sifriraj_geslo

PARAM_FMT = ":{}" # za SQLite

class Tabela:
    """
    Razred, ki predstavlja tabelo v bazi.
    Polja razreda:
    - ime: ime tabele
    - podatki: ime datoteke s podatki ali None
    """
    ime = None
    podatki = None

    def __init__(self, conn):
        """
        Konstruktor razreda.
        """
        self.conn = conn

    def ustvari(self):
        """
        Metoda za ustvarjanje tabele.
        Podrazredi morajo povoziti to metodo.
        """
        raise NotImplementedError

    def izbrisi(self):
        """
        Metoda za brisanje tabele.
        """
        self.conn.execute("DROP TABLE IF EXISTS {};".format(self.ime))

    def uvozi(self, encoding="UTF-8"):
        """
        Metoda za uvoz podatkov.
        Argumenti:
        - encoding: kodiranje znakov
        """
        if self.podatki is None:
            return
        with open(self.podatki, encoding=encoding) as datoteka:
            podatki = csv.reader(datoteka)
            stolpci = next(podatki)
            for vrstica in podatki:
                vrstica = {k: None if v == "" else v for k, v in zip(stolpci, vrstica)}
                self.dodaj_vrstico(**vrstica)

    def izprazni(self):
        """
        Metoda za praznjenje tabele.
        """
        self.conn.execute("DELETE FROM {};".format(self.ime))

    def dodajanje(self, stolpci=None):
        """
        Metoda za gradnjo poizvedbe.
        Argumenti:
        - stolpci: seznam stolpcev
        """
        return "INSERT INTO {} ({}) VALUES ({});" \
            .format(self.ime, ", ".join(stolpci),
                    ", ".join(PARAM_FMT.format(s) for s in stolpci))

    def dodaj_vrstico(self, /, **podatki):
        """
        Metoda za dodajanje vrstice.
        Argumenti:
        - poimenovani parametri: vrednosti v ustreznih stolpcih
        """
        podatki = {kljuc: vrednost for kljuc, vrednost in podatki.items() if vrednost is not None}
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.conn.execute(poizvedba, podatki)
        return cur.lastrowid


class Uporabnik(Tabela):
    """
    Tabela za uporabnike.
    """
    ime = "uporabnik"
    podatki = "podatki/uporabnik.csv"

    def ustvari(self):
        """
        Ustvari tabelo uporabnik.
        """
        self.conn.execute("""
            CREATE TABLE uporabnik (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ime       TEXT NOT NULL UNIQUE,
                zgostitev TEXT NOT NULL,
                sol       TEXT NOT NULL
            )
        """)

    def dodaj_vrstico(self, /, **podatki):
        """
        Dodaj uporabnika.
        Če sol ni podana, zašifrira podano geslo.
        Argumenti:
        - poimenovani parametri: vrednosti v ustreznih stolpcih
        """
        if podatki.get("sol", None) is None and podatki.get("zgostitev", None) is not None:
            podatki["zgostitev"], podatki["sol"] = sifriraj_geslo(podatki["zgostitev"])
        return super().dodaj_vrstico(**podatki)


class Podjetje(Tabela):
    """
    Tabela za Podjetja.
    """
    ime = "podjetje"

    def ustvari(self):
        """
        Ustvari tabelo podjetje.
        """
        self.conn.execute("""
            CREATE TABLE podjetje (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT UNIQUE NOT NULL,
                [datum ustanovitve] as DATE NOT NULL,
                država TEXT NOT NULL,
                opis TEXT  
            );
        """)




class Igra(Tabela):
    """
    Tabela za oznake.
    """
    ime = "igra"

    def ustvari(self):
        """
        Ustvari tabelo Igra.
        """
        self.conn.execute("""
            CREATE TABLE igra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                [ime igre] TEXT NOT NULL,
                [datum izdaje] DATE NOT NULL,
                ocena FLOAT NOT NULL,
                žanr TEXT NOT NULL
                opis TEXT
            );
        """)


class Platforma(Tabela):
    """
    Tabela za platforme.
    """
    ime = "platforma"
    podatki = "podatki/film.csv"

    def __init__(self, conn, oznaka):
        """
        Konstruktor tabele filmov.
        Argumenti:
        - conn: povezava na bazo
        - oznaka: tabela za oznake
        """
        super().__init__(conn)
        self.oznaka = oznaka

    def ustvari(self):
        """
        Ustavari tabelo film.
        """
        self.conn.execute("""
            CREATE TABLE film (
                id        INTEGER PRIMARY KEY,
                ime       TEXT NOT NULL,
                tip   TEXT NOT NULL,
                [datum izdaje] DATE NOT NULL,
                opis     TEXT,
                oznaka    TEXT    REFERENCES oznaka (kratica),
            );
        """)

class Oseba(Tabela):
    """
    Tabela za osebe.
    """
    ime = "oseba"
    podatki = "podatki/oseba.csv"

    def ustvari(self):
        """
        Ustvari tabelo oseba.
        """
        self.conn.execute("""
            CREATE TABLE oseba (
                id  INTEGER PRIMARY KEY,
                ime TEXT
            );
        """)


class Vloga(Tabela):
    """
    Tabela za vloge.
    """
    ime = "vloga"
    podatki = "podatki/vloga.csv"

    def ustvari(self):
        """
        Ustvari tabelo vloga.
        """
        self.conn.execute("""
            CREATE TABLE vloga (
                film  INTEGER   REFERENCES film (id),
                oseba INTEGER   REFERENCES oseba (id),
                tip   CHARACTER CHECK (tip IN ('I',
                                'R') ),
                mesto INTEGER,
                PRIMARY KEY (
                    film,
                    oseba,
                    tip
                )
            );
        """)


class Pripada(Tabela):
    """
    Tabela za relacijo pripadnosti filma žanru.
    """
    ime = "pripada"
    podatki = "podatki/zanr.csv"

    def __init__(self, conn, zanr):
        """
        Konstruktor tabele pripadnosti žanrom.
        Argumenti:
        - conn: povezava na bazo
        - zanr: tabela za žanre
        """
        super().__init__(conn)
        self.zanr = zanr

    def ustvari(self):
        """
        Ustvari tabelo pripada.
        """
        self.conn.execute("""
            CREATE TABLE pripada (
                film INTEGER REFERENCES film (id),
                zanr INTEGER REFERENCES zanr (id),
                PRIMARY KEY (
                    film,
                    zanr
                )
            );
        """)

    def dodaj_vrstico(self, /, **podatki):
        """
        Dodaj pripadnost filma in pripadajoči žanr.
        Argumenti:
        - podatki: slovar s podatki o pripadnosti
        """
        if podatki.get("naziv", None) is not None:
            podatki["zanr"] = self.zanr.dodaj_vrstico(naziv=podatki["naziv"])
            del podatki["naziv"]
        return super().dodaj_vrstico(**podatki)


def ustvari_tabele(tabele):
    """
    Ustvari podane tabele.
    """
    for t in tabele:
        t.ustvari()


def izbrisi_tabele(tabele):
    """
    Izbriši podane tabele.
    """
    for t in tabele:
        t.izbrisi()


def uvozi_podatke(tabele):
    """
    Uvozi podatke v podane tabele.
    """
    for t in tabele:
        t.uvozi()


def izprazni_tabele(tabele):
    """
    Izprazni podane tabele.
    """
    for t in tabele:
        t.izprazni()


def ustvari_bazo(conn):
    """
    Izvede ustvarjanje baze.
    """
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele)


def pripravi_tabele(conn):
    """
    Pripravi objekte za tabele.
    """
    uporabnik = Uporabnik(conn)
    zanr = Zanr(conn)
    oznaka = Oznaka(conn)
    film = Film(conn, oznaka)
    oseba = Oseba(conn)
    vloga = Vloga(conn)
    pripada = Pripada(conn, zanr)
    return [uporabnik, zanr, oznaka, film, oseba, vloga, pripada]


def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, če ta še ne obstaja.
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)