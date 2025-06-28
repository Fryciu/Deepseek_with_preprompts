# **Gemini Chat Pro**

**Gemini Chat Pro** to aplikacja desktopowa, która umożliwia prowadzenie rozmów z modelem językowym Google Gemini 2.5. Flash. 

**Zalety:**
1. Funkcja prepromptów, czyli wiadomości które zawsze dodajesz na początku twojego polecenia

**Wady:**
1. LaTeX wyświetla się tak średnio jak mam być szczery.
2. Dla nietechnicznych osób pobranie klucza API może być męczące.
3. Brak kolorowej składni programowania

Jeśli odzew będzie duży (lub jeśli będą mnie te wady bardzo wkurzać) to postaram się dodać te funkcje.

Jak mam być szczery, to tak w połowie robienia tej aplikacji się dowiedziałem że chatGPT ma takie coś, ale go osobiście nie lubię, ze względu na jego przełączenie do wersji 3.5 po kilku promptach, a na dodatek Gemini 2.5. Flash ma 65535 output tokenów, co pozwala na bardzo długie wypowiedzi.

## **Instalacja**

Aby uruchomić aplikację, wystarczy pobrać gotowy plik wykonywalny i rozpakować archiwum.

1. Pobierz aplikację:  
   Pobierz najnowszą wersję aplikacji Gemini Chat Pro ze strony na której jesteś lol.
2. Rozpakuj archiwum:  
   Po pobraniu, rozpakuj zawartość archiwum (.zip lub .rar) do wybranego folderu na swoim komputerze.
3. Uruchom aplikację:  
   W rozpakowanym folderze znajdziesz plik wykonywalny (np. GeminiChatPro.exe na Windowsie lub GeminiChatPro na macOS/Linux). Uruchom go dwukrotnie, aby otworzyć aplikację.  
   _Pamiętaj, że do poprawnego działania funkcji renderowania formuł LaTeX (jeśli będziesz z nich korzystać), musisz mieć zainstalowaną dystrybucję LaTeX (np. TeX Live, MiKTeX) w systemie. Upewnij się, że narzędzia pdflatex i dvipng są dostępne w zmiennej środowiskowej PATH._

## **Użycie**

1. **Zdobądź klucz API**
   - Wejdź na stronę \[https://aistudio.google.com/apikey\]
  
     
   - Naciśnij "Get API key"
     
     ![api1](https://github.com/user-attachments/assets/681cf26f-84b6-4d14-8ee1-fae57b4bba86)
  
   - Naciśnij pierwsze "I consent"
     
     ![api2](https://github.com/user-attachments/assets/7fd6e94b-e954-4221-a7e1-f0970ad8e83c)

   - Naciśnij "Create API key"
     
     ![api3](https://github.com/user-attachments/assets/5479a8e7-94e7-44c8-b0eb-64f805f043c6)

   - Naciśnij "Create API key in new project"
     
     ![api4](https://github.com/user-attachments/assets/d9e140dd-02ce-4c71-af89-2aec9e8d70b5)

   - Skopiuj klucz za pomocą przycisku "copy"
     
     ![api5](https://github.com/user-attachments/assets/a7d950eb-00fe-4746-a48f-fba216860304)

3. **Ustaw Klucz API:**
   - Przy pierwszym uruchomieniu lub jeśli klucz nie jest ustawiony pojawi się
   - Przejdź do menu Ustawienia \-\> Ustaw klucz API. Wprowadź swój klucz API Google Gemini i zatwierdź. Klucz zostanie zapisany lokalnie w pliku api_key.txt obok aplikacji.
4. **Rozpocznij Konwersację:**
   - Domyślnie nowa konwersacja zostanie utworzona po uruchomieniu. Możesz także użyć Plik \-\> Nowa konwersacja.
   - Podaj nazwę dla nowej konwersacji.
5. **Wysyłaj Wiadomości:**
   - Wpisz wiadomość w polu na dole i naciśnij Enter lub przycisk Wyślij.
   - Historia czatu będzie aktualizowana na bieżąco.
6. **Zarządzanie Konwersacjami:**
   - W lewym panelu Konwersacje możesz wybrać inną zapisaną konwersację.
   - Użyj przycisków Nowa, Zmień nazwę i Usuń, aby zarządzać swoimi konwersacjami.
   - Plik \-\> Zapisz konwersację pozwoli Ci ręcznie zapisać aktualny stan konwersacji.
7. **Użycie Prepromptów:**
   - W lewym panelu Preprompty wybierz gotowy preprompt lub stwórz własny.
   - Zarządzaj prepromptami w menu Preprompty otwiera edytor do zaawansowanej edycji i dodawania.

## **Rzeczy które dodam jak się apka spodoba**

- Różne języki, czyli możliwość zmiany języka na angielski
- Kolorowa składnia tekstu programistycznego
- Żeby LaTeX się pobierał wraz z tym chatbotem, żeby było wszystko git (do przetestowania)
- Możliwość zmiany tekstu na grubszy, choć nie obiecuję że latex będzie się wtedy dobrze wyświetlał
- Różne chatboty

## **Konfiguracja**

- **Klucz API:** Klucz API jest przechowywany w pliku api_key.txt w katalogu głównym aplikacji.
- **Konwersacje:** Wszystkie konwersacje są zapisywane w katalogu conversations w postaci plików JSON.

## **Budowanie Aplikacji Wykonywalnej (Executable)**

_(Ta sekcja jest przeznaczona dla deweloperów, którzy chcą zbudować własny plik wykonywalny z kodu źródłowego.)_

Aby stworzyć samodzielną wersję aplikacji, możesz użyć PyInstallera.

1. **Sklonuj repozytorium (jeśli jest dostępne) lub pobierz pliki źródłowe.**
2. **Zalecane: Utwórz wirtualne środowisko** (zalecane dla czystych zależności projektu):  
   python \-m venv venv_chat_app

3. **Aktywuj wirtualne środowisko:**

   - **Windows:**  
     .\\venv_chat_app\\Scripts\\activate

   - **macOS/Linux:**  
     source venv_chat_app/bin/activate

4. **Zainstaluj wymagane biblioteki:**  
   pip install google-generativeai==0.6.0 matplotlib pillow pyinstaller

   _(Wersja google-generativeai może wymagać aktualizacji w zależności od Twojego użycia. Pillow i PyInstaller są potrzebne do budowania.)_

5. Zainstaluj dystrybucję LaTeX:  
   Aplikacja wymaga zainstalowanej dystrybucji LaTeX (np. TeX Live, MiKTeX) w systemie, aby funkcja renderowania LaTeX mogła działać poprawnie. Upewnij się, że pdflatex i dvipng są dostępne w zmiennej PATH.
6. Zbuduj aplikację:  
   Aby stworzyć pojedynczy plik wykonywalny bez otwierania okna konsoli:  
   pyinstaller \--noconsole \--onefile your_main_app_file.py

   Jeśli chcesz zredukować rozmiar pliku, upewnij się, że UPX jest zainstalowany i dostępny w PATH lub użyj \--upx-dir:  
   pyinstaller \--noconsole \--onefile \--upx-dir "C:\\path\\to\\upx" your_main_app_file.py

   Wygenerowany plik wykonywalny znajdziesz w katalogu dist. (Szczerze sam muszę się do tego dostosować)

## **Licencja**

\[Wstaw tutaj informacje o licencji, np. MIT License\]

**Autor:** \[Fryciu\]

**Kontakt:** \[Twój adres e-mail lub profil GitHub\]
