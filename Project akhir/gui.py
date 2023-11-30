import tkinter as tk
import threading
from client import *
from tkinter import scrolledtext
from tkinter import messagebox
from datetime import datetime
from tkinter import PhotoImage
from tkinter import filedialog  # Make sure this line is present
import socket
import os
from PIL import Image, ImageTk
import customtkinter


ENCODING = 'utf-8'


class GUI(threading.Thread):
    def __init__(self, client):
        super().__init__(daemon=False, target=self.run)
        self.font = ('Helvetica', 13)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.client = client
        self.login_window = None
        self.main_window = None
        

    def run(self):
        self.login_window = LoginWindow(self, self.font)
        self.main_window = ChatWindow(self, self.font)
        self.notify_server(self.login_window.login, 'login')
        self.main_window.run()

    @staticmethod
    def display_alert(message):
        """Display alert box"""
        messagebox.showinfo('Error', message)

    def update_login_list(self, active_users):
        """Update login list in main window with list of users"""
        self.main_window.update_login_list(active_users)

    def display_message(self, message):
        """Display message in ChatWindow"""
        self.main_window.display_message(message)

    def send_message(self, message):
        """Enqueue message in client's queue"""
        self.client.queue.put(message)

    def set_target(self, target):
        """Set target for messages"""
        self.client.target = target

    def notify_server(self, message, action):
        """Notify server after action was performed"""
        data = action + ";" + message
        data = data.encode(ENCODING)
        self.client.notify_server(data, action)

    def login(self, login):
        self.client.notify_server(login, 'login',)

    def logout(self, logout):
        self.client.notify_server(logout, 'logout')


class Window(object):
    def __init__(self, title, font):
        self.root = tk.Tk()
        self.title = title
        self.root.title(title)
        self.font = font


class LoginWindow(Window):
    def __init__(self, gui, font):
        super().__init__("Login", font)
        self.gui = gui
        self.label = None
        self.entry = None
        self.button = None
        self.login = None

        self.build_window()
        self.run()

    def build_window(self):
        # Load the background image
        background_image = Image.open("loginbg.jpg")
        background_image = ImageTk.PhotoImage(background_image)

        # Create a Label widget to serve as the background
        background_label = tk.Label(self.root, image=background_image)
        background_label.image = background_image  # Keep a reference to the image to prevent it from being garbage collected
        background_label.place(relwidth=1, relheight=1)  # Make the label cover the entire window

        # Create a frame on top of the background for other widgets
        frame = tk.Frame(self.root, bg="#CCD3E4")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Now, add your login elements to the frame
        self.label = tk.Label(frame, text='Login',  bg="#CCD3E4", font=customtkinter.CTkFont("Elephant", 35), fg="black")
        self.label.pack(expand="True", pady=20, padx=20)
        
        self.label = tk.Label(frame, text='Insert Your username',  bg="#CCD3E4", font=self.font, fg="black")
        self.label.pack(expand="True", pady=5)

        self.entry = customtkinter.CTkEntry(frame, font=self.font)
        self.entry.focus_set()
        self.entry.bind('<Return>', self.get_login_event)
        self.entry.pack(expand="True", pady=5)

        self.button = customtkinter.CTkButton(frame, text="Login", width=140)
        self.button.bind('<Button-1>', self.get_login_event)
        self.button.pack(expand="True", pady=5)

    def run(self):
        """Handle login window actions"""
        self.root.mainloop()
        self.root.destroy()

    def get_login_event(self, event):
        """Get login from login box and close login window"""
        self.login = self.entry.get()
        self.root.quit()


