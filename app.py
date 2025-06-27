import os
import json
import tkinter as tk
from tkinter import (
    ttk, scrolledtext, messagebox, 
    filedialog, simpledialog
)
from datetime import datetime
from threading import Thread
import google.generativeai as genai
import matplotlib.pyplot as plt
import re
import io
from PIL import Image, ImageTk # Import Pillow for image handling
from pathlib import Path

class GeminiChatApp:
    def __init__(self, root):
        # Konfiguracja głównego okna
        self.root = root
        self.root.title("Gemini Chat Pro")
        self.root.geometry("1000x700")
        
        # Inicjalizacja ścieżek konfiguracyjnych
        self.init_paths()
        
        # Konfiguracja Gemini API
        self.init_gemini()
        
        # Inicjalizacja interfejsu
        self.setup_ui()
        
        # Zmienne stanu
        self.conversation_history = []
        self.current_conversation_id = None
        self.rendered_images = [] # Store references to PhotoImage objects
        self.app_data_dir = Path(__file__).parent
        
    def init_paths(self):
        """Inicjalizuje ścieżki do plików konfiguracyjnych"""
        self.app_data_dir = Path(__file__).parent
        print(self.app_data_dir)
        os.makedirs(self.app_data_dir, exist_ok=True)
    
        self.preprompts_file = os.path.join(
            self.app_data_dir, 
            "preprompts.json"
        )
        self.conversations_dir = os.path.join(
            self.app_data_dir, 
            "conversations"
        )
        os.makedirs(self.conversations_dir, exist_ok=True)
        self.api_key_file = os.path.join(self.app_data_dir, "api_key.txt") # Dodaj tę linię
            
        

    def init_gemini(self):
        """Konfiguruje połączenie z Gemini API"""
        try:
            # W rzeczywistej aplikacji klucz powinien być ładowany
            # z zmiennych środowiskowych lub pliku konfiguracyjnego
            # IMPORTANT: Replace with your actual API key or load from env var
            try:
                with open(self.api_key_file, "r") as f:
                    api_key = f.read().strip()
            except FileNotFoundError:
                full_path = os.path.join(self.app_data_dir, "api_key.txt")
                api_key = simpledialog.askstring(
                    "Zapisz klucz API",
                    "Podaj klucz API:"
                )
                f = open(full_path, "a")
                f.write(api_key)
            genai.configure(api_key=api_key) 
            self.model = genai.GenerativeModel("gemini-2.5-flash") # Updated model to 1.5-flash
        except Exception as e:
            messagebox.showerror(
                "Błąd inicjalizacji", 
                f"Nie można połączyć z Gemini API:\n{str(e)}"
            )
            raise

    def setup_ui(self):
        """Konfiguruje cały interfejs użytkownika"""
        self.setup_menu()
        self.setup_main_frames()
        self.setup_config_panel()
        self.setup_chat_panel()
        self.setup_status_bar()
        
        # Ładowanie danych
        self.load_preprompts()
        self.load_conversation_list()

    def setup_menu(self):
        """Konfiguruje menu główne"""
        menubar = tk.Menu(self.root)
        
        # Menu Plik
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(
            label="Nowa konwersacja", 
            command=self.new_conversation,
            accelerator="Ctrl+N"
        )
        file_menu.add_command(
            label="Zapisz konwersację", 
            command=self.save_conversation,
            accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="Eksportuj jako...", 
            command=self.export_conversation
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Zakończ", 
            command=self.confirm_exit
        )
        menubar.add_cascade(label="Plik", menu=file_menu)
        
        # Menu Preprompty
        preprompts_menu = tk.Menu(menubar, tearoff=0)
        preprompts_menu.add_command(
            label="Zapisz obecny preprompt", 
            command=self.save_current_preprompt
        )
        preprompts_menu.add_command(
            label="Zarządzaj prepromptami", 
            command=self.show_preprompts_manager
        )
        menubar.add_cascade(label="Preprompty", menu=preprompts_menu)
        
        # Menu Pomoc
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="O programie", 
            command=self.show_about
        )
        menubar.add_cascade(label="Pomoc", menu=help_menu)
        
        # Menu Edycja
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(
            label="Zmień klucz API", 
            command=self.zmien_api_key
        )
        menubar.add_cascade(label="Edycja", menu=edit_menu)
        
        
        self.root.config(menu=menubar)
        
        # Skróty klawiaturowe
        self.root.bind("<Control-n>", lambda e: self.new_conversation())
        self.root.bind("<Control-s>", lambda e: self.save_conversation())


    def zmien_api_key(self):
        api_key = simpledialog.askstring(
            "Zapisz klucz API",
            "Podaj klucz API:"
        )
        with open(self.api_key_file, "w") as f:
            f.write(api_key)
        messagebox.showinfo(
            "Sukces",
            "Klucz API został zapisany."
        )
        self.init_gemini()
    
    def show_about(self):
        messagebox.showinfo(
            "O programie",
            "Gemini Chat Pro v1.0\n\nAutor: Fryderyk Sadłocha \n\nWersja: 1.0 \n\nOprogramowanie " + 
            "jest darmowe i dostępne na GitHubie. Wszelkie prawa autorskie zastrzeżone.")
    
    
    def setup_main_frames(self):
        """Konfiguruje główne obszary interfejsu"""
        # Główny kontener
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lewy panel (konfiguracja)
        self.left_panel = ttk.Frame(self.main_frame, width=250)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # Prawy panel (czat)
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_config_panel(self):
        """Konfiguruje lewy panel ustawień"""
        # Notatnik konwersacji
        conv_frame = ttk.LabelFrame(
            self.left_panel, 
            text="Konwersacje",
            padding=10
        )
        conv_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.conversation_listbox = tk.Listbox(
            conv_frame,
            height=10,
            selectmode=tk.SINGLE
        )
        self.conversation_listbox.pack(fill=tk.X)
        self.conversation_listbox.bind(
            "<<ListboxSelect>>", 
            self.on_conversation_select
        )
        
        ttk.Button(
            conv_frame,
            text="Załaduj",
            command=self.load_selected_conversation
        ).pack(side=tk.LEFT)
        ttk.Button(
            conv_frame,
            text="Usuń",
            command=self.delete_selected_conversation
        ).pack(side=tk.RIGHT)
        
        # Zarządzanie prepromptami
        preprompt_frame = ttk.LabelFrame(
            self.left_panel, 
            text="Preprompty",
            padding=10
        )
        preprompt_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preprompt_listbox = tk.Listbox(
            preprompt_frame,
            height=10
        )
        self.preprompt_listbox.pack(fill=tk.BOTH, expand=True)
        self.preprompt_listbox.bind(
            "<<ListboxSelect>>", 
            self.on_preprompt_select
        )
        
        btn_frame = ttk.Frame(preprompt_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="Zastosuj",
            command=self.apply_selected_preprompt
        ).pack(side=tk.LEFT, expand=True)
        ttk.Button(
            btn_frame,
            text="Usuń",
            command=self.delete_selected_preprompt
        ).pack(side=tk.LEFT, expand=True)

    def setup_chat_panel(self):
        """Konfiguruje prawy panel czatu"""
        # Górny panel - konfiguracja
        config_frame = ttk.Frame(self.right_panel)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            config_frame,
            text="Prompt systemowy:"
        ).pack(side=tk.LEFT)
        
        self.system_prompt = ttk.Entry(
            config_frame,
            width=50
        )
        self.system_prompt.pack(
            side=tk.LEFT, 
            fill=tk.X, 
            expand=True, 
            padx=5
        )
        self.system_prompt.insert(
            0, 
            "Jesteś pomocnym asystentem. Odpowiadaj w języku polskim."
        )
        
        # Główny obszar czatu
        self.chat_display = scrolledtext.ScrolledText(
            self.right_panel,
            wrap=tk.WORD,
            font=('Arial', 11), # Changed to non-bold for general text
            state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Konfiguracja stylów wiadomości
        self.chat_display.tag_config(
            'user_prefix', # Tag for "Ty: "
            foreground='#0066cc',
            font=('Arial', 11, 'bold')
        )
        self.chat_display.tag_config(
            'user_text', # Tag for user's actual message
            foreground='black', # Default text color
            font=('Arial', 11)
        )
        self.chat_display.tag_config(
            'bot_prefix', # Tag for "AI: "
            foreground='#009933',
            font=('Arial', 11, 'bold')
        )
        self.chat_display.tag_config(
            'bot_text', # Tag for bot's actual message
            foreground='black', # Default text color
            font=('Arial', 11)
        )
        self.chat_display.tag_config(
            'error', 
            foreground='#cc0000',
            font=('Arial', 11)
        )
        
        # Dolny panel - wprowadzanie wiadomości
        input_frame = ttk.Frame(self.right_panel)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.user_input = ttk.Entry(
            input_frame,
            font=('Arial', 11)
        )
        self.user_input.pack(
            side=tk.LEFT, 
            fill=tk.X, 
            expand=True, 
            padx=(0, 5)
        )
        self.user_input.bind(
            "<Return>", 
            lambda e: self.send_message()
        )
        
        ttk.Button(
            input_frame,
            text="Wyślij",
            command=self.send_message
        ).pack(side=tk.RIGHT)

    def setup_status_bar(self):
        """Konfiguruje pasek statusu"""
        self.status_var = tk.StringVar()
        self.status_var.set("Gotowy")
        
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X)

    # === Metody zarządzania prepromptami ===
    def load_preprompts(self):
        """Wczytuje preprompty z pliku"""
        self.preprompts = {}
        try:
            if os.path.exists(self.preprompts_file):
                with open(self.preprompts_file, 'r', encoding='utf-8') as f:
                    self.preprompts = json.load(f)
        except Exception as e:
            messagebox.showwarning(
                "Ostrzeżenie",
                f"Nie można wczytać prepromptów:\n{str(e)}"
            )
        
        # Aktualizacja listy
        self.preprompt_listbox.delete(0, tk.END)
        for name in sorted(self.preprompts.keys()):
            self.preprompt_listbox.insert(tk.END, name)

    def save_preprompts(self):
        """Zapisuje preprompty do pliku"""
        try:
            with open(self.preprompts_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.preprompts, 
                    f, 
                    indent=2, 
                    ensure_ascii=False
                )
            return True
        except Exception as e:
            messagebox.showerror(
                "Błąd",
                f"Nie można zapisać prepromptów:\n{str(e)}"
            )
            return False

    def save_current_preprompt(self):
        """Zapisuje bieżący prompt jako nowy preprompt"""
        current_prompt = self.system_prompt.get().strip()
        if not current_prompt:
            messagebox.showwarning(
                "Puste pole",
                "Prompt systemowy jest pusty!"
            )
            return
            
        name = simpledialog.askstring(
            "Zapisz preprompt",
            "Podaj nazwę dla tego prepromptu:"
        )
        
        if name:
            if name in self.preprompts:
                if not messagebox.askyesno(
                    "Potwierdzenie",
                    f"Preprompt '{name}' już istnieje. Nadpisać?"
                ):
                    return
                    
            self.preprompts[name] = current_prompt
            if self.save_preprompts():
                self.load_preprompts()
                messagebox.showinfo(
                    "Sukces",
                    f"Zapisano preprompt '{name}'"
                )

    def on_preprompt_select(self, event):
        """Obsługuje wybór prepromptu z listy"""
        selection = self.preprompt_listbox.curselection()
        if selection:
            selected_name = self.preprompt_listbox.get(selection[0])
            selected_prompt = self.preprompts.get(selected_name, "")
            self.system_prompt.delete(0, tk.END)
            self.system_prompt.insert(0, selected_prompt)

    def apply_selected_preprompt(self):
        """Stosuje wybrany preprompt"""
        selection = self.preprompt_listbox.curselection()
        if selection:
            self.on_preprompt_select(None)

    def delete_selected_preprompt(self):
        """Usuwa wybrany preprompt"""
        selection = self.preprompt_listbox.curselection()
        if not selection:
            return
            
        selected_name = self.preprompt_listbox.get(selection[0])
        if messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz usunąć preprompt '{selected_name}'?"
        ):
            del self.preprompts[selected_name]
            if self.save_preprompts():
                self.load_preprompts()

    def show_preprompts_manager(self):
        """Pokazuje zaawansowane okno zarządzania prepromptami"""
        manager = tk.Toplevel(self.root)
        manager.title("Zarządzanie prepromptami")
        manager.geometry("600x400")
        
        # Edytor tekstu
        editor = scrolledtext.ScrolledText(
            manager,
            wrap=tk.WORD,
            font=('Arial', 11)
        )
        editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Wczytanie aktualnego promptu
        editor.insert(tk.END, self.system_prompt.get())
        
        # Przyciski akcji
        btn_frame = ttk.Frame(manager)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Zapisz jako nowy",
            command=lambda: self.save_from_editor(
                editor,
                manager,
                new=True
            )
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="Aktualizuj obecny",
            command=lambda: self.save_from_editor(
                editor,
                manager,
                new=False
            )
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="Anuluj",
            command=manager.destroy
        ).pack(side=tk.RIGHT)

    def save_from_editor(self, editor, window, new=False):
        """Zapisuje prompt z edytora"""
        content = editor.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning(
                "Puste pole",
                "Prompt systemowy jest pusty!"
            )
            return
            
        if new:
            self.save_custom_preprompt(content, window)
        else:
            self.update_current_preprompt(content, window)

    def update_current_preprompt(self, content, window):
        """Aktualizuje obecny preprompt"""
        selection = self.preprompt_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Brak wyboru",
                "Nie wybrano prepromptu do aktualizacji!"
            )
            return
            
        selected_name = self.preprompt_listbox.get(selection[0])
        self.preprompts[selected_name] = content
        if self.save_preprompts():
            self.load_preprompts()
            window.destroy()
            messagebox.showinfo(
                "Sukces",
                f"Zaktualizowano preprompt '{selected_name}'"
            )

    # === Metody zarządzania konwersacjami ===
    def load_conversation_list(self):
        """Wczytuje listę zapisanych konwersacji"""
        self.conversation_list = []
        try:
            for filename in os.listdir(self.conversations_dir):
                if filename.endswith('.json'):
                    self.conversation_list.append(
                        os.path.splitext(filename)[0]
                    )
        except Exception as e:
            messagebox.showwarning(
                "Ostrzeżenie",
                f"Nie można wczytać listy konwersacji:\n{str(e)}"
            )
        
        # Aktualizacja listy
        self.conversation_listbox.delete(0, tk.END)
        for conv in sorted(self.conversation_list, reverse=True):
            self.conversation_listbox.insert(tk.END, conv)

    def new_conversation(self):
        """Rozpoczyna nową konwersację"""
        if (self.conversation_history and 
            not messagebox.askyesno(
                "Potwierdzenie",
                "Czy na pewno chcesz rozpocząć nową konwersację?\nNie zapisane dane zostaną utracone."
            )):
            return
            
        self.conversation_history = []
        self.current_conversation_id = None
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state='disabled')
        self.status_var.set("Nowa konwersacja - niezapisana")
        # Clear image references for new conversation
        self.rendered_images = [] 

    def save_custom_preprompt(self, content, window):
        """Zapisuje nowy preprompt z edytora"""
        name = simpledialog.askstring(
            "Zapisz preprompt",
            "Podaj nazwę dla tego prepromptu:",
            parent=window
        )
        
        if name:
            self.preprompts[name] = content
            if self.save_preprompts():
                self.load_preprompts()
                window.destroy()
                messagebox.showinfo(
                    "Sukces",
                    f"Zapisano preprompt '{name}'"
                )

    def save_conversation(self):
        """Zapisuje aktualną konwersację"""
        if not self.conversation_history:
            messagebox.showwarning(
                "Pusta konwersacja",
                "Nie ma nic do zapisania!"
            )
            return
        
        name = simpledialog.askstring(
            "Zapisz konwersację",
            "Podaj nazwę dla tej konwersacji:",
            
        )
            
        if self.current_conversation_id:
            filename = f"{self.current_conversation_id}.json"
        elif name:  
            filename = f"{name}.json"
            messagebox.showinfo(
                    "Sukces",
                    f"Zapisano preprompt '{name}'"
                )
        else:
            filename = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        filepath = os.path.join(self.conversations_dir, filename)
        
        try:
            data = {
                "system_prompt": self.system_prompt.get(),
                "history": self.conversation_history,
                "created_at": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.current_conversation_id = os.path.splitext(filename)[0]
            self.load_conversation_list()
            self.status_var.set(f"Konwersacja zapisana: {self.current_conversation_id}")
            return True
            
        except Exception as e:
            messagebox.showerror(
                "Błąd",
                f"Nie można zapisać konwersacji:\n{str(e)}"
            )
            return False

    def load_selected_conversation(self):
        """Wczytuje wybraną konwersację z listy"""
        selection = self.conversation_listbox.curselection()
        if not selection:
            return
            
        conv_name = self.conversation_listbox.get(selection[0])
        filepath = os.path.join(
            self.conversations_dir, 
            f"{conv_name}.json"
        )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Potwierdzenie przed nadpisaniem
            if (self.conversation_history and 
                not messagebox.askyesno(
                    "Potwierdzenie",
                    "Czy na pewno chcesz wczytać tę konwersację?\nNie zapisane dane zostaną utracone."
                )):
                return
                
            # Wczytanie danych
            self.system_prompt.delete(0, tk.END)
            self.system_prompt.insert(0, data.get("system_prompt", ""))
            
            self.conversation_history = data.get("history", [])
            self.current_conversation_id = conv_name
            
            # Wyświetlenie historii
            self.chat_display.config(state='normal')
            self.chat_display.delete('1.0', tk.END)
            self.rendered_images = [] # Clear old image references
            
            for role, msg in self.conversation_history:
                # Use display_message to handle potential LaTeX in loaded history
                self.display_message(role, msg, is_new_entry=False) 
                
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)
            
            self.status_var.set(f"Wczytano konwersację: {conv_name}")
            
        except Exception as e:
            messagebox.showerror(
                "Błąd",
                f"Nie można wczytać konwersacji:\n{str(e)}"
            )

    def on_conversation_select(self, event):
        """Obsługuje wybór konwersacji z listy"""
        selection = self.conversation_listbox.curselection()
        if selection:
            conv_name = self.conversation_listbox.get(selection[0])
            self.status_var.set(f"Wybrano: {conv_name}")

    def delete_selected_conversation(self):
        """Usuwa wybraną konwersację"""
        selection = self.conversation_listbox.curselection()
        if not selection:
            return
            
        conv_name = self.conversation_listbox.get(selection[0])
        
        if messagebox.askyesno(
            "Potwierdzenie",
            f"Czy na pewno chcesz usunąć konwersację '{conv_name}'?"
        ):
            filepath = os.path.join(
                self.conversations_dir, 
                f"{conv_name}.json"
            )
            
            try:
                os.remove(filepath)
                self.load_conversation_list()
                messagebox.showinfo(
                    "Sukces",
                    f"Usunięto konwersację '{conv_name}'"
                )
            except Exception as e:
                messagebox.showerror(
                    "Błąd",
                    f"Nie można usunąć konwersacji:\n{str(e)}"
                )

    def export_conversation(self):
        """Eksportuje konwersację do pliku tekstowego"""
        if not self.conversation_history:
            messagebox.showwarning(
                "Pusta konwersacja",
                "Nie ma nic do eksportowania!"
            )
            return
            
        default_name = (
            self.current_conversation_id 
            or f"konwersacja_{datetime.now().strftime('%Y%m%d_%H%M')}"
        )
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Plik tekstowy", "*.txt"),
                ("Plik Markdown", "*.md"),
                ("Wszystkie pliki", "*.*")
            ],
            initialfile=default_name
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Nagłówek
                    f.write(f"=== Konwersacja Gemini Chat ===\n")
                    f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"Prompt systemowy: {self.system_prompt.get()}\n\n")
                    
                    # Historia
                    for role, msg in self.conversation_history:
                        prefix = "UŻYTKOWNIK: " if role == "user" else "ASYSTENT: "
                        f.write(f"{prefix}{msg}\n\n")
                
                messagebox.showinfo(
                    "Sukces",
                    f"Konwersacja zapisana do:\n{filepath}"
                )
                return True
                
            except Exception as e:
                messagebox.showerror(
                    "Błąd",
                    f"Nie można zapisać pliku:\n{str(e)}"
                )
                return False

    # === Metody obsługi czatu ===
    def send_message(self):
        """Wysyła wiadomość do Gemini API"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        
        # Display user message first without preprompt in display
        self.display_message('user', user_text, is_new_entry=True) 
        self.user_input.delete(0, tk.END)
        
        # Combine preprompt and user message for the API call
        full_message_for_api = self.system_prompt.get().strip() + " " + user_text 
        
        # Uruchomienie zapytania w tle
        Thread(
            target=self.process_ai_response,
            args=(full_message_for_api,),
            daemon=True
        ).start()

    def process_ai_response(self, message):
        self.status_var.set("Łączenie z Gemini API...")
        
        try:
            response = self.model.generate_content(
                contents=message,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 2048 # A more reasonable default for text generation
                },
                safety_settings={
                    "HARASSMENT": "BLOCK_NONE",
                    "HATE_SPEECH": "BLOCK_NONE",
                    "SEXUAL": "BLOCK_NONE",
                    "DANGEROUS": "BLOCK_NONE"
                }
            )
            
            # Rozszerzona walidacja odpowiedzi
            if not response.candidates:
                raise ValueError("Brak odpowiedzi od modelu (pusta odpowiedź)")
                
            # Check for block_reason in Candidates[0].safety_ratings (more reliable)
            if hasattr(response.candidates[0], 'safety_ratings') and any(rating.blocked for rating in response.candidates[0].safety_ratings):
                 bot_reply = "[ODPOWIEDŹ ZABLOKOWANA - filtr bezpieczeństwa Gemini]"
            elif not response.parts: # Check if there are any content parts
                bot_reply = "[Brak treści w odpowiedzi pomimo braku blokady bezpieczeństwa]"
            else:
                bot_reply = response.text # Assuming text is the main part
            
            # Check finish reason, if applicable
            finish_reason = getattr(response.candidates[0], 'finish_reason', None)
            if finish_reason == "MAX_TOKENS":
                bot_reply += "\n\n[UWAGA: Odpowiedź została obcięta - osiągnięto limit tokenów]"
            elif finish_reason and finish_reason not in ["STOP", "RECITATION"]: # STOP and RECITATION are normal
                bot_reply += f"\n\n[UWAGA: Niekompletna odpowiedź - powód: {finish_reason}]"

            # Aktualizacja historii i UI
            self.conversation_history.append(("user", message)) # Store the full message sent to API
            self.conversation_history.append(("bot", bot_reply))
            
            self.display_message('bot', bot_reply, is_new_entry=True)
            self.status_var.set("Odpowiedź otrzymana")
        
        except Exception as e:
            error_msg = f"Błąd API: {str(e)}"
            self.display_message('error', error_msg, is_new_entry=True)
            self.status_var.set(error_msg)
            # Only append error to history if it's a new error from the bot
            # not if it's part of a loaded conversation.
            self.conversation_history.append(("error", error_msg))

    def display_message(self, sender, text, is_new_entry=True):
        """
        Wyświetla wiadomość z obsługą LaTeX.
        is_new_entry: True jeśli wiadomość jest nowa (z czatu), False jeśli ładowana z historii.
        """
        self.chat_display.config(state='normal')

        # Add sender prefix and tag
        if sender == 'user':
            self.chat_display.insert(tk.END, "Ty: ", 'user_prefix')
            message_tag = 'user_text'
        elif sender == 'bot':
            self.chat_display.insert(tk.END, "AI: ", 'bot_prefix')
            message_tag = 'bot_text'
        elif sender == 'error':
            self.chat_display.insert(tk.END, "BŁĄD: ", 'error')
            message_tag = 'error'
        else: # Fallback
            self.chat_display.insert(tk.END, f"{sender.capitalize()}: ", 'bot_prefix')
            message_tag = 'bot_text'

        # Regex to split by LaTeX delimiters ($...$ for inline, $$...$$ for block)
        # It keeps the delimiters in the result
        parts = re.split(r'(\$\$[^$]+\$\$|\$[^$]+\$)', text)

        for part in parts:
            if part.startswith('$$') and part.endswith('$$'):
                # Block LaTeX formula
                latex_content = part[2:-2].strip()
                self.insert_latex_image(latex_content, block_mode=True)
                
            elif part.startswith('$') and part.endswith('$'):
                # Inline LaTeX formula
                latex_content = part[1:-1].strip()
                self.insert_latex_image(latex_content, block_mode=False)
            else:
                # Regular text
                self.chat_display.insert(tk.END, part, message_tag)

        self.chat_display.insert(tk.END, '\n\n') # Add spacing after each message
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def insert_latex_image(self, latex_string, block_mode=False):
        """Renders a LaTeX string to a PIL Image and inserts it into the Text widget."""
        fig = None # Inicjalizacja fig na None na wypadek błędu przed utworzeniem
        try:
            # Create a new figure for rendering
            # Adjust figsize and dpi based on desired output size and clarity
            # Block mode might need larger figure/fontsize
            if block_mode:
                fig_width = 8 # inches
                # Lepsza heurystyka dla wysokości w block_mode może być potrzebna,
                # ale na razie zostawiamy Twoją logikę.
                fig_height = 0.5 + (latex_string.count('\\\\') * 0.3) # Adjust height for multiline equations
                font_size = 18
            else:
                # Dynamiczna szerokość dla inline, może wymagać dalszych testów
                fig_width = 0.8 + (len(latex_string) * 0.08)
                fig_height = 0.3 # Height for inline
                font_size = 14

            # Zwiększone DPI dla lepszej jakości, ale może zwiększyć rozmiar obrazka
            fig = plt.figure(figsize=(fig_width, fig_height), dpi=150) # Zwiększono DPI do 150
            
            # Use fig.add_subplot to get an Axes object for text placement
            ax = fig.add_subplot(111)
            ax.set_axis_off() # Hide axes

            # Render LaTeX text
            # Upewnij się, że string jest poprawnie otoczony $ dla trybu matematycznego
            # matplotlib oczekuje LaTeX-a w formacie matematycznym, np. $...$ lub $$...$$
            # Jeśli latex_string już zawiera $ (np. z wejścia użytkownika), może to być problematyczne.
            # Zakładam, że latex_string to surowy kod LaTeX-a, który ma być osadzony w trybie matematycznym.
            ax.text(0.5, 0.5, f"${latex_string}$", # Re-add $ for matplotlib's LaTeX processing
                            horizontalalignment='center',
                            verticalalignment='center',
                            fontsize=font_size,
                            color='black',
                            usetex=True) # Crucial for LaTeX rendering

            # Usunięcie zbędnych białych marginesów
            # plt.savefig z bbox_inches='tight' jest zazwyczaj wystarczające.
            # fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
            
            # Save to an in-memory buffer
            buf = io.BytesIO()
            # Użyj facecolor='none' dla przezroczystości (jeśli to możliwe w zależności od backendu)
            # bbox_inches='tight' i pad_inches=0.01 kontrolują marginesy wokół renderowanego obrazu.
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.01, transparent=True)
            buf.seek(0) # Rewind the buffer to the beginning
            
            # Convert buffer to PhotoImage
            pil_image = Image.open(buf)
            tk_image = ImageTk.PhotoImage(pil_image)
            self.rendered_images.append(tk_image) # Keep a reference to prevent garbage collection

            # Insert image into Text widget
            if block_mode:
                self.chat_display.insert(tk.END, '\n') # New line before block equation
                self.chat_display.image_create(tk.END, image=tk_image)
                self.chat_display.insert(tk.END, '\n') # New line after block equation
            else:
                self.chat_display.image_create(tk.END, image=tk_image)

        except Exception as e:
            print(f"Error rendering LaTeX: {e}")
            self.chat_display.insert(tk.END, f"[BŁĄD LaTeX: {latex_string}]", 'error')
        finally:
            # ZAWSZE zamykaj figurę, aby zwolnić zasoby
            if fig is not None:
                plt.close(fig)
    
    # === Metody pomocnicze ===
    def confirm_exit(self):
        """Potwierdza zamknięcie aplikacji"""
        if (self.conversation_history and 
            not messagebox.askyesno(
                "Potwierdzenie",
                "Czy na pewno chcesz wyjść?\nNie zapisane dane zostaną utracone."
            )):
            return
            
        self.root.destroy()

if __name__ == "__main__":
    # Configure Matplotlib for LaTeX rendering (requires a LaTeX distribution like TeX Live/MiKTeX)
    # This block should be uncommented if you have a LaTeX distribution installed.
    try:
        plt.rcParams['text.usetex'] = True
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = 'Computer Modern Roman' # Or 'Latin Modern Roman'
    except Exception as e:
        print(f"Warning: LaTeX configuration for Matplotlib failed. Ensure you have a LaTeX distribution (e.g., MiKTeX, TeX Live) installed and properly configured in your PATH. Math will be rendered as plain text or cause errors: {e}")
        # Optionally, you might want to show a messagebox or disable LaTeX rendering if it fails.
        # For now, we'll let it try and fail gracefully within display_message.

    root = tk.Tk()
    try:
        app = GeminiChatApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror(
            "Błąd krytyczny",
            f"Aplikacja nie może zostać uruchomiona:\n{str(e)}"
        )