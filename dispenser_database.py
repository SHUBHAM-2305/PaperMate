import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('dispenser.db')
cursor = conn.cursor()

# Function to display all users and their total pages dispensed
def view_database():
    # Create a new window to display the database contents
    view_window = tk.Toplevel(root)
    view_window.title("View Database")
    view_window.geometry("600x400")
    
    # Create a Label to display the headers
    tk.Label(view_window, text="Users in Database (with Pages Dispensed)", font=("Helvetica", 16, "bold")).pack(pady=10)
    
    # Fetch all users and their total pages dispensed
    cursor.execute("""
        SELECT users.name, users.uid, SUM(dispensing_history.pages_dispensed) 
        FROM users
        LEFT JOIN dispensing_history ON users.uid = dispensing_history.user_uid
        GROUP BY users.uid
    """)
    users = cursor.fetchall()
    
    if not users:
        messagebox.showinfo("No Data", "No users found in the database.")
        return
    
    # Create a treeview widget to display the user data in a table format
    tree = ttk.Treeview(view_window, columns=("Name", "UID", "Pages Dispensed"), show="headings", height=10)
    tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # Define the column headings
    tree.heading("Name", text="Name")
    tree.heading("UID", text="UID")
    tree.heading("Pages Dispensed", text="Pages Dispensed")

    # Set the column widths (adjust as needed)
    tree.column("Name", width=200, anchor="w")
    tree.column("UID", width=100, anchor="center")
    tree.column("Pages Dispensed", width=150, anchor="center")

    # Add data to the treeview
    for user in users:
        name, uid, total_pages_dispensed = user
        # If no pages have been dispensed, display 0
        total_pages_dispensed = total_pages_dispensed if total_pages_dispensed else 0
        tree.insert("", "end", values=(name, uid, total_pages_dispensed))
    
    # Button to close the view window
    tk.Button(view_window, text="Close", command=view_window.destroy, font=("Helvetica", 12)).pack(pady=10)

# Function to display users sorted by pages dispensed in descending order
def view_sorted_by_pages():
    # Create a new window to display the sorted database contents
    view_window = tk.Toplevel(root)
    view_window.title("Users Sorted by Pages Dispensed")
    view_window.geometry("600x400")
    
    # Create a Label to display the headers
    tk.Label(view_window, text="Users Sorted by Pages Dispensed (Descending)", font=("Helvetica", 16, "bold")).pack(pady=10)
    
    # Fetch users sorted by total pages dispensed in descending order
    cursor.execute("""
        SELECT users.name, users.uid, SUM(dispensing_history.pages_dispensed) 
        FROM users
        LEFT JOIN dispensing_history ON users.uid = dispensing_history.user_uid
        GROUP BY users.uid
        ORDER BY SUM(dispensing_history.pages_dispensed) DESC
    """)
    users = cursor.fetchall()
    
    if not users:
        messagebox.showinfo("No Data", "No users found in the database.")
        return
    
    # Create a treeview widget to display the user data in a table format
    tree = ttk.Treeview(view_window, columns=("Name", "UID", "Pages Dispensed"), show="headings", height=10)
    tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # Define the column headings
    tree.heading("Name", text="Name")
    tree.heading("UID", text="UID")
    tree.heading("Pages Dispensed", text="Pages Dispensed")

    # Set the column widths (adjust as needed)
    tree.column("Name", width=200, anchor="w")
    tree.column("UID", width=100, anchor="center")
    tree.column("Pages Dispensed", width=150, anchor="center")

    # Add data to the treeview
    for user in users:
        name, uid, total_pages_dispensed = user
        # If no pages have been dispensed, display 0
        total_pages_dispensed = total_pages_dispensed if total_pages_dispensed else 0
        tree.insert("", "end", values=(name, uid, total_pages_dispensed))
    
    # Button to close the view window
    tk.Button(view_window, text="Close", command=view_window.destroy, font=("Helvetica", 12)).pack(pady=10)

# Main window
root = tk.Tk()
root.title("Paper Dispenser System")
root.geometry("400x300")

# Button to view the database
tk.Button(root, text="View Database", command=view_database, width=40, height=5, font=("Helvetica", 25, "bold")).pack(pady=10)

# Button to view users sorted by pages dispensed in descending order
tk.Button(root, text="View Sorted by Pages Dispensed", command=view_sorted_by_pages, width=40, height=5, font=("Helvetica", 25, "bold")).pack(pady=10)

root.mainloop()

