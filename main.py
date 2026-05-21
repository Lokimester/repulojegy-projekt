# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from datetime import datetime


# ==============================================================================
# 1. FŐ OSZTÁLYOK (Reprezentáció és Logika)
# ==============================================================================

class Jarat(ABC):
    """Absztrakt alaposztály a járatok számára."""

    def __init__(self, jaratszam: str, celallomas: str, alap_ar: int):
        self._jaratszam = jaratszam  # Non-public attribútum
        self._celallomas = celallomas  # Non-public attribútum
        self._alap_ar = alap_ar  # Non-public attribútum

    # Getterek a tulajdonságok eléréséhez
    @property
    def jaratszam(self) -> str:
        return self._jaratszam

    @property
    def celallomas(self) -> str:
        return self._celallomas

    @abstractmethod
    def jegyar_szamitas(self) -> int:
        """Absztrakt metódus, amit a leszármazottaknak kötelező megvalósítani."""
        pass


class BelfoldiJarat(Jarat):
    """Belföldi járat osztály - fix kedvezménnyel (olcsóbb)."""

    def __init__(self, jaratszam: str, celallomas: str, alap_ar: int):
        super().__init__(jaratszam, celallomas, alap_ar)
        self._kedvezmeny = 0.8  # 20% kedvezmény a belföldi járatokra

    def jegyar_szamitas(self) -> int:
        return int(self._alap_ar * self._kedvezmeny)

    def __str__(self):
        return f"Belföldi járat [{self.jaratszam}] -> {self.celallomas} (Ár: {self.jegyar_szamitas()} Ft)"


class NemzetkoziJarat(Jarat):
    """Nemzetközi járat osztály - extra illetékkel (magasabb ár)."""

    def __init__(self, jaratszam: str, celallomas: str, alap_ar: int):
        super().__init__(jaratszam, celallomas, alap_ar)
        self._illetek = 1.25  # 25% felár a nemzetközi adók/illetékek miatt

    def jegyar_szamitas(self) -> int:
        return int(self._alap_ar * self._illetek)

    def __str__(self):
        return f"Nemzetközi járat [{self.jaratszam}] -> {self.celallomas} (Ár: {self.jegyar_szamitas()} Ft)"


class JegyFoglalas:
    """Egy konkrét jegyfoglalást reprezentáló osztály (Ékezet nélkül a kód biztonságáért)."""

    def __init__(self, foglalasi_id: int, jarat: Jarat, utas_neve: str, datum: datetime):
        self._foglalasi_id = foglalasi_id
        self._jarat = jarat
        self._utas_neve = utas_neve
        self._datum = datum

    @property
    def foglalasi_id(self) -> int:
        return self._foglalasi_id

    @property
    def jarat(self) -> Jarat:
        return self._jarat

    @property
    def utas_neve(self) -> str:
        return self._utas_neve

    @property
    def datum(self) -> datetime:
        return self._datum

    def __str__(self):
        return f"ID: {self._foglalasi_id} | Utas: {self._utas_neve} | Járat: {self._jarat.jaratszam} ({self._jarat.celallomas}) | Dátum: {self._datum.strftime('%Y-%m-%d')} | Ár: {self._jarat.jegyar_szamitas()} Ft"


class LegiTarsasag:
    """A légitársaságot reprezentáló osztály, amely kezeli a járatokat és foglalásokat."""

    def __init__(self, nev: str):
        self._nev = nev
        self._jaratok = []
        self._foglalasok = []
        self._foglalasi_szamlalo = 1000  # Innen indulnak a foglalási ID-k

    @property
    def nev(self) -> str:
        return self._nev

    def jarat_hozzaadas(self, jarat: Jarat):
        self._jaratok.append(jarat)

    def jarat_keres(self, jaratszam: str) -> Jarat:
        """Megkeres egy járatot a járatszáma alapján."""
        for jarat in self._jaratok:
            if jarat.jaratszam.upper() == jaratszam.upper():
                return jarat
        return None

    def jaratok_listazasa(self):
        """Segédfunkció az elérhető járatok megjelenítéséhez."""
        if not self._jaratok:
            print("Nincsenek elérhető járatok.")
            return
        for jarat in self._jaratok:
            print(f"  {jarat}")

    # --- KÖVETELMÉNY FUNKCIÓK ---

    def jegy_foglalasa(self, jaratszam: str, utas_neve: str, datum_str: str) -> int:
        """Jegy foglalása adatvalidációval és hibakezeléssel."""
        # 1. Járat ellenőrzése
        jarat = self.jarat_keres(jaratszam)
        if not jarat:
            raise ValueError(f"Hiba: A '{jaratszam}' járatszámú járat nem létezik!")

        # 2. Dátum ellenőrzése és validálása
        try:
            foglalasi_datum = datetime.strptime(datum_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Hiba: Hibás dátum formátum! Kérjük 'ÉÉÉÉ-HH-NN' formátumot használj.")

        if foglalasi_datum < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            raise ValueError("Hiba: Nem lehet múltbeli dátumra foglalni!")

        # 3. Foglalás létrehozása
        self._foglalasi_szamlalo += 1
        uj_foglalas = JegyFoglalas(self._foglalasi_szamlalo, jarat, utas_neve, foglalasi_datum)
        self._foglalasok.append(uj_foglalas)

        return jarat.jegyar_szamitas()

    def foglalasz_lemondasa(self, foglalasi_id: int) -> bool:
        """Foglalás lemondása validációval."""
        for foglalas in self._foglalasok:
            if foglalas.foglalasi_id == foglalasi_id:
                self._foglalasok.remove(foglalas)
                return True
        raise ValueError(f"Hiba: A '{foglalasi_id}' azonosítójú foglalás nem létezik!")

    def foglalasok_listazasa(self):
        """Aktuális foglalások listázása."""
        if not self._foglalasok:
            print("\n[Rendszer] Jelenleg nincsenek aktív foglalások.")
            return

        print(f"\n--- Aktuális Foglalások ({self._nev}) ---")
        for foglalas in self._foglalasok:
            print(foglalas)


# ==============================================================================
# 2. ELŐKÉSZÍTÉS (Adatok inicializálása)
# ==============================================================================

def rendszer_inicializalasa() -> LegiTarsasag:
    """Létrehozza a légitársaságot, feltölti 3 járattal és 6 alapértelmezett foglalással."""
    tarsasag = LegiTarsasag("AeroHungaria")

    # 3 járat hozzáadása (1 belföldi, 2 nemzetközi)
    j1 = BelfoldiJarat("BUD101", "Debrecen", 20000)
    j2 = NemzetkoziJarat("LON202", "London", 50000)
    j3 = NemzetkoziJarat("PAR303", "Párizs", 60000)

    tarsasag.jarat_hozzaadas(j1)
    tarsasag.jarat_hozzaadas(j2)
    tarsasag.jarat_hozzaadas(j3)

    # 6 foglalás előre bevitele (jövőbeli dátumokkal a validáció miatt)
    tarsasag.jegy_foglalasa("BUD101", "Kovács János", "2026-06-15")
    tarsasag.jegy_foglalasa("BUD101", "Nagy Erika", "2026-06-20")
    tarsasag.jegy_foglalasa("LON202", "Szabó Péter", "2026-07-01")
    tarsasag.jegy_foglalasa("LON202", "Tóth Gábor", "2026-07-01")
    tarsasag.jegy_foglalasa("PAR303", "Kiss Ilona", "2026-08-12")
    tarsasag.jegy_foglalasa("PAR303", "Horváth Tamás", "2026-08-15")

    return tarsasag


# ==============================================================================
# 3. FELHASZNÁLÓI INTERFÉSZ (Konzolos menü)
# ==============================================================================

def main():
    tarsasag = rendszer_inicializalasa()

    while True:
        print("\n========================================")
        print(f"     {tarsasag.nev} - FOGLALÁSI RENDSZER")
        print("========================================")
        print("1. Jegy foglalása")
        print("2. Foglalás lemondása")
        print("3. Foglalások listázása")
        print("4. Elérhető járatok megtekintése")
        print("5. Kilépés")
        print("----------------------------------------")

        valasztas = input("Kérlek válassz egy menüpontot (1-5): ").strip()

        if valasztas == "1":
            print("\n--- ÚJ JEGY FOGLALÁSA ---")
            tarsasag.jaratok_listazasa()
            print("----------------------------------------")
            jaratszam = input("Adja meg a járatszámot: ").strip()
            utas_neve = input("Adja meg az utas nevét: ").strip()
            datum_str = input("Adja meg a dátumot (ÉÉÉÉ-HH-NN, pl. 2026-06-01): ").strip()

            if not utas_neve:
                print("[Hiba] Az utas neve nem lehet üres!")
                continue

            try:
                ar = tarsasag.jegy_foglalasa(jaratszam, utas_neve, datum_str)
                print(f"\n[Sikeres foglalás] A foglalás rögzítve lett! A jegy ára: {ar} Ft")
            except ValueError as e:
                print(f"\n[Sikertelen foglalás] {e}")

        elif valasztas == "2":
            print("\n--- FOGLALÁS LEMONDÁSA ---")
            tarsasag.foglalasok_listazasa()
            print("----------------------------------------")
            try:
                id_input = input("Adja meg a lemondani kívánt foglalás ID-ját: ").strip()
                foglalasi_id = int(id_input)

                tarsasag.foglalasz_lemondasa(foglalasi_id)
                print(f"\n[Sikeres lemondás] A {foglalasi_id} azonosítójú foglalást töröltük.")
            except ValueError as e:
                if "invalid literal for int()" in str(e):
                    print("\n[Hiba] Kérjük, számot adjon meg az azonosítóhoz!")
                else:
                    print(f"\n[Sikertelen lemondás] {e}")

        elif valasztas == "3":
            tarsasag.foglalasok_listazasa()

        elif valasztas == "4":
            print("\n--- ELÉRHETŐ JÁRATOK ---")
            tarsasag.jaratok_listazasa()

        elif valasztas == "5":
            print(f"\nKöszönjük, hogy az {tarsasag.nev} rendszerét használta! Viszlát!")
            break
        else:
            print("\n[Hiba] Érvénytelen választás! Kérjük 1 és 5 közötti számot adjon meg.")


if __name__ == "__main__":
    main()