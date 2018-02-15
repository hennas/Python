import haravasto
import random
import math
import time
import csv
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText

# Tiedosto, johon tallennetaan pelien tiedot
TIEDOSTO = "miinantallaajaTilastot.csv"
# Sanakirja, joka pitää muistissa pelaajalle piirrettävän kentän (aluksi täysin tyhjä), sekä pohjana toimivan paljastetun kentän (ts. sisältää miinojen sijainnit sekä numerolliset ruudut lukuunottamatta '0' ruutuja).
tila = {
    "kentta": None,
    "pohja_kentta": None
}
# Sanakirja, johon lisätään pelin lopussa tiedostoon tallennettavat tiedot
tallennettavat_tiedot = {
    "aloitusPmvJaAika": None,
    "aloitusAika": None,
    "lopetusAika": None,
    "vuorot": 0,
    "kentanKoko": None,
    "miinat": None,
    "lopputulos": None
}

def lataa_tiedosto(tiedosto):
    """
    Lataa tiedostosta tiedot ja palauttaa ne listassa. Jos tiedoston avaamisessa tapahtuu virhe, funktio ei palauta mitään.
    """
    tiedot = []    
    try:
        with open(tiedosto, newline="") as lahde:
            reader = csv.reader(lahde)
            for rivi in reader:
                tiedot.append(rivi)
    except IOError:
        tkinter.messagebox.showerror("Virhe", "Tiedoston lataaminen ei onnistunut")
    else:
        return tiedot
    
def tallenna_tiedostoon(tiedosto):
    """
    Tallentaa pelituloksen tiedostoon.
    """
    aloitus = tallennettavat_tiedot["aloitusPmvJaAika"]
    peliminuutit = (tallennettavat_tiedot["lopetusAika"] - tallennettavat_tiedot["aloitusAika"]) / 60
    vuorot = tallennettavat_tiedot["vuorot"]
    kentta = tallennettavat_tiedot["kentanKoko"]
    miinat = tallennettavat_tiedot["miinat"]
    lopputulos = tallennettavat_tiedot["lopputulos"]
    
    try:
        with open(tiedosto, "a", newline="") as kohde:
            csv.writer(kohde).writerow([aloitus, peliminuutit, vuorot, kentta, miinat, lopputulos])
    except IOError:
        tkinter.messagebox.showerror("Virhe", "Pelitietojen tallennus tiedostoon epäonnistui")

def tarkista_koordinaatit(x, y, leveys, korkeus):
    """
    Tarkistaa ovatko annetut x, y -koordinaatit annettujen rajojen sisällä. 
    Palauttaa True, jos koordinaatit ovat rajojen sisällä; muuten palautetaan False.
    """
    if x < 0 or y < 0 or x >= leveys or y >= korkeus:
        return False
    else:
        return True

def tulvataytto(kentta, pohjakentta, x, y):
    """
    Merkitsee kentällä olevat tuntemattomat alueet tyhjiksi siten, että täyttö aloitetaan annetusta x, y -pisteestä.
    """
    taytto_pisteet = [(x, y)]
    while taytto_pisteet:
        x, y = taytto_pisteet.pop()
        # Jos pohjakentän ruudussa on " ", se muutetaan merkkijonoksi "0", mikä erottaa jo paljastetut tyhjät ruudut paljastamattomista ja saa pygletin piirtämään pelaajalle tyhjän ruudun (sijoitus piirrettävään kenttään pari riviä alempana)
        if pohjakentta[y][x] == " ":
            pohjakentta[y][x] = "0"
        kentta[y][x] = pohjakentta[y][x]
        # Jos kentässä on kohdassa (x, y) merkkijono 0, mennään silmukkaan. Tarkistus täytyy tehdä, sillä silmukka ottaa listaan myös ruudut, joissa on joku muu luku, eikä näiden ympäristöä enää pidä käydä läpi.
        if pohjakentta[y][x] == "0":
            for i in range(y - 1, y + 2):
                for j in range(x - 1, x + 2):
                    if tarkista_koordinaatit(j, i, len(kentta[0]), len(kentta)) and pohjakentta[i][j] != "0": #Täytyy tarkistaa, että ei oteta jo paljastettuja tyhjiä ruutuja listaan uudestaan, muuten saadaan infinite loop
                            taytto_pisteet.append((j, i))
                        
