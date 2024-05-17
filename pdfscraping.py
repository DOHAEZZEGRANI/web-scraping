import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
from PIL import Image, ImageTk
import io

DOWNLOAD_FOLDER = ""
total_downloaded = 0
total_recovered = 0
file_type_selection = 'pdf'

def choose_download_folder():
    global DOWNLOAD_FOLDER
    folder_path = filedialog.askdirectory()
    if folder_path:
        DOWNLOAD_FOLDER = folder_path

def get_files_links():
    global total_recovered
    url = url_entry.get()
    pdf_count = 0
    word_count = 0
    files_links = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if file_type_selection == 'pdf':
                if href.endswith('.pdf'):
                    file_link = urljoin(url, href)
                    files_links.append(file_link)
                    pdf_count += 1
            elif file_type_selection == 'word':
                if href.endswith('.docx'):
                    file_link = urljoin(url, href)
                    files_links.append(file_link)
                    word_count += 1
            elif file_type_selection == 'both':
                if href.endswith('.pdf') or href.endswith('.docx'):
                    file_link = urljoin(url, href)
                    files_links.append(file_link)
                    if href.endswith('.pdf'):
                        pdf_count += 1
                    elif href.endswith('.docx'):
                        word_count += 1
        total_recovered = len(files_links)
        display_links(files_links)
        messagebox.showinfo("Liens récupérés", f"{total_recovered} liens ont été récupérés avec succès.")
        recovered_label.config(text=f"Fichiers récupérés : {total_recovered} (PDF: {pdf_count}, Word: {word_count})")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur de requête", f"Une erreur est survenue lors de la récupération des liens : {e}")
    except Exception as e:
        messagebox.showerror("Erreur inattendue", f"Une erreur inattendue s'est produite : {e}")

def display_links(links):
    links_listbox.delete(0, tk.END)
    for link in links:
        links_listbox.insert(tk.END, link)

def download_selected():
    global total_downloaded
    selected_indexes = links_listbox.curselection()
    if not selected_indexes:
        messagebox.showwarning("Aucune sélection", "Veuillez sélectionner au moins un lien à télécharger.")
        return
    
    if not DOWNLOAD_FOLDER:
        messagebox.showwarning("Aucun dossier sélectionné", "Veuillez choisir un dossier de téléchargement avant de télécharger les fichiers.")
        return
    
    success_message = ""
    for index in selected_indexes:
        file_link = links_listbox.get(index)
        file_name = file_link.split('/')[-1]
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        try:
            with requests.get(file_link, stream=True) as response:
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    success_message += f"Le fichier '{file_name}' a été téléchargé avec succès.\n"
                    total_downloaded += 1
                else:
                    messagebox.showerror("Erreur de téléchargement", f"Le téléchargement du fichier '{file_name}' a échoué avec le code de statut HTTP : {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur de téléchargement", f"Une erreur est survenue lors du téléchargement du fichier '{file_name}': {e}")
        except Exception as e:
            messagebox.showerror("Erreur inattendue", f"Une erreur inattendue s'est produite : {e}")

    if success_message:
        messagebox.showinfo("Téléchargement réussi", success_message)
        downloaded_label.config(text=f"Fichiers téléchargés : {total_downloaded}")

def download_all():
    global total_downloaded, total_recovered
    all_links = links_listbox.get(0, tk.END)
    if not all_links:
        messagebox.showwarning("Aucun lien", "Aucun lien disponible pour le téléchargement.")
        return
    
    if not DOWNLOAD_FOLDER:
        messagebox.showwarning("Aucun dossier sélectionné", "Veuillez choisir un dossier de téléchargement avant de télécharger les fichiers.")
        return
    
    total_recovered = len(all_links)
    
    all_downloaded = False
    for link in all_links:
        file_name = link.split('/')[-1]
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
        try:
            with requests.get(link, stream=True) as response:
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    total_downloaded += 1
                else:
                    messagebox.showerror("Erreur de téléchargement", f"Le téléchargement du fichier '{file_name}' a échoué avec le code de statut HTTP : {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erreur de téléchargement", f"Une erreur est survenue lors du téléchargement du fichier '{file_name}': {e}")
        except Exception as e:
            messagebox.showerror("Erreur inattendue", f"Une erreur inattendue s'est produite : {e}")
    
    all_downloaded = True
    messagebox.showinfo("Téléchargement terminé", "Tous les fichiers ont été téléchargés avec succès.")
    downloaded_label.config(text=f"Fichiers téléchargés : {total_downloaded}")

