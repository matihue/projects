from colorama import init, Fore, Style                          ######### ZASOBY
from pathlib import Path
from collections import defaultdict 
import os

plik = Path(__file__).parent / "kontakty.txt"                   ######### NAPRAWIENIE ŚCIEŻKI

init(autoreset=True)                                            ######### AUTORESET COLORAMY

kontakty = []                                                   ######### LISTA KONTAKTÓW

if plik.exists():                                               ######### WCZYTYWANIE PLIKU                      
    try:
        with open(plik, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "->" in line:
                    nazwa, numer = line.split("->")
                    kontakty.append({
                        "nazwa": nazwa.strip(),
                        "numer": numer.strip()
                    })
    except Exception as e:
        print(Fore.RED + "Coś poszło nie tak. Błąd: ", e)
        
def czysc_ekran():                                              ######### CZYSZCZENIE EKRANU
    os.system('cls' if os.name == 'nt' else 'clear')            
    
def formatuj_numer(numer):                                      ######### FORMATOWANIE NUMERU
    return f"{numer[0:3]} {numer[3:6]} {numer[6:9]}"

def wyswietl_posortowane_po_literach(kontakty):                 ######### WYPISYWANIE NA EKRAN
    if kontakty:
        grupy = defaultdict(list)
        
        for k in kontakty:
            if k['nazwa']:
                litera = k['nazwa'][0].upper()
            else:
                litera = '#'
            
            grupy[litera].append(k)
        
        for litera in sorted(grupy.keys()):
            print(f"\n {litera}")
            for i, k in enumerate(sorted(grupy[litera], key=lambda x: x['nazwa'].lower()), start=1):
                print(Fore.GREEN + f"{i}. {k['nazwa']} -> {formatuj_numer(k['numer'])}")
                    
    else:
        print(Fore.RED + "\nBrak kontaktów")
    input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
    czysc_ekran()
                    
def zapisz_kontakty_do_pliku():                                 ######### ZAPISYWANIE KONTAKTÓW DO PLIKU
    try:
        with open(plik, "w", encoding="utf-8") as f:
            for k in kontakty:
                f.write(f"{k['nazwa']} -> {k['numer']}\n")
    except Exception as e:
        print(Fore.RED + "Coś poszło nie tak. Błąd: ", e)

def dodaj_kontakt(kontakty):                                    ######### DODAWANIE KONTAKTU
    

    while True:
        nazwa = input("Podaj nazwę kontaktu: ")
        
        if not nazwa:
            print(Fore.RED + "Nazwa nie może być pusta.")
            continue
        if any(k['nazwa'] == nazwa for k in kontakty):
            print(Fore.RED + "Taki kontakt już istnieje. Wpisz inną nazwę.")
            continue
            
        break

    while True:
        numer = input("Podaj numer: ")

        if not numer.isdigit():
            print(Fore.RED + "Numer ma zawierać tylko cyfry.")
            continue
    
        if len(numer) < 9:
            print(Fore.RED + "Ten numer jest zbyt krótki, podaj 9 cyfr.")
            continue
        
        if any(k['numer'] == numer for k in kontakty):
            print(Fore.RED + "Taki numer już istnieje. Wpisz inny numer.")
            continue

        break 

    kontakt = {
        "nazwa": nazwa,
        "numer": numer
    }
    
    kontakty.append(kontakt)
    
    try:
        with open(plik, "a", encoding="utf-8") as f:
            f.write(f"{kontakt['nazwa']} -> {kontakt['numer']}\n")
        print("\nKontakt zapisany.")
        input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
        czysc_ekran()
    except Exception as e:
        print(Fore.RED + "Coś poszło nie tak. Błąd: ", e)
    
def usun_kontakt(kontakty):                                     ######### USUWANIE KONTAKTU
    ktory = input("Który kontakt chcesz usunąć?: ")
    for k in kontakty:
        if k['nazwa'] == ktory:
            kontakty.remove(k)
            zapisz_kontakty_do_pliku()
            print(f"\n{ktory} został usunięty")
            input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
            czysc_ekran()
            return
    print(Fore.RED + "\nNie ma takiego kontaktu")
    input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
    czysc_ekran()
            
def edytuj_kontakt(kontakty):                                   ######### EDYTOWANIE KONTAKTU
    ktory = input("Który kontakt chcesz edytować?: ")
    for k in kontakty:
        if k['nazwa'] == ktory:
            co = input("Co chcesz edytować? (nazwa/numer): ")
            
            if co == "nazwa":
                while True:
                    nowa_nazwa = input("Na jaką nazwę chcesz zmienić?: ")
                    if not nowa_nazwa:
                        print(Fore.RED + "Nazwa nie może być pusta.")
                        continue
                    if any(k['nazwa'] == nowa_nazwa for k in kontakty):
                        print(Fore.RED + "Taki kontakt już istnieje. Wpisz inną nazwę.")
                        continue
                    break
                k['nazwa'] = nowa_nazwa   
            
            elif co == "numer":
                while True:
                    nowy_numer = input("Na jaki numer chcesz zmienić?: ")

                    if not nowy_numer.isdigit():
                        print(Fore.RED + "Numer ma zawierać tylko cyfry.")
                        continue

                    if len(nowy_numer) != 9:
                        print(Fore.RED + "Numer musi mieć dokładnie 9 cyfr.")
                        continue

                    if any(x['numer'] == nowy_numer and x is not k for x in kontakty):
                        print(Fore.RED + "Taki numer już istnieje.")
                        continue

                    break
                k['numer'] = nowy_numer

            zapisz_kontakty_do_pliku()
            print(f"\n{ktory} został zaktualizowany")
            input(Fore.BLUE +"\nNaciśnij enter, aby kontynuować...")
            czysc_ekran()
            return
    print(Fore.RED + "\nNie ma takiego kontaktu")
    input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
    czysc_ekran()
    
def wyszukaj_kontakt(kontakty):                                 ######### WYSZUKIWANIE KONTAKTU
    szukaj = input("\nWpisz fragment nazwy lub numeru do wyszukania: ")
    wyniki = []
    for x in kontakty:
        if szukaj.lower() in x['nazwa'].lower() or szukaj in x['numer']:
            wyniki.append(x)
 
    if wyniki:
        for i, k in enumerate(wyniki, start=1):
            print(f"{i}. {k['nazwa']} -> {k['numer']}")

    else:
        print(Fore.RED + "\nNie znaleziono kontaktu")
    input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
    czysc_ekran()
        
while True:                                                     ######### GŁÓWNA PĘTLA PROGRAMU
    print(Fore.YELLOW + Style.BRIGHT +"\n Wybierz działanie: ")
    print(Fore.YELLOW + Style.BRIGHT +"1. Wyświetl kontakty")
    print(Fore.YELLOW + Style.BRIGHT +"2. Dodaj kontakt")
    print(Fore.YELLOW + Style.BRIGHT +"3. Edytuj kontakt")
    print(Fore.YELLOW + Style.BRIGHT +"4. Usuń kontakt")
    print(Fore.YELLOW + Style.BRIGHT +"5. Wyszukiwarka kontaktów")
    print(Fore.YELLOW + Style.BRIGHT +"6. Zakończ")
    
    try:
        wybor = int(input("\nTwój wybór: "))
        print()
    
        if wybor == 1:
            wyswietl_posortowane_po_literach(kontakty)
                   
        elif wybor == 2:
            dodaj_kontakt(kontakty)
        
        elif wybor == 3:
            edytuj_kontakt(kontakty)
            
        elif wybor == 4:
            usun_kontakt(kontakty)
            
        elif wybor == 5:
            wyszukaj_kontakt(kontakty)
        
        elif wybor == 6:
            print("Zamykanie... ")
            break
        
        else:
            print(Fore.RED + "\nNieprawidłowy wybór")
            
    except ValueError:
        print(Fore.RED + "\nWybierz liczbę!")
        input(Fore.BLUE + "\nNaciśnij enter, aby kontynuować...")
        czysc_ekran()