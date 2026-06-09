import json
from pathlib import Path
from datetime import date, datetime
import tkinter as tk
import customtkinter as ctk
import threading
import random
import re

root = ctk.CTk()
root.title('Bank')
root.geometry("500x700+650+130")

now = datetime.now().strftime("%d/%m/%Y %H:%M")
today = date.today().strftime("%d/%m/%Y")

path = Path(__file__).parent
FILE = path / "data.json"

current_user = None
current_login = None

if FILE.exists() and FILE.stat().st_size > 0:
    with open(FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {}
    

def clear_window():
    for widget in root.winfo_children():
        try:
            widget.destroy()
        except:
            pass

        
def valid_birth_date(date_of_birth_str):
    
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", date_of_birth_str):
        return False
    try:
        datetime.strptime(date_of_birth_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False
        
        
def transfer():
    clear_window()
    
    ctk.CTkLabel(root, text="Numer konta odbiorcy: ").pack()
    recipient_number_entry = ctk.CTkEntry(root)
    recipient_number_entry.pack()
    
    ctk.CTkLabel(root, text="Kwota: ").pack()
    amount_entry = ctk.CTkEntry(root)
    amount_entry.pack()
    
    ctk.CTkButton(root, text="\u2B8C",width=7, height=7, command=main).place(x=10, y=10)

    def make_transfer():
        
        recipient_number = recipient_number_entry.get()
        amount = int(amount_entry.get())
        
        recipient = None
        for user in data.values():
            if str(user['number']) == recipient_number:
                recipient = user
                break
            
        if recipient is None:
            ctk.CTkLabel(root, text="Nie ma takiego odbiorcy").pack()
            return       

        elif current_user["balance"] < amount:
            ctk.CTkLabel(root, text="Niewystarczające środki!").pack()
            return
        
        elif recipient['number'] == current_user['number']:
            ctk.CTkLabel(root, text="Nie możesz wysłać przelewu samemu sobie").pack()
            return
        
        else:
            
            transfer_history = {
                'date': now,
                'sender': current_user['name'] + " " + current_user['surname'] ,
                'recipient': recipient['name'] + " " + recipient['surname'] ,
                'sender_number': current_user['number'],
                'recipient_number': recipient['number'],
                'amount': amount,
                'outgoing': True,
                'incoming': False  
            }
            
            current_user["history"].append(transfer_history)
            current_user["balance"] -= amount
            
            data[current_login]["balance"] = current_user["balance"]
            data[current_login]["history"] = current_user["history"]
            
            transfer_history_recipient = transfer_history.copy()
            transfer_history_recipient['outgoing'] = False
            transfer_history_recipient['incoming'] = True
            
            recipient["history"].append(transfer_history_recipient)
            recipient["balance"] += amount


        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        ctk.CTkLabel(root, text="Przelew wykonany pomyślnie").pack()
    
    ctk.CTkButton(root, text="Wykonaj przelew", command=make_transfer).pack(pady=15)
 
 
def history():
    clear_window()
    
    frame = ctk.CTkScrollableFrame(
        root,
        width=500,
        height=400
    )
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    ctk.CTkLabel(frame, text="HISTORIA PRZELEWÓW")
    
    if current_user['history']:
            for i, val in enumerate(reversed(current_user['history']), start=1):
                btn = ctk.CTkLabel(frame, text=f"{val['date']}")
                btn.pack()
                btn.configure(font=("Segoe UI", 30, 'bold'))
                sender_number = str(val['sender_number'])
                recipient_number = str(val['recipient_number'])
                
                formated_sender_number = " ".join([sender_number[i:i+4] for i in range(0,16,4)])
                formated_recipient_number = " ".join([recipient_number[i:i+4] for i in range(0,16,4)])
                
                
                ctk.CTkLabel(frame, text=f"Nadawca: {val['sender']}").pack()
                ctk.CTkLabel(frame, text=f"Numer konta nadawcy: {formated_sender_number}").pack()
                ctk.CTkLabel(frame, text=f"Odbiorca: {val['recipient']}").pack()
                ctk.CTkLabel(frame, text=f"Numer konta odbiorcy: {formated_recipient_number}").pack()
                ctk.CTkLabel(frame, text=f"Kwota przelewu: {val['amount']} zł").pack()
                if val['outgoing'] == True:
                    type = 'Przychodzący'
                elif val['incoming'] == True:
                    type = 'Odchodzący'   
                ctk.CTkLabel(frame, text=f"Typ: {type}").pack()
                ctk.CTkButton(frame, text="\u2B8C",width=7, height=7, command=main).place(x=10, y=10)
                
                
    else:
        ctk.CTkLabel(frame, text="Brak historii przelewów")
        ctk.CTkButton(frame, text="\u2B8C", width=7 , height=7, command=main).place(x=10, y=10)

def main():
    
    clear_window()
    
    if current_user is None:
        ctk.CTkLabel(root, text="nie jesteś zalogowany").pack()
        return

    btn1 = ctk.CTkLabel(root, text=f"{current_user['name']} {current_user['surname']}")
    btn1.place(x=15, y=5)
    btn1.configure(font=("Segoe UI", 30))
    
    number = str(current_user['number'])
    formated_number = " ".join([number[i:i+4] for i in range(0,16,4)])
    btn2 = ctk.CTkLabel(root, text=f"{formated_number}", )
    btn2.place(x=16, y=42)
    btn2.configure(font=("Segoe UI", 18))
    
    btn3 = ctk.CTkLabel(root, text=f"Dostępne środki: ", )
    btn3.place(x=15, y=82)
    btn3.configure(font=("Segoe UI", 15))
    
    btn4 = ctk.CTkLabel(root, text=f"{current_user['balance']} zł", height=8)
    btn4.place(x=15, y=105)
    btn4.configure(font=("Segoe UI", 20))
    
    btn5 = ctk.CTkButton(root, text="💸 Przelew", command=transfer, width=110, height=30, fg_color="#52555C", corner_radius=15, hover_color="#33353b")
    btn5.place(x=357, y=17)
    btn5.configure(font=("Segoe UI", 15))
    btn6 = ctk.CTkButton(root, text="📜 Historia", command=history, width=110, height=30, fg_color="#52555C", corner_radius=15, hover_color="#33353b")
    btn6.place(x=357, y=59)
    btn6.configure(font=("Segoe UI", 15))
    btn7 = ctk.CTkButton(root, text="🔓 Wyloguj", command=start, width=110, height=30, fg_color="#52555C", corner_radius=15, hover_color="#33353b")
    btn7.place(x=357, y=101)
    btn7.configure(font=("Segoe UI", 15))
    
    
main()

def validate_char(char):
    return char.isdigit() or char == "/"


 
def new_account():
        
        clear_window()
        
        ctk.CTkLabel(root, text="Zakładanie konta").pack()
        
        ctk.CTkLabel(root, text="Imię: ").pack()
        name_entry = ctk.CTkEntry(root)
        name_entry.pack()
        
        ctk.CTkLabel(root, text="Nazwisko: ").pack()
        surname_entry = ctk.CTkEntry(root)
        surname_entry.pack()
            
        ctk.CTkLabel(root, text="Data urodzenia: DD/MM/YYYY ").pack()
        
        vcmd = root.register(validate_char)
        date_of_birth_entry = ctk.CTkEntry(
            root,
            validate="key",
            validatecommand=(vcmd, "%S")
            )
        date_of_birth_entry.pack()
        
        
        ctk.CTkLabel(root, text="Login: ").pack()
        login_entry = ctk.CTkEntry(root)
        login_entry.pack()
        
        ctk.CTkLabel(root, text="Hasło: ").pack()
        password_entry = ctk.CTkEntry(root, show="*")
        password_entry.pack()
        
        ctk.CTkLabel(root, text="Powtórz hasło: ").pack()
        password2_entry = ctk.CTkEntry(root, show="*")
        password2_entry.pack()
        
        ctk.CTkButton(root, text="\u2B8C", width=7, height=7, command=start).place(x=10, y=10)
        
        def change_text_p():
            if show_password.cget('text') == "Pokaż":
                show_password.configure(text="Ukryj")
            else: 
                show_password.configure(text="Pokaż")
                
        def change_text_p2():
            if show_password_repeat.cget('text') == "Pokaż":
                show_password_repeat.configure(text="Ukryj")
            else: 
                show_password_repeat.configure(text="Pokaż")
        
        def toggle_show_password():
            if password_entry.cget('show') == "*":
                password_entry.configure(show="")
            else:
                password_entry.configure(show="*")
            change_text_p()
                        
        def toggle_show_password_repeat():
            if password2_entry.cget('show') == "*":
                password2_entry.configure(show="")
            else:
                password2_entry.configure(show="*")  
            change_text_p2()
                
        show_password = ctk.CTkButton(root, text="Pokaż", command=toggle_show_password, width=50, height=20, fg_color="#52555C", corner_radius=15, hover_color="#33353b")
        show_password.place(x=328, y= 284)
        show_password_repeat = ctk.CTkButton(root, text="Pokaż", command=toggle_show_password_repeat, width=50, height=20, fg_color="#52555C", corner_radius=15, hover_color="#33353b")
        show_password_repeat.place(x=328, y= 340)        
        
            
            
        
        def create_acc():
            name = name_entry.get()
            surname = surname_entry.get()
            date_of_birth = date_of_birth_entry.get()
            if not valid_birth_date(date_of_birth):
                
                new_account()
                error_label = ctk.CTkLabel(root, text="Zły format daty (DD/MM/YYYY)")
                error_label.pack()
                root.after(2000, error_label.destroy)
                return
                
                
            login = login_entry.get()
            password = password_entry.get()
            password2 = password2_entry.get()
            if name or surname or date_of_birth or login or password:
                if login not in data:
                    if password == password2:
                        if FILE.exists():
                            with open(FILE, "w", encoding="utf-8") as f:
                                
                                account = {}
                                account['number'] = random.randint(1000000000000000, 9999999999999999)
                                account['name'] = name
                                account['surname'] = surname
                                account['date_of_birth'] = date_of_birth
                                account['password'] = password
                                account['balance'] = 0
                                account['history'] = []
                                data[login] = account
                                
                                json.dump(data, f, ensure_ascii=False, indent=2)
                                
                                clear_window()
                                ctk.CTkLabel(root, text="Konto założone pomyślnie!").pack()
                                threading.Timer(2, lambda: start() ).start()

                        else:
                            ctk.CTkLabel(root, text="Wystąpił błąd").pack()

                    else:
                        new_account()
                        ctk.CTkLabel(root, text="Hasła nie są takie same!").pack()
                    
                else:
                    new_account()
                    ctk.CTkLabel(root, text="Taki login już istnieje!").pack()
            else:
                new_account()
                ctk.CTkLabel(root, text="Wpisz dane, okno nie może być puste ").pack()
                
        ctk.CTkButton(root, text="Załóż konto", command=create_acc, corner_radius=15).pack(pady=15)
        
            
        
                
def logging():
        clear_window()
        
        ctk.CTkLabel(root, text="Logowanie").pack()
        with open(FILE, "r", encoding='utf-8') as f:
            
            data = json.load(f)
            
            ctk.CTkLabel(root, text="Login: ").pack()
            login_entry = ctk.CTkEntry(root)
            login_entry.pack()
            
            ctk.CTkLabel(root, text="Hasło: ", ).pack()
            password_entry = ctk.CTkEntry(root, show="*")
            password_entry.pack()
            
            ctk.CTkButton(root, text="\u2B8C", command=start, width=7, height=7).place(x=10, y=10)
            
            def change_text_p():
                if show_password.cget('text') == "Pokaż":
                    show_password.configure(text="Ukryj")
                else: 
                    show_password.configure(text="Pokaż")
            
            def toggle_show_password():
                if password_entry.cget('show') == "*":
                    password_entry.configure(show="")
                else:
                    password_entry.configure(show="*")
                change_text_p()
            
            show_password = ctk.CTkButton(root, text="Pokaż", command=toggle_show_password, width=50, height=20, fg_color="#52555C", corner_radius=15, hover_color="#33353b")
            show_password.place(x=328, y= 116)
            
            def log_info():    
                global current_user, current_login
                
                login = login_entry.get()
                password = password_entry.get()
                
                if login in data:
                    user = data[login]
                    if user['password'] == password:
                        current_user = user
                        current_login = login
                        main()

                    else:
                        logging()
                        ctk.CTkLabel(root, text="Nieprawidłowe hasło").pack()

                else:
                    logging()
                    ctk.CTkLabel(root, text="Nieprawidłowy login").pack()
            
            ctk.CTkButton(root, text="Zaloguj się", command=log_info, width=80).pack(pady=15)
                
def start():
    clear_window()
    
    label = ctk.CTkLabel(root, text="Witaj w banku",)
    label.pack(padx=10, pady=10)
    button = ctk.CTkButton(root, text="Logowanie", command=logging)
    button.pack(padx=10, pady=10)
    button = ctk.CTkButton(root, text="Zakładanie konta", command=new_account)
    button.pack(padx=10, pady=5)
    
    
start()


root.mainloop()
            
