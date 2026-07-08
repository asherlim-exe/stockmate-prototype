    #prototype
import sqlite3
import tkinter as tk
from tkinter import messagebox

#database set up
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT UNIQUE,
    quantity INTEGER,
    low_stock_threshold INTEGER
)
""")
conn.commit()


#add item button/function
def add_item():
    name = entry_name.get()
    try:
        qty = int(entry_qty.get())
        threshold = int(entry_threshold.get())
    except ValueError:
        messagebox.showerror("Error", "Quantity and threshold must be numbers.")
        return

    try:
        cursor.execute("INSERT INTO inventory (item_name, quantity, low_stock_threshold) VALUES (?, ?, ?)",
                       (name, qty, threshold))
        conn.commit()
        messagebox.showinfo("Success", f"Added {name} with {qty} units.")
        refresh_inventory()
    except sqlite3.IntegrityError:
        messagebox.showwarning("Warning", f"{name} already exists. Try updating instead.")

#update item button/function
def update_item():
    name = entry_name.get()
    try:
        qty = int(entry_qty.get())
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a number.")
        return

    cursor.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (qty, name))
    if cursor.rowcount == 0:
        messagebox.showwarning("Warning", f"{name} not found.")
    else:
        conn.commit()
        messagebox.showinfo("Updated", f"{name} stock set to {qty}.")
        refresh_inventory()

#reduce stock button/function added in Stockmate 2.0
def reduce_stock():
    name = entry_name.get()
    try:
        amount = int(entry_qty.get())
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")
        return

    cursor.execute("SELECT quantity, low_stock_threshold FROM inventory WHERE item_name = ?", (name,))
    row = cursor.fetchone()
    if row:
        new_qty = row[0] - amount
        if new_qty < 0:
            messagebox.showerror("Error", "Not enough stock.")
            return
        cursor.execute("UPDATE inventory SET quantity = ? WHERE item_name = ?", (new_qty, name))
        conn.commit()
        refresh_inventory()
        if new_qty <= row[1]:
            messagebox.showwarning("Low Stock", f"{name} is low! Only {new_qty} left.")
    else:
        messagebox.showwarning("Warning", f"{name} not found.")

#delete item button/function 
def delete_item():
    name = entry_name.get()
    if not name:
        messagebox.showerror("Error", "Enter an item name to delete.")
        return

    cursor.execute("DELETE FROM inventory WHERE item_name = ?", (name,))
    if cursor.rowcount == 0:
        messagebox.showwarning("Warning", f"{name} not found.")
    else:
        conn.commit()
        messagebox.showinfo("Deleted", f"{name} has been removed from inventory.")
        refresh_inventory()

#refresh inventory button/function
def refresh_inventory():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT item_name, quantity, low_stock_threshold FROM inventory")
    items = cursor.fetchall()
    for item in items:
        listbox.insert(tk.END, f"{item[0]} | Qty: {item[1]} | Low-stock at: {item[2]}")



root = tk.Tk()
root.title("StockMate")
root.geometry("1920x1080")


tk.Label(root, text="Item Name").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Quantity / Amount").pack()
entry_qty = tk.Entry(root)
entry_qty.pack()

tk.Label(root, text="Low Stock Threshold").pack()
entry_threshold = tk.Entry(root)
entry_threshold.pack()


tk.Button(root, text="Add Item", command=add_item).pack(pady=2)
tk.Button(root, text="Update Stock", command=update_item).pack(pady=2)
tk.Button(root, text="Reduce Stock", command=reduce_stock).pack(pady=2)
tk.Button(root, text="Delete Item", command=delete_item, fg="red").pack(pady=2)  #delete button graphics, StockMate Ver 2.0


tk.Label(root, text="Inventory:").pack()
listbox = tk.Listbox(root, width=60, height=12)
listbox.pack(pady=5)


tk.Button(root, text="Refresh Inventory", command=refresh_inventory).pack(pady=5)


refresh_inventory()

root.mainloop()