def laske_ymparoivat_miinat(x, y, kentta, leveys, korkeus):
    """
    Laskee kentässä yhden pisteen ympärillä olevat miinat ja palauttaa niiden lukumäärän. 
    Funktio toimii sillä oletuksella, että valitussa ruudussa ei ole miinaa - jos on, sekin lasketaan mukaan.
    """
    miinoja = 0
    for i in range(y - 1, y + 2):
        for j in range(x - 1, x + 2):
            if tarkista_koordinaatit(j, i, leveys, korkeus) and kentta[i][j] == "x":
                miinoja += 1
    return miinoja
    
def miinoita(kentta, vapaat, miinojen_maara):
    """
    Asettaa kentällä n kpl miinoja satunnaisiin paikkoihin. Parametreina saa viittauksen pohjakenttään, listan vapaista ruuduista (listassa (x,y) monikkoja), ja miinojen määrän kokonaislukuna
    """
    miinat = random.sample(vapaat, miinojen_maara)
    for x, y in miinat:
        kentta[y][x] = "x"
        
def tayta_pohja_kentta(kentta, leveys, korkeus):
    """
    Täyttää pohjakenttään tiedon numeroruuduista (1-8) laskemalla ruudun ympärillä olevat miinat. Jos miinoja on 0, sitä ei merkitä vielä pohjakenttään (ks. tulvataytto-funktio)
    """
    for x in range(leveys):
        for y in range(korkeus):
            miinat = laske_ymparoivat_miinat(x, y, kentta, leveys, korkeus)
            if kentta[y][x] != "x" and miinat > 0:
                    kentta[y][x] = miinat
def piirra():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän ruudut näkyviin peli-ikkunaan. 
    Funktiota kutsutaan aina kun pelimoottori pyytää ruudun näkymän päivitystä.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    for indeksi, rivi in enumerate(tila["kentta"]):
        for i, avain in enumerate(rivi):
            haravasto.lisaa_piirrettava_ruutu(avain, i * 40, indeksi * 40)  
    haravasto.piirra_ruudut()
    lopputulos = tallennettavat_tiedot["lopputulos"]
    if lopputulos != None:
        if lopputulos == "Häviö":
            haravasto.piirra_tekstia("Hävisit!", 0, len(tila["kentta"]) * 40)
        else:
            haravasto.piirra_tekstia("Voitit!", 0, len(tila["kentta"]) * 40)
    
