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

    def dodaj_vrstico(self,  **podatki):
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

    def dodaj_vrstico(self,  **podatki):
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
    podatki = "podatki/podjetje.csv"

    def ustvari(self):
        """
        Ustvari tabelo podjetje.
        """
        self.conn.execute("""
            CREATE TABLE podjetje (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT NOT NULL UNIQUE,
                drzava TEXT,
                datum_ustanovitve DATE,
                opis TEXT
            );
        """)

    def dodaj_vrstico(self,  **podatki):
        """
        Doda podjetje v bazo.
        """
        return super().dodaj_vrstico(**podatki)


class Igra(Tabela):
    """
    Tabela za igre.
    """

    ime = "igra"
    podatki = "podatki/igre.csv"

    def __init__(self, conn, podjetje):
        """
        Konstruktor tabele platform.
        Argumenti:
        - conn: povezava na bazo
        - podjetje: tabela za podjetje
        """
        super().__init__(conn)
        self.podjetje = podjetje

    def ustvari(self):
        """
        Ustvari tabelo Igra.
        """
        self.conn.execute("""
            CREATE TABLE igra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ime_igre TEXT NOT NULL,
                datum_izdaje DATE NOT NULL,
                cena FLOAT,
                vsebuje TEXT,
                razvija INTEGER REFERENCES podjetje(id),
                povprecno_igranje FLOAT,
                mediana FLOAT,
                ocena FLOAT
              
            );
        """)

    def dodaj_vrstico(self,  **podatki):
        """
        Doda igro v bazo.
        """
        assert "razvija" in podatki
        sql = """
                    SELECT DISTINCT podjetje.id
                    FROM podjetje 
                    WHERE podjetje.ime = ?
                """

        for razvijalec in self.conn.execute(sql, [podatki["razvija"]]):
            podatki["razvija"] = razvijalec[0]

        return super().dodaj_vrstico(**podatki)
    

class Platforma(Tabela):
    """
    Tabela za platforme.
    """
    ime = "platforma"
    podatki = "podatki/platforme.csv"

    def ustvari(self):
        """
        Ustavari tabelo Platforma.
        """
        self.conn.execute("""
            CREATE TABLE platforma (
                id        INTEGER PRIMARY KEY,
                ime       TEXT NOT NULL,
                tip   TEXT NOT NULL,
                datum_izdaje DATE NOT NULL,
                opis     TEXT,
                podjetje    TEXT
            );
        """)


class Distributira(Tabela):
    """
    Tabela za relacijo pripadnosti distributerja igre.
    """
    ime = "distributira"
    podatki = "podatki/publisherji.csv"

    def __init__(self, conn, igra):
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
                podjetje INTEGER REFERENCES podjetje (id),
                ime_igre INTEGER REFERENCES igra (id),
                PRIMARY KEY (
                    ime_igre,
                    podjetje
                )
            );
        """)

    def dodaj_vrstico(self, **podatki):
        """
        Dodaj relacijo med igro in pripadajočim distributerjem.
        """
        assert "podjetje" in podatki
        sql = """
                    SELECT podjetje.id
                    FROM podjetje
                    WHERE ime = ?
                """
        for podjetje in self.conn.execute(sql, [podatki["podjetje"]]):
            podatki["podjetje"] = podjetje[0]
        return super().dodaj_vrstico(**podatki)


class Podpira(Tabela):
    """
    Tabela za relacijo pripadnosti platforme igri.
    """
    ime = "podpira"
    podatki = "podatki/podpira.csv"

    def __init__(self, conn, igra):
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
                ime_igre INTEGER REFERENCES igra (id),
                platforma INTEGER REFERENCES platforma (id),
                PRIMARY KEY (
                    ime_igre,
                    platforma
                )
            );
        """)

    def dodaj_vrstico(self, **podatki):
        """
        Doda relacijo med igro in platformo.
        """
        assert "platforma" in podatki
        sql = """
                    SELECT platforma.id
                    FROM platforma
                    WHERE ime == ?
                """

        for platforma in self.conn.execute(sql, [podatki["platforma"]]):
            podatki["platforma"] = platforma[0]
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
    platforma = Platforma(conn)
    igra = Igra(conn, podjetje)
    distributira = Distributira(conn, igra)
    podpira = Podpira(conn, igra)
    return [uporabnik, podjetje, igra, platforma, distributira, podpira]


def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, če ta še ne obstaja.
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)