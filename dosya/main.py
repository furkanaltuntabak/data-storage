import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import simpledialog
import hashlib
import os
import json
import shutil
from PIL import Image, ImageTk
import datetime
USER_DATA_FILE = 'users.json'
STORAGE_DIR = 'dosya_depolama'
REQUESTS_FILE = 'password_change_requests.json'
LOG_FILE = 'activity_log.json'
MESSAGES_FILE = 'messages.json'

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as file:
        json.dump(messages, file)
def send_message():
    recipient = simpledialog.askstring("Mesaj Gönder", "Mesajı göndermek istediğiniz kullanıcıyı girin:")
    
    if recipient not in users:
        messagebox.showerror("Hata", "Geçersiz kullanıcı adı.")
        return

    message_content = simpledialog.askstring("Mesaj Gönder", "Mesajınızı yazın:")
    
    if not message_content:
        messagebox.showerror("Hata", "Mesaj boş olamaz.")
        return

    messages = load_messages()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if recipient not in messages:
        messages[recipient] = []

    messages[recipient].append({
        "sender": current_user,
        "message": message_content,
        "timestamp": timestamp
    })
    
    save_messages(messages)
    log_activity("Mesaj Gönderme", current_user, f"Mesaj gönderildi: {message_content} - Alıcı: {recipient}")
    messagebox.showinfo("Başarılı", f"Mesaj {recipient} kullanıcısına gönderildi.")
def view_inbox():
    messages = load_messages()
    
    if current_user not in messages or not messages[current_user]:
        messagebox.showinfo("Bilgi", "Henüz bir mesajınız yok.")
        return

    inbox_window = tk.Toplevel(root)
    inbox_window.title(f"{current_user} - Gelen Mesajlar")

    message_listbox = tk.Listbox(inbox_window, width=80, height=20)
    message_listbox.pack(padx=10, pady=10)

    for msg in messages[current_user]:
        message_listbox.insert(tk.END, f"{msg['timestamp']} - {msg['sender']}: {msg['message']}")

def log_activity(action, username, details=""):
    log_entry = {
        "action": action,
        "username": username,
        "details": details,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # datetime ile zaman formatlama
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as file:
            log_data = json.load(file)
    else:
        log_data = []

    log_data.append(log_entry)

    with open(LOG_FILE, 'w') as file:
        json.dump(log_data, file, indent=4)
def load_requests():
    if os.path.exists(REQUESTS_FILE):
        with open(REQUESTS_FILE, 'r') as file:
            return json.load(file)
    return {}

def log_failed_login(username):
    log_activity("Başarısız Giriş", username, "Yanlış şifre veya kullanıcı adı.")

def save_requests(requests):
    with open(REQUESTS_FILE, 'w') as file:
        json.dump(requests, file)

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_profile():
    username = username_entry.get()
    password = password_entry.get()

    if username in users:
        messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")
    else:
        hashed_password = hash_password(password)
        users[username] = hashed_password
        save_users(users)
        messagebox.showinfo("Başarılı", "Profil başarıyla oluşturuldu!")
        log_activity("Kullanıcı Kaydı", username, f"{username} adlı kullanıcı kaydedildi.")  # Log kaydı ekle
        show_file_management_screen(username)

def login():
    global current_user
    username = username_entry.get()
    password = password_entry.get()

    if username not in users:
        messagebox.showerror("Hata", "Kullanıcı adı bulunamadı.")
    else:
        hashed_password = hash_password(password)
        if users[username] == hashed_password:
            current_user = username
            messagebox.showinfo("Başarılı", f"Hoş geldiniz, {username}!")
            log_activity("Giriş", username, f"{username} giriş yaptı.")  # Log kaydı ekle

            if username == 'admin':  # Admin giriş yaptıysa admin panelini göster
                show_admin_panel()
            else:
                show_file_management_screen(username)
        else:
            log_failed_login(username)
            messagebox.showerror("Hata", "Yanlış şifre.")

def show_admin_panel():
    profile_frame.grid_forget()
    admin_panel_frame.grid(row=0, column=0, padx=10, pady=10)
    log_activity("Admin Paneline Erişim", current_user, "Admin paneline erişim sağlandı.")  # Log kaydı ekle
    
    list_users()

def show_file_management_screen(username):
    profile_frame.grid_forget()
    file_management_frame.grid(row=0, column=0, padx=10, pady=10)
    create_user_directory(username)
    list_files(username)

def create_user_directory(username):
    user_directory = os.path.join(STORAGE_DIR, username)
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

def list_users():
    user_listbox.delete(0, tk.END)
    for user in users:
        user_listbox.insert(tk.END, user)

def delete_user():
    selected_user = user_listbox.get(tk.ACTIVE)
    if selected_user and selected_user != 'admin':  # Admin'yi silemeyiz
        del users[selected_user]
        save_users(users)
        messagebox.showinfo("Başarılı", f"{selected_user} kullanıcısı silindi.")
        log_activity("Kullanıcı Silme", current_user, f"{selected_user} kullanıcısı silindi.")  # Log kaydı ekle
        list_users()
    else:
        messagebox.showerror("Hata", "Admin kullanıcısı silinemez.")

def upload_file():
    source_file = filedialog.askopenfilename(title="Dosya Seçin", filetypes=(("Tüm Dosyalar", "*.*"),))
    if source_file:
        user_directory = os.path.join(STORAGE_DIR, current_user)
        num_files_uploaded = len(source_file)
        shutil.copy(source_file, user_directory)
        log_activity("Dosya Yükleme", current_user, f"Yüklenen dosya: {source_file}")
        messagebox.showinfo("Başarılı", f"{source_file} başarıyla {user_directory} dizinine yüklendi.")
        if num_files_uploaded > 1:
            log_activity("Çoklu Dosya Yükleme!!ANORMAL DURUM!!", current_user, f"aynı anda fazla dosya yüklendi: {', '.join(source_file)}")
        list_files(current_user)
    else:
        messagebox.showerror("Hata", "Hiçbir dosya seçilmedi.")
def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        messagebox.showinfo("Başarılı", "İşlem logları başarıyla silindi.")
    else:
        messagebox.showerror("Hata", "Log dosyası bulunamadı.")

def list_files(username):
    user_directory = os.path.join(STORAGE_DIR, username)
    files = os.listdir(user_directory)
    file_listbox.delete(0, tk.END)
    if files:
        for file in files:
            file_listbox.insert(tk.END, file)
def logout():
    global current_user
    current_user = None
    profile_frame.grid(row=0, column=0, padx=10, pady=10)
    admin_panel_frame.grid_forget()
    file_management_frame.grid_forget()
    messagebox.showinfo("Çıkış", "Başarıyla çıkış yapıldı.")
def delete_file():
    selected_file = file_listbox.get(tk.ACTIVE)
    if selected_file:
        file_path = os.path.join(STORAGE_DIR, current_user, selected_file)
        if os.path.exists(file_path):
            os.remove(file_path)
            messagebox.showinfo("Başarılı", f"{selected_file} başarıyla silindi.")
            log_activity("Dosya Silme", current_user, f"{selected_file} dosyası silindi.")  # Log kaydı ekle
            list_files(current_user)
        else:
            messagebox.showerror("Hata", "Dosya bulunamadı.")


def open_file():
    selected_file = file_listbox.get(tk.ACTIVE)
    if selected_file:
        file_path = os.path.join(STORAGE_DIR, current_user, selected_file)
        if os.path.exists(file_path):
            if selected_file.endswith(".txt"):
                open_text_file(file_path)
            elif selected_file.endswith((".jpg", ".png", ".jpeg")):
                open_image_file(file_path)
                log_activity("Dosya Açma", current_user, f"{selected_file} dosyası açıldı.")  # Log kaydı ekle
            else:
                messagebox.showinfo("Desteklenmeyen Dosya", "Bu dosya türü şu an desteklenmiyor.")
        else:
            messagebox.showerror("Hata", "Dosya bulunamadı.")
    else:
        messagebox.showerror("Hata", "Bir dosya seçin.")

def open_text_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    
    text_window = tk.Toplevel(root)
    text_window.title("Metin Dosyası")
    
    text_box = tk.Text(text_window, wrap=tk.WORD, width=50, height=20)
    text_box.insert(tk.END, file_content)
    text_box.pack(padx=10, pady=10)
    text_box.config(state=tk.DISABLED)

def open_image_file(file_path):
    image = Image.open(file_path)
    image = image.resize((400, 400), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image)
    
    image_window = tk.Toplevel(root)
    image_window.title("Resim Dosyası")
    
    image_label = tk.Label(image_window, image=photo)
    image_label.image = photo
    image_label.pack(padx=10, pady=10)

def share_file():
    selected_file = file_listbox.get(tk.ACTIVE)
    if not selected_file:
        messagebox.showerror("Hata", "Bir dosya seçin.")
        return
    
    target_user = simpledialog.askstring("Kullanıcı Seçimi", "Dosyayı paylaşmak istediğiniz kullanıcı adını girin:")
    if target_user not in users:
        messagebox.showerror("Hata", "Geçersiz kullanıcı adı.")
        return

    source_path = os.path.join(STORAGE_DIR, current_user, selected_file)
    target_directory = os.path.join(STORAGE_DIR, target_user)
    
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    
    target_path = os.path.join(target_directory, selected_file)
    
    shutil.copy(source_path, target_path)
    log_activity("Dosya Paylaşma", current_user, f"{selected_file} dosyası {target_user} ile paylaşıldı.")  # Log kaydı ekle
    messagebox.showinfo("Başarılı", f"{selected_file} dosyası {target_user} ile paylaşıldı.")


root = tk.Tk()
root.title("Dosya Depolama Sistemi")

users = load_users()
if 'admin' not in users:
    users['admin'] = hash_password('admin')  # Admin kullanıcısını ekliyoruz

current_user = None

# Profil ekranı
profile_frame = tk.Frame(root)

label_username = tk.Label(profile_frame, text="Kullanıcı Adı:")
label_username.grid(row=0, column=0, padx=10, pady=5)

username_entry = tk.Entry(profile_frame)
username_entry.grid(row=0, column=1, padx=10, pady=5)

label_password = tk.Label(profile_frame, text="Şifre:")
label_password.grid(row=1, column=0, padx=10, pady=5)

password_entry = tk.Entry(profile_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

create_profile_button = tk.Button(profile_frame, text="Profil Oluştur", command=create_profile)
create_profile_button.grid(row=2, column=0, padx=10, pady=10)

login_button = tk.Button(profile_frame, text="Giriş Yap", command=login)
login_button.grid(row=2, column=1, padx=10, pady=10)


profile_frame.grid(row=0, column=0, padx=10, pady=10)

def approve_password_change():
    requests = load_requests()
    if not requests:
        messagebox.showinfo("Bilgi", "Bekleyen hiçbir talep yok.")
        return
    
    user_to_approve = simpledialog.askstring("Talep Onayı", "Onaylamak istediğiniz kullanıcı adını girin:")
    if user_to_approve not in requests:
        messagebox.showerror("Hata", "Bu kullanıcı için talep bulunamadı.")
        return
    
    users[user_to_approve] = requests[user_to_approve]
    del requests[user_to_approve]
    save_users(users)
    save_requests(requests)
    messagebox.showinfo("Başarılı", f"{user_to_approve} kullanıcısının şifresi başarıyla güncellendi.")
def show_activity_log():
    if not os.path.exists(LOG_FILE):
        messagebox.showinfo("Bilgi", "Henüz hiçbir işlem yapılmadı.")
        return

    # Log dosyasını yükle
    with open(LOG_FILE, 'r') as file:
        log_data = json.load(file)

    # Yeni pencere oluştur
    log_window = tk.Toplevel(root)
    log_window.title("İşlem Logları")

    # Kullanıcı adıyla filtreleme için giriş kutusu
    filter_label = tk.Label(log_window, text="Kullanıcı Adına Göre Filtrele:")
    filter_label.pack(padx=10, pady=5)
    
    filter_entry = tk.Entry(log_window)
    filter_entry.pack(padx=10, pady=5)

    def filter_logs():
        username_filter = filter_entry.get()
        filtered_logs = [entry for entry in log_data if username_filter.lower() in entry['username'].lower()]

        log_listbox.delete(0, tk.END)
        if filtered_logs:
            for entry in filtered_logs:
                log_listbox.insert(tk.END, f"{entry['timestamp']} - {entry['username']} - {entry['action']} - {entry['details']}")
        else:
            log_listbox.insert(tk.END, "Hiçbir işlem bulunamadı.")

    # Filtreleme butonu
    filter_button = tk.Button(log_window, text="Filtrele", command=filter_logs)
    filter_button.pack(padx=10, pady=10)

    # Logları listelemek için listbox
    log_listbox = tk.Listbox(log_window, width=80, height=20)
    log_listbox.pack(padx=10, pady=10)

    # İlk başta tüm logları listele
    for entry in log_data:
        log_listbox.insert(tk.END, f"{entry['timestamp']} - {entry['username']} - {entry['action']} - {entry['details']}")

# Listbox ve Label'ı global değişken olarak tanımlayacağız
files_listbox = None
files_listbox_label = None

def load_all_user_files():
    global files_listbox, files_listbox_label

    # Eğer daha önce Listbox oluşturulmuşsa, temizle
    if files_listbox is not None:
        files_listbox.destroy()
    if files_listbox_label is not None:
        files_listbox_label.destroy()

    # Label oluştur
    files_listbox_label = tk.Label(admin_panel_frame, text="Tüm Kullanıcıların Dosyaları:")
    files_listbox_label.grid(row=3, column=0, padx=10, pady=5)

    # Listbox oluştur
    files_listbox = tk.Listbox(admin_panel_frame, width=50, height=15)
    files_listbox.grid(row=4, column=0, padx=10, pady=5)

    # Tüm kullanıcı dosyalarını yükle
    all_files = []
    users = [user for user in os.listdir(STORAGE_DIR) if os.path.isdir(os.path.join(STORAGE_DIR, user))]
    for user in users:
        user_directory = os.path.join(STORAGE_DIR, user)
        files = os.listdir(user_directory)
        for file in files:
            all_files.append(f"{user} -> {file}")

    # Listbox'a dosyaları ekle
    if all_files:
        for entry in all_files:
            files_listbox.insert(tk.END, entry)
    else:
        files_listbox.insert(tk.END, "Hiçbir dosya bulunamadı.")

        
admin_panel_frame = tk.Frame(root)

user_listbox = tk.Listbox(admin_panel_frame, width=40, height=10)
user_listbox.grid(row=0, column=0, padx=10, pady=10)

delete_user_button = tk.Button(admin_panel_frame, text="Kullanıcı Sil", command=delete_user)
delete_user_button.grid(row=1, column=0, padx=10, pady=10)

approve_password_button = tk.Button(admin_panel_frame, text="Şifre Talebini Onayla", command=approve_password_change)
approve_password_button.grid(row=2, column=0, padx=10, pady=10)

view_log_button = tk.Button(admin_panel_frame, text="İşlem Loglarını Görüntüle", command=show_activity_log)
view_log_button.grid(row=3, column=0, padx=10, pady=10)

clear_log_button = tk.Button(admin_panel_frame, text="Logları Sil", command=clear_log)
clear_log_button.grid(row=4, column=0, padx=10, pady=10)

load_files_button = tk.Button(admin_panel_frame, text="Tüm Dosyaları Görüntüle", command=load_all_user_files)
load_files_button.grid(row=5, column=0, padx=10, pady=10)

logout_button_admin = tk.Button(admin_panel_frame, text="Çıkış Yap", command=logout)
logout_button_admin.grid(row=6, column=0, padx=10, pady=10)



def request_password_change():
    global current_user
    if not current_user:
        messagebox.showerror("Hata", "Önce giriş yapmalısınız.")
        return

    new_password = simpledialog.askstring("Şifre Değiştirme", "Yeni şifrenizi girin:", show="*")
    confirm_password = simpledialog.askstring("Şifre Değiştirme", "Yeni şifrenizi tekrar girin:", show="*")
    
    if new_password != confirm_password:
        messagebox.showerror("Hata", "Şifreler uyuşmuyor.")
        return

    requests = load_requests()
    requests[current_user] = hash_password(new_password)
    save_requests(requests)

    # Log kaydetme
    log_activity("Şifre Değişikliği Talebi", current_user)
    
    messagebox.showinfo("Başarılı", "Şifre değişikliği talebiniz admin onayı bekliyor.")

# Dosya yönetim ekranı
file_management_frame = tk.Frame(root)


label_file = tk.Label(file_management_frame, text="Yüklemek istediğiniz dosyanın yolunu girin:")
label_file.grid(row=0, column=0, padx=10, pady=5)

file_entry = tk.Entry(file_management_frame)
file_entry.grid(row=0, column=1, padx=10, pady=5)

upload_button = tk.Button(file_management_frame, text="Dosya Yükle", command=upload_file)
upload_button.grid(row=1, column=0, padx=10, pady=10)

list_button = tk.Button(file_management_frame, text="Dosyaları Listele", command=lambda: list_files(current_user))
list_button.grid(row=1, column=1, padx=10, pady=10)

file_listbox = tk.Listbox(file_management_frame, width=40, height=10)
file_listbox.grid(row=2, column=0, columnspan=2, padx=30, pady=50)

delete_button = tk.Button(file_management_frame, text="Dosya Sil", command=delete_file)
delete_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

open_button = tk.Button(file_management_frame, text="Dosyayı Aç", command=open_file)
open_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

share_button = tk.Button(file_management_frame, text="Dosyayı Paylaş", command=share_file)
share_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
request_password_button = tk.Button(file_management_frame, text="Şifre Değişikliği Talebi", command=request_password_change)
request_password_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

message_button = tk.Button(file_management_frame, text="Gelen Mesajlar", command=view_inbox)
message_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

send_message_button = tk.Button(file_management_frame, text="Mesaj Gönder", command=send_message)
send_message_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
logout_button_profile = tk.Button(file_management_frame, text="Çıkış Yap", command=logout)
logout_button_profile.grid(row=3, column=0, padx=10, pady=10)
root.mainloop()  
