import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import csv

# ----- Database Setup -----
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ----- Main Application -----
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x600")
        self.root.config(bg="grey")

        # Buttons
        add_btn = tk.Button(root, text="Add Item", command=self.open_add_window)
        add_btn.pack(pady=10)

        update_btn = tk.Button(root, text="Update Item", command=self.update_item)
        update_btn.pack(pady=10)

        delete_btn = tk.Button(root, text="Delete Item", command=self.delete_item)
        delete_btn.pack(pady=10)

        export_btn = tk.Button(root, text="Export to CSV", command=self.export_to_csv)
        export_btn.pack(pady=10)

        search_label = tk.Label(root, text="Search:")
        search_label.pack(pady=5)
        self.search_entry = tk.Entry(root)
        self.search_entry.pack(pady=5)
        search_btn = tk.Button(root, text="Search", command=self.search_inventory)
        search_btn.pack(pady=5)

        # Inventory Table
        self.tree = ttk.Treeview(root, columns=("ID", "Item Name", "Quantity", "Price"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both")

        self.view_inventory()

    def open_add_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add New Item")

        tk.Label(add_win, text="Item Name").grid(row=0, column=0)
        tk.Label(add_win, text="Quantity").grid(row=1, column=0)
        tk.Label(add_win, text="Price").grid(row=2, column=0)

        name_entry = tk.Entry(add_win)
        qty_entry = tk.Entry(add_win)
        price_entry = tk.Entry(add_win)

        name_entry.grid(row=0, column=1)
        qty_entry.grid(row=1, column=1)
        price_entry.grid(row=2, column=1)

        def add_item():
            name = name_entry.get()
            quantity = qty_entry.get()
            price = price_entry.get()

            if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
                conn = sqlite3.connect("inventory.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?)",
                               (name, int(quantity), float(price)))
                conn.commit()
                conn.close()
                add_win.destroy()
                self.view_inventory()
            else:
                messagebox.showerror("Invalid Input", "Please enter valid values.")

        tk.Button(add_win, text="Add", command=add_item).grid(row=3, columnspan=2, pady=10)

    def update_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Item Selected", "Please select an item to update.")
            return

        item_id = self.tree.item(selected_item, "values")[0]
        update_win = tk.Toplevel(self.root)
        update_win.title("Update Item")

        tk.Label(update_win, text="Item Name").grid(row=0, column=0)
        tk.Label(update_win, text="Quantity").grid(row=1, column=0)
        tk.Label(update_win, text="Price").grid(row=2, column=0)

        name_entry = tk.Entry(update_win)
        qty_entry = tk.Entry(update_win)
        price_entry = tk.Entry(update_win)

        name_entry.grid(row=0, column=1)
        qty_entry.grid(row=1, column=1)
        price_entry.grid(row=2, column=1)

        # Pre-fill the existing values for the selected item
        current_values = self.tree.item(selected_item, "values")
        name_entry.insert(0, current_values[1])
        qty_entry.insert(0, current_values[2])
        price_entry.insert(0, current_values[3])

        def update():
            name = name_entry.get()
            quantity = qty_entry.get()
            price = price_entry.get()

            if name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
                conn = sqlite3.connect("inventory.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE inventory SET item_name = ?, quantity = ?, price = ? WHERE id = ?",
                               (name, int(quantity), float(price), item_id))
                conn.commit()
                conn.close()
                update_win.destroy()
                self.view_inventory()
            else:
                messagebox.showerror("Invalid Input", "Please enter valid values.")

        tk.Button(update_win, text="Update", command=update).grid(row=3, columnspan=2, pady=10)

    def delete_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Item Selected", "Please select an item to delete.")
            return

        item_id = self.tree.item(selected_item, "values")[0]
        result = messagebox.askyesno("Delete Item", "Are you sure you want to delete this item?")
        if result:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            self.view_inventory()

    def export_to_csv(self):
        with open("inventory.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Item Name", "Quantity", "Price"])
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory")
            rows = cursor.fetchall()
            conn.close()
            writer.writerows(rows)
        messagebox.showinfo("Export Successful", "Inventory exported to inventory.csv")

    def search_inventory(self):
        search_term = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE item_name LIKE ?", ('%' + search_term + '%',))
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

    def view_inventory(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

# ----- Run -----
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