class ChatWindow(Window):
    def __init__(self, gui, font):
        super().__init__("Python Chat", font)
        self.gui = gui
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages_list = None
        self.logins_list = None

        self.entry = None
        self.send_button = None
        self.send_file_button = None
        self.exit_button = None
        self.lock = threading.RLock()
        self.target = ''
        self.login = self.gui.login_window.login
        

        self.build_window()

    def sendFile(self, file_path):
        """Send a file to the server"""
        file_name = os.path.basename(file_path)  #salah


        with open(file_path, 'rb') as file:
            file_data = file.read()

        message = f"file;{file_name};{len(file_data)}"

        self.gui.send_message(message.encode(ENCODING))

        confirmation = self.sock.recv(1024).decode(ENCODING)

        if confirmation == 'ready':
            self.gui.send_message(file_data)
            print(f"File '{file_name}' sent successfully.")
        else:
            print("Server is not ready to receive the file.")

    def build_window(self):
        """Build chat window, set widgets positioning and event bindings"""
        # Size config
        self.root.geometry('1000x500')
        self.root.minsize(700, 400)
        self.root.configure(bg="black")
        

        # Frames config
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # List of messages
        frame00 = tk.Frame(main_frame)
        frame00.grid(column=0, row=0, rowspan=2, sticky=tk.N + tk.S + tk.W + tk.E)

        # List of logins
        frame01 = tk.Frame(main_frame)
        frame01.grid(column=1, row=0, rowspan=3, sticky=tk.N + tk.S + tk.W + tk.E)

        # Message entry
        frame02 = tk.Frame(main_frame)
        frame02.grid(column=0, row=2, columnspan=1, sticky=tk.N + tk.S + tk.W + tk.E)

        # Buttons
        frame03 = tk.Frame(main_frame)
        frame03.grid(column=0, row=3, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E)

        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ScrolledText widget for displaying messages
        
        self.messages_list = scrolledtext.ScrolledText(frame00, wrap='word',bg="#1F1D36", font=self.font, fg="white")
        self.messages_list.insert(tk.END, 'Welcome to the club\n')
        self.messages_list.configure(state='disabled')
        self.messages_list.tag_configure("outgoing_message", font=('Your Outgoing Font', 12), foreground="#EEF5FF")
        self.messages_list.tag_configure("incoming_message", font=('Your Incoming Font', 12), foreground="#39A7FF")
        
        # Listbox widget for displaying active users and selecting them
        self.logins_list = tk.Listbox(frame01, selectmode=tk.SINGLE, font=self.font,
                                      exportselection=False,bg="#1F1D36", fg="white")
        self.logins_list.bind('<<ListboxSelect>>', self.selected_login_event)

        # Entry widget for typing messages in
        self.entry = tk.Text(frame02, font=self.font, bg="#1F1D36", fg="white")
        self.entry.focus_set()
        self.entry.bind('<Return>', self.send_entry_event)

        # IMPORT IMAGE FOR BUTTON SEND MESSAGE
        send_button_image = PhotoImage(file='kirimmsg.png')

        # Create a button with the WhatsApp send button image
        self.send_button = tk.Button(frame02, image=send_button_image, command=self.send_entry_event, bd=1, bg="#1F1D36")
        self.send_button.image = send_button_image  # Keep a reference to the image to prevent it from being garbage collected
        self.send_button.bind('<Button-1>', self.send_entry_event)
        
       
        # IMPORT IMAGE FOR BUTTON SEND MESSAGE
        send_file_button_image = PhotoImage(file='file.png')
         ## Button widget for sending file
        self.send_file_button = tk.Button(frame02, image=send_file_button_image, font=self.font, command=self.send_file_dialog, bd=1, bg="#1F1D36")
        self.send_file_button.image = send_file_button_image
        self.send_file_button.bind('<Button-1>')
        
        # Button for exiting
        self.exit_button = tk.Button(frame03, text='Exit', font=self.font)
        self.exit_button.bind('<Button-1>', self.exit_event)

        # Positioning widgets in frame
        self.messages_list.pack(fill=tk.BOTH, expand=tk.YES)
        self.logins_list.pack(fill=tk.BOTH, expand=tk.YES)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.send_button.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)
        self.send_file_button.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.exit_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        # Protocol for closing window using 'x' button
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_event)
        
    def send_file_dialog(self, event=None):
        """Open a file dialog to choose a file and send it to the server"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.sendFile(file_path)

    def send_file(self, file_path):
        """Send the selected file to the server"""
        if self.client is not None:
            self.send_file(file_path)
        else:
            messagebox.showinfo('Error', 'Client not initialized. Cannot send file.')
    def run(self):
        """Handle chat window actions"""
        self.root.mainloop()
        self.root.destroy()

    def selected_login_event(self, event):
        """Set as target currently selected login on login list"""
        target = self.logins_list.get(self.logins_list.curselection())
        self.target = target
        self.gui.set_target(target)

    def send_entry_event(self, event):
        """Send message from entry field to target"""
        text = self.entry.get(1.0, tk.END)
        if text != '\n':
            message = 'msg;' + self.login + ';' + self.target + ';' + text[:-1]
            print(message)
            self.gui.send_message(message.encode(ENCODING))
            self.entry.mark_set(tk.INSERT, 1.0)
            self.entry.delete(1.0, tk.END)
            self.entry.focus_set()
        else:
            messagebox.showinfo('Warning', 'You must enter non-empty message')

        with self.lock:
            self.messages_list.configure(state='normal')
            if text != '\n':
                self.messages_list.insert(tk.END, text)
            self.messages_list.configure(state='disabled')
            self.messages_list.see(tk.END)
        return 'break'

    def exit_event(self, event):
        """Send logout message and quit app when "Exit" pressed"""
        self.gui.notify_server(self.login, 'logout')
        self.root.quit()

    def on_closing_event(self):
        """Exit window when 'x' button is pressed"""
        self.exit_event(None)

    def display_message(self, message, is_outgoing=False):
        """Display message in ScrolledText widget with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        with self.lock:
            self.messages_list.configure(state='normal')
            if is_outgoing:
                self.messages_list.insert(tk.END, formatted_message, "outgoing_message")
            else:
                self.messages_list.insert(tk.END, formatted_message, "incoming_message")
                self.messages_list.see(tk.END)
                self.messages_list.update_idletasks()  # Force update to show the new message
                self.messages_list.yview(tk.END)  # Scroll to the end after the update
            self.messages_list.configure(state='disabled')

    def update_login_list(self, active_users):
        """Update listbox with list of active users"""
        self.logins_list.delete(0, tk.END)
        for user in active_users:
            self.logins_list.insert(tk.END, user)
        self.logins_list.select_set(0)
        self.target = self.logins_list.get(self.logins_list.curselection())