def on_file_type_change(*args):
    global file_type_selection
    file_type_selection = file_type_var.get()

window = tk.Tk()
window.title("Récupération et Téléchargement de Fichiers")
window.configure(bg="#E0FFFF")

bg_color = "#E0FFFF"
fg_color = "#008B8B"
button_bg = "#008080"
button_fg = "white"

dufu_label = tk.Label(window, text="DUFU scraping", font=("Arial", 16, "italic"), fg=fg_color, bg=bg_color)
dufu_label.grid(row=0, column=0, columnspan=2, pady=5)

logo_url = "https://i.pinimg.com/originals/3a/b0/b3/3ab0b35ae418a7eefe36aec352acd153.png"
logo_response = requests.get(logo_url)
logo_data = logo_response.content

logo_image_pil = Image.open(io.BytesIO(logo_data))
logo_image_pil = logo_image_pil.resize((100, 100))
logo_image_tk = ImageTk.PhotoImage(logo_image_pil)

logo_label = tk.Label(window, image=logo_image_tk, bg=bg_color)
logo_label.grid(row=1, column=0, columnspan=2, pady=10)

url_label = tk.Label(window, text="URL du site web :", font=("Arial", 12), fg=fg_color, bg=bg_color)
url_label.grid(row=2, column=0, padx=5)

url_entry = tk.Entry(window, width=50, font=("Arial", 12))
url_entry.grid(row=2, column=1, padx=5)

file_type_var = tk.StringVar()
file_type_var.set('pdf')  # Définit la valeur par défaut
file_type_menu = tk.OptionMenu(window, file_type_var, 'pdf', 'word', 'both')
file_type_menu.grid(row=3, column=0, pady=20)

file_type_var.trace("w", on_file_type_change)

get_links_button = tk.Button(window, text="Obtenir les liens", command=get_files_links, font=("Arial", 12), bg=button_bg, fg=button_fg)
get_links_button.grid(row=4, column=0, pady=10, padx=5)

download_folder_button = tk.Button(window, text="Choisir le dossier de téléchargement", command=choose_download_folder, font=("Arial", 12), bg=button_bg, fg=button_fg)
download_folder_button.grid(row=4, column=1, pady=10, padx=5)

links_listbox = tk.Listbox(window, width=80, height=10, font=("Arial", 12), selectmode=tk.MULTIPLE)
links_listbox.grid(row=5, column=0, columnspan=2, pady=10)

download_selected_button = tk.Button(window, text="Télécharger les fichiers sélectionnés", command=download_selected, font=("Arial", 12), bg=button_bg, fg=button_fg)
download_selected_button.grid(row=6, column=0, columnspan=2, pady=10, padx=5)

download_all_button = tk.Button(window, text="Télécharger tous les fichiers", command=download_all, font=("Arial", 12), bg=button_bg, fg=button_fg)
download_all_button.grid(row=7, column=0, columnspan=2, pady=10, padx=5)

recovered_label = tk.Label(window, text="Fichiers récupérés : 0", font=("Arial", 12), fg=fg_color, bg=bg_color)
recovered_label.grid(row=8, column=0, columnspan=2, pady=5)

downloaded_label = tk.Label(window, text="Fichiers téléchargés : 0", font=("Arial", 12), fg=fg_color, bg=bg_color)
downloaded_label.grid(row=9, column=0, columnspan=2, pady=5)

error_message_label = tk.Label(window, text="", font=("Arial", 12), fg="red", bg=bg_color)
error_message_label.grid(row=10, column=0, columnspan=2, pady=5)

window.mainloop()
