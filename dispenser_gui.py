import tkinter as tk
from tkinter import messagebox
import sqlite3
import serial  # For communication with Arduino
import time

# Serial connection to Arduino Nano
arduino = serial.Serial('/dev/ttyUSB0', 9600)

# Database connection
conn = sqlite3.connect('dispenser.db')
cursor = conn.cursor()

# Global variables for admin password and registered users
admin_password = 'admin123'  # Admin password to register new users

# Main window
root = tk.Tk()
root.title("Paper Dispenser System")

def register_user():
    def submit_registration():
        # Verify that all fields are filled out
        name = name_entry.get()
        uid = uid_entry.get()
        password = password_entry.get()
        
        if not name and not uid and not password:
            messagebox.showerror("Error","Please enter all the fields")
            return
            reg_window.lift()
            
        if not name and not uid:
            messagebox.showerror("Error","Please enter name and user ID")
            return
            reg_window.lift()
        
        if not name:
            messagebox.showerror("Error", "Please enter name")
            return
            reg_window.lift()
            
        if not uid:
            messagebox.showerror("Error","Please enter uid")
            return
            reg_window.lift()
        
        if not password:
            messagebox.showerror("Error","Please enter password")
            return
            reg_window.lift()
            
      # Verify admin password
        if password != admin_password:
            messagebox.showerror("Error", "Incorrect admin password!")
            return
            reg_window.lift()
        
        # Insert new user into the database
        try:
            cursor.execute("INSERT INTO users (name, uid) VALUES (?, ?)", (name, uid))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            reg_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "UID already exists!")
            reg_window.destroy()
    
     # Registration window
    reg_window = tk.Toplevel(root)
    reg_window.title("Register New User")
    reg_window.geometry("400x300")

    font_button = ('Helvetica', 13, 'bold')

    # Configure grid column for even spacing
    reg_window.grid_columnconfigure(0, weight=1)
    reg_window.grid_columnconfigure(1, weight=1)

    # Label and Entry for Admin Password
    tk.Label(reg_window, text="Admin Password", font=font_button).grid(row=0, column=0, padx=20, pady=10, sticky="e")
    password_entry = tk.Entry(reg_window, show='*')
    password_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

    # Label and Entry for Name
    tk.Label(reg_window, text="Name", font=font_button).grid(row=1, column=0, padx=20, pady=10, sticky="e")
    name_entry = tk.Entry(reg_window)
    name_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

    # Label and Entry for UID
    tk.Label(reg_window, text="UID", font=font_button).grid(row=2, column=0, padx=20, pady=10, sticky="e")
    uid_entry = tk.Entry(reg_window)
    uid_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")

    # Register Button
    tk.Button(reg_window, text="Register", command=submit_registration, font=font_button).grid(row=3, column=1, padx=20, pady=10)


def dispense_paper():
    def submit_dispensing():
        # Get user inputs
        name = name_entry.get()
        uid = uid_entry.get()
        pages = pages_entry.get()

        # Verify that all fields are filled out
        if not name and not uid and not pages:
            messagebox.showerror("Error", "Please enter all the fields!")
            return
            
        if not name and not uid:
            messagebox.showerror("Error","Please enter name and uid!")
            return
            
        if not name:
            messagebox.showerror("Error","Please enter name")
            return
            
        if not uid:
            messagebox.showerror("Error","Please enter User ID")
            return
            
        if not pages:
            messagebox.showerror("Error","Please enter number of pages")
            return

        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE name=? AND uid=?", (name, uid))
        user = cursor.fetchone()

        if user:
            # Send dispensing information to Arduino
            if pages.isdigit():
                pages_to_dispense = int(pages)
                arduino.write(str(pages_to_dispense).encode())

                # Wait for Arduino to process and dispense pages
                arduino_response = ''
                total_pages_dispensed = False

                while True:
                    if arduino.in_waiting > 0:
                        # Read the serial response from Arduino
                        line = arduino.readline().decode().strip()
                        arduino_response += line + "\n"
                        
                        # Check if we received the 'Total pages dispensed:' response
                        if "Total pages dispensed:" in line:
                            total_pages_dispensed = True

                    # Exit the loop if the expected response is received
                    if total_pages_dispensed:
                        break
                    time.sleep(0.1)  # Adjust this time if necessary to avoid high CPU usage

                # Store dispensing info in database
                cursor.execute("INSERT INTO dispensing_history (user_name, user_uid, pages_dispensed) VALUES (?, ?, ?)", 
                               (name, uid, pages_to_dispense))
                conn.commit()

                # Show the serial responses in the message box
                if arduino_response:
                    messagebox.showinfo("Success", f"Arduino Response:\n{arduino_response}")
                else:
                    messagebox.showinfo("Success", "No response from Arduino after dispensing.")
                
                dispense_window.destroy()

            else:
                messagebox.showerror("Error", "Enter a valid number of pages!")
        else:
            messagebox.showerror("Error", "User not found!")

     # Dispensing window
    dispense_window = tk.Toplevel(root)
    dispense_window.title("Dispense Paper")
    dispense_window.geometry("400x300")
    
    font_button = ('Helvetica', 13, 'bold') 

    # Configure grid column for even spacing
    dispense_window.grid_columnconfigure(0, weight=1)
    dispense_window.grid_columnconfigure(1, weight=1)

    # Label and Entry for Name
    tk.Label(dispense_window, text="Name", font = font_button).grid(row=0, column=0, padx=20, pady=10, sticky="e")
    name_entry = tk.Entry(dispense_window)
    name_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

    # Label and Entry for UID
    tk.Label(dispense_window, text="UID", font = font_button).grid(row=1, column=0, padx=20, pady=10, sticky="e")
    uid_entry = tk.Entry(dispense_window)
    uid_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

    # Label and Entry for Pages to Dispense
    tk.Label(dispense_window, text="Pages to Dispense", font = font_button).grid(row=2, column=0, padx=20, pady=10, sticky="e")
    pages_entry = tk.Entry(dispense_window)
    pages_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")

    # Button to trigger paper dispensing
    tk.Button(dispense_window, text="Dispense", command=submit_dispensing, font = font_button).grid(row=3, column=1, padx=20, pady=10)


# Main screen buttons
tk.Button(root, text="Register New User", command=register_user, width=40, height=5, font=("Helvetica", 25, "bold")).pack(pady=10)

tk.Button(root, text="Dispense Paper", command=dispense_paper, width=40, height=5, font=("Helvetica", 25, "bold")).pack(pady=10)

root.mainloop()
