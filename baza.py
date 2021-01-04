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
    Tabela za igre.
    """

    ime = "igra"
    podatki = "podatki/_.csv" # RABIVA DODATI

    def ustvari(self):
        """
        Ustvari tabelo Igra.
        """
        self.conn.execute("""
            CREATE TABLE igra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                [ime igre] TEXT NOT NULL,
                razvijalec TEXT REFRENCES razvijalec(razvijalec)
                [datum izdaje] DATE NOT NULL,
                ocena FLOAT NOT NULL,
                žanr TEXT NOT NULL,
                opis TEXT,
            );
        """)


class Platforma(Tabela):
    """
    Tabela za platforme.
    """
    ime = "platforma"
    podatki = "podatki/_.csv" # RABIVA DODATI

    def __init__(self, conn, podjetje):
        """
        Konstruktor tabele platform.
        Argumenti:
        - conn: povezava na bazo
        - podjejte: tabela za podjetje
        """
        super().__init__(conn)
        self.podjetje = podjetje

    def ustvari(self):
        """
        Ustavari tabelo Platforma.
        """
        self.conn.execute("""
            CREATE TABLE platforma (
                id        INTEGER PRIMARY KEY,
                ime       TEXT NOT NULL,
                tip   TEXT NOT NULL,
                [datum izdaje] DATE NOT NULL,
                opis     TEXT,
                podjetje    TEXT    REFERENCES podjetje (ime),
            );
        """)

class Razvijalec(Tabela):
    """
    Tabela za razvijalce.
    """
    ime = "razvijalec"
    podatki = "podatki/_.csv" # MANJKA

    def __init__(self, conn, razvijalec):
        """
        Konstruktor tabele platform.
        Argumenti:
        - conn: povezava na bazo
        - podjetje: tabela za podjetje
        """
        super().__init__(conn)
        self.razvijalec = razvijalec

    def ustvari(self):
        """
        Ustvari tabelo razvijalec.
        """
        self.conn.execute("""
            CREATE TABLE razvijalec (
                id INTEGER PRIMARY KEY,
                razvijalec  TEXT REFERENCES podjetje (ime),
            );
        """)


class Distributer(Tabela):
    """
    Tabela za Distributarja.
    """
    ime = "distributer"
    podatki = "podatki/_.csv" # MANJKA

    def __init__(self, conn, distributer):
        """
        Konstruktor tabele distributerja.
        Argumenti:
        - conn: povezava na bazo
        - podjetje: tabela za podjetje
        """
        super().__init__(conn)
        self.distributer = distributer

    def ustvari(self):
        """
        Ustvari tabelo distributer.
        """
        self.conn.execute("""
            CREATE TABLE distributer (
                id INTEGER PRIMARY KEY,
                distributer  TEXT REFERENCES podjetje (ime),
                )
            );
        """)


class Distributira(Tabela):
    """
    Tabela za relacijo pripadnosti distributerja igre.
    """
    ime = "distributira"
    podatki = "podatki/_.csv" # MANJKA

    def __init__(self, conn, zanr):
        # VPRAŠANJE
        """
        Konstruktor tabele pripadnosti igre.
        Argumenti:
        - conn: povezava na bazo
        - igra: tabela za igre
        """
        super().__init__(conn)
        self.igra = igra

    def ustvari(self):
        """
        Ustvari tabelo distributira.
        """
        self.conn.execute("""
            CREATE TABLE distributira (
                id_igre INTEGER REFERENCES igra (id),
                distributer INTEGER REFERENCES distributer (id),
                PRIMARY KEY (
                    distributer,
                    igra
                )
            );
        """)

    def dodaj_vrstico(self, /, **podatki):
        """
        Dodaj pripadnost igre in pripadajoči distributer.
        Argumenti:
        - podatki: slovar s podatki o distribuciji
        """
        if podatki.get("ime igre", None) is not None:
            podatki["igra"] = self.igra.dodaj_vrstico(naziv=podatki["ime igre"])
            del podatki["ime gre"]
        return super().dodaj_vrstico(**podatki)



class Podpira(Tabela):
    """
    Tabela za relacijo pripadnosti platforme igri.
    """
    ime = "podpira"
    podatki = "podatki/_.csv" # MANJKA

    def __init__(self, conn, zanr):
        # VPRAŠANJE
        """
        Konstruktor tabele pripadnosti igre.
        Argumenti:
        - conn: povezava na bazo
        - igra: tabela za igre
        """
        super().__init__(conn)
        self.igra = igra

    def ustvari(self):
        """
        Ustvari tabelo podpira.
        """
        self.conn.execute("""
            CREATE TABLE podpira (
                id_igre INTEGER REFERENCES igra (id),
                platforma INTEGER REFERENCES platforma (id),
                PRIMARY KEY (
                    platforma,
                    igra
                )
            );
        """)

    def dodaj_vrstico(self, /, **podatki):
        """
        Dodaj pripadnost filma in pripadajoči žanr.
        Argumenti:
        - podatki: slovar s podatki o pripadnosti
        """
        if podatki.get("ime igre", None) is not None:
            podatki["igra"] = self.igra.dodaj_vrstico(naziv=podatki["ime igre"]) # VPRAŠANJE
            del podatki["ime igre"]
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
    podjetje = Podjetje(conn)
    platforma = Platforma(conn, podjetje)
    distributer = Distributer(conn)
    razvijalec = Razvijalec(conn)
    igra = Igra(conn, razvijalec)
    distributira = Distributira(conn, igra)
    podpira = Podpira(conn, igra)
    return [uporabnik, igra, podjetje, platforma, distributer, distributira, razvijalec, podpira]


def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, če ta še ne obstaja.
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)