def hiiri_kasittelija(x, y, nappi, muokkausnapit):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä. 
    """
    x = math.floor(x / 40)
    y = math.floor(y / 40)
    pohjakentta = tila["pohja_kentta"]
    kentta = tila["kentta"]
        
    if tallennettavat_tiedot["lopputulos"] == None:
        if nappi == haravasto.HIIRI_VASEN:
            tallennettavat_tiedot["vuorot"] += 1
            painettu_vasenta(kentta, pohjakentta, x, y)             
        elif nappi == haravasto.HIIRI_OIKEA:
            if kentta[y][x] == " ":
                kentta[y][x] = "f"
            elif kentta[y][x] == "f":
                kentta[y][x] = " "
            
def painettu_vasenta(kentta, pohjakentta, x, y):
    """
    Hoitaa toiminnot pelaajan painettua vasenta hiiren painiketta kentän yllä.
    """
    leveys = len(kentta[0])
    korkeus = len(kentta)
    
    if pohjakentta[y][x] == "x":
        tallennettavat_tiedot["lopputulos"] = "Häviö"
        tallennettavat_tiedot["lopetusAika"] = time.time()
        # Näyttää miinojen paikat
        for i in range(leveys):
            for j in range(korkeus):
                if pohjakentta[j][i] == "x":
                    kentta[j][i] = "x"
        # Näyttää miinan, jota pelaaja painoi.
        kentta[y][x] = "h"
        uusi_ikkunan_koko()
        tallenna_tiedostoon(TIEDOSTO)
        # Häviön jälkeen palaa takaisin, jotta koodi ei tarkista turhaan voittoa funktion lopussa.
        return
    elif pohjakentta[y][x] == " ":
        tulvataytto(kentta, pohjakentta, x, y)
    else:
        kentta[y][x] = pohjakentta[y][x]
    # Jokaisen painalluksen jälkeen tarkistaa, onko pelaaja voittanut.     
    if onko_voitettu():
        tallennettavat_tiedot["lopputulos"] = "Voitto" 
        tallennettavat_tiedot["lopetusAika"] = time.time()
        uusi_ikkunan_koko()
        tallenna_tiedostoon(TIEDOSTO)
        
def onko_voitettu():
    """
    Tarkistaa, onko pelaaja voittanut. Palauttaa True, jos on, ja False, jos ei.
    Pelaaja on voittanut, jos pelaajalle piirrettävässä kentässä olevat tyhjät ruudut ovat vain miinojen päällä ja mahdolliset lipulla merkityt ruudut ("f") ovat myös vain miinojen päällä.
    """
    pohjakentta = tila["pohja_kentta"]
    kentta = tila["kentta"]
    leveys = len(tila["kentta"][0])
    korkeus = len(tila["kentta"])
    
    for x in range(leveys):
        for y in range(korkeus):
            # Jos kentällä on tyhjä tai lippu jonkun muun kuin miinan päällä, palautetaan heti False. Jos päästään silmukan loppuun ilman, että on löytynyt yhtäkään tyhjää tai lippua jonkun muun kuin miinan päällä, pelaaja on voittanut
            if (kentta[y][x] == " " and pohjakentta[y][x] != "x") or (kentta[y][x] == "f" and pohjakentta[y][x] != "x"):
                return False
        
    return True
    
def uusi_ikkunan_koko():
    """
    Muuttaa ikkunan koon, kun pelaaja häviää/voittaa, jotta tekstilaatikolle olisi tilaa (ks. piirra-funktio)
    """
    leveys = len(tila["kentta"][0]) * 40
    uusikorkeus = len(tila["kentta"]) * 40 + 50
    haravasto.muuta_ikkunan_koko(leveys, uusikorkeus)

def luo_kentta(leveys, korkeus):
    """
    Luo pelaajan antaman kentän koon pohjalta kaksiulotteisen listan, joka esittää tyhjää kenttää ja palauttaa sen.
    """
    kentta = []
    for rivi in range(korkeus):
        kentta.append([])
        for sarake in range(leveys):
            kentta[-1].append(" ")

    return kentta
          
def tyhjat_ruudut(kentta, leveys, korkeus):
    """
    Palauttaa listan kentan tyhjistä ruuduista, listan alkioina monikot, joihin on tallennettu x- ja y-koordinaatit.
    """
    tyhjat = []
    for x in range(leveys):
        for y in range(korkeus):
            if kentta[y][x] == " ":
                tyhjat.append((x, y))
    return tyhjat
    
def laske_voitot(tiedot):
    """
    Laskee, kuinka monta voittoa on pelitiedoissa.
    """
    voittoja = 0
    for rivi in tiedot:
        if rivi[5] == "Voitto":
            voittoja += 1
    return voittoja
    
def nayta_tilastot():
    """
    Saa tiedot lataa_tiedosto-funktion kautta ja jos kyseinen funktio palauttaa tietoja, koostaa niistä graafisen esityksen uuteen ikkunaan.
    """
    tiedot = lataa_tiedosto(TIEDOSTO)
    # Tarkistus estää ikkunan näyttämisen, jos tiedostoa ei ole olemassa (eli lataa_tiedosto-funktio ei palauta mitään)
    if tiedot:
        tilastoikkuna = tkinter.Toplevel()
        tilastoikkuna.title("Tilastot")
        tilastoikkuna.geometry("980x250")
        tilastoikkuna.grab_set()

        tekstilaatikko = ScrolledText(tilastoikkuna, width=130, height=10, font=("sans-serif", 10))
        try:
            for pvm, peliminuutit, vuorot, kentankoko, miinat, lopputulos in tiedot:
                minuuttiraja = peliminuutit.index(".")
                kokominuutit = int(peliminuutit[:minuuttiraja])
                peliminuutit = float(peliminuutit)
                sekunnit = round((peliminuutit - kokominuutit) * 60)
                tilastorivi = "{} aloitit pelin, joka kesti {} minuuttia ja {} sekuntia. Kentän koko oli {}, miinoja {}, teit {} siirtoa ennen loppua. Lopputulos: {}\n".format(pvm, kokominuutit, sekunnit, kentankoko, miinat, vuorot, lopputulos)
                tekstilaatikko.insert(tkinter.INSERT, tilastorivi)          
        except ValueError:
            tkinter.messagebox.showerror("Virhe", "Tiedostosi on vahingoittunut, tilastoja ei voida näyttää.")
        else:
            yhteenveto = tkinter.Label(tilastoikkuna, text="", font=("sans-serif", 10), pady=20)
            pelienmaara = len(tiedot)
            voittoja = laske_voitot(tiedot)
            yhteenveto.config(text="Pelattuja pelejä: {}   Voitettuja pelejä: {}   Voittoprosentti: {:.1f}%".format(pelienmaara, voittoja, voittoja / pelienmaara * 100))
            tekstilaatikko.config(state=tkinter.DISABLED)
            yhteenveto.pack()
            tekstilaatikko.pack()
            tilastoikkuna.mainloop()
    
def aloita_peli(leveys, korkeus, miinojen_maara, ikkuna):
    """
    Käynnistää pelin, jos käyttäjältä on saatu oikeanmuotoiset syötteet aloitusikkunaan. Antaa myös viittauksen tkinterin pääikkunaan, jotta se voidaan näyttää uudestaan pelin päätyttyä
    """
    # Nollaa kaksi kohtaa, kun pelaaja aloittaa uuden pelin heti edellisen jälkeen, muuten pelaaminen ei onnistu.
    tallennettavat_tiedot["lopputulos"] = None
    tallennettavat_tiedot["vuorot"] = 0

    tila["kentta"] = luo_kentta(leveys, korkeus)
    tila["pohja_kentta"] = luo_kentta(leveys, korkeus)    

    tyhjat = tyhjat_ruudut(tila["kentta"], leveys, korkeus)        
    miinoita(tila["pohja_kentta"], tyhjat, miinojen_maara)
    tayta_pohja_kentta(tila["pohja_kentta"], len(tila["pohja_kentta"][0]), len(tila["pohja_kentta"]))
        
    tallennettavat_tiedot["aloitusPmvJaAika"] = time.strftime("%d.%m.%Y %H:%M:%S")
    tallennettavat_tiedot["kentanKoko"] = "{}x{}".format(leveys, korkeus)
    tallennettavat_tiedot["miinat"] = miinojen_maara
    tallennettavat_tiedot["aloitusAika"] = time.time()
        
    haravasto.lataa_kuvat("spritet")
    haravasto.luo_ikkuna(leveys * 40, korkeus * 40)
    haravasto.aseta_piirto_kasittelija(piirra)
    haravasto.aseta_hiiri_kasittelija(hiiri_kasittelija)
    haravasto.aloita() 
    ikkuna.deiconify()

def tarkista(koko, miinat, virheilmoitus, ikkuna):
    """
    Tarkistaa, onko käyttäjä antanut oikeanmuotoiset tiedot kentän koolle ja miinojen määrälle. Jos ei, käyttäjälle ilmoitetaan asiasta. Jos on, peli aloitetaan.
    """
    virheilmoitus.config(text="")
    if len(koko) != 2:
        virheilmoitus.config(text="Kentän koko täytyy antaa muodossa leveysxkorkeus!")
        return
    try: 
        leveys = int(koko[0])
        korkeus = int(koko[1])
        miinat = int(miinat)    
    except ValueError:
        virheilmoitus.config(text="Kentän leveyden ja korkeuden sekä miinojen määrän täytyy olla kokonaislukuja!")
    else:
        if leveys < 1 or korkeus < 1:
            virheilmoitus.config(text="Tarkista kentän koko! Olematonta kenttää on vaikea luoda.")
            return
        if leveys == 1 and korkeus == 1:
            virheilmoitus.config(text="1x1 kenttä? Älä nyt viitsi, häviät heti.")
            return
        if miinat < 1 or miinat > leveys * korkeus:
            virheilmoitus.config(text="Kenttää ei pysty miinoittamaan antamallasi arvolla.")
            return
        if miinat == leveys * korkeus:
            virheilmoitus.config(text="Haluat miinoittaa koko kentän? Jätähän nyt jonkinlainen mahdollisuus voittoon.")
            return
        #Piilottaa tkinterin pääikkunan pelin ajaksi
        ikkuna.withdraw()
        aloita_peli(leveys, korkeus, miinat, ikkuna)

def main():
    """
    Luo aloitusikkunan.
    """
    ikkuna = tkinter.Tk()
    ikkuna.title("Aloitusvalikko")
    ikkuna.geometry("490x300")
    
    alkulabel = tkinter.Label(ikkuna, text="Tervetuloa pelaamaan Miinantallaajaa!", pady=10, font=("sans-serif", 15))
    ohjelabel = tkinter.Label(ikkuna, text="Täytä seuraavat kentät, jos haluat aloittaa uuden pelin.", font=("sans-serif", 10))
    kenttalabel = tkinter.Label(ikkuna, text="Anna kentän koko muodossa leveysxkorkeus (esim. 10x10): ", font=("sans-serif", 10))
    miinalabel = tkinter.Label(ikkuna, text="Anna miinojen lukumäärä: ", font=("sans-serif", 10))
    virheilmoitus = tkinter.Label(ikkuna, text="", font=("sans-serif", 10))
    
    kysykentankoko = tkinter.Entry(ikkuna, width=7, exportselection=0, justify=tkinter.CENTER, font=("sans-serif", 10))
    kysymiinat = tkinter.Entry(ikkuna, width=7, exportselection=0, justify=tkinter.CENTER, font=("sans-serif", 10))
    
    aloitusnappi = tkinter.Button(ikkuna, text="Aloita peli", command=lambda: tarkista(kysykentankoko.get().split("x"), kysymiinat.get(), virheilmoitus, ikkuna), font=("sans-serif", 10))
    tilastonappi = tkinter.Button(ikkuna, text="Tilastot", command=nayta_tilastot, font=("sans-serif", 10))
    lopetanappi = tkinter.Button(ikkuna, text="Lopeta", command=ikkuna.destroy, font=("sans-serif", 10))
    
    alkulabel.pack()
    ohjelabel.pack()
    kenttalabel.pack()
    kysykentankoko.pack()
    miinalabel.pack()
    kysymiinat.pack()
    virheilmoitus.pack()
    aloitusnappi.pack()
    tilastonappi.pack()
    lopetanappi.pack()
    
    ikkuna.mainloop()
    
if __name__ == "__main__":
    main()