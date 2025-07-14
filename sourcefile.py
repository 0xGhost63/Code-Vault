import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext, ttk, filedialog

# ------------------ Entry Animation ------------------
class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Launching...")
        self.attributes("-fullscreen", True)
        self.configure(bg="black")

        self.label = tk.Label(self, text="Developed by 0xGhost", font=("Consolas", 32, "bold"), fg="#00ff00", bg="black")
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.opacity = 0
        self.attributes('-alpha', 0.0)
        self.fade_in()

    def fade_in(self):
        if self.opacity < 1:
            self.opacity += 0.05
            self.attributes('-alpha', self.opacity)
            self.after(20, self.fade_in)
        else:
            self.after(800, self.fade_out)

    def fade_out(self):
        if self.opacity > 0:
            self.opacity -= 0.05
            self.attributes('-alpha', self.opacity)
            self.after(20, self.fade_out)
        else:
            self.destroy()

SplashScreen().mainloop()

# ------------------ Data Model ------------------
class Snippet:
    def __init__(self, id, title, language, tags, code, is_favourite):
        self.id = id
        self.title = title
        self.language = language
        self.tags = tags
        self.code = code
        self.is_favourite = is_favourite

    def to_dict(self):
        return self.__dict__

arr = []
snippets_file = "snippets.json"
id_file = "id.txt"

# ------------------ File Handling ------------------
def load_snippets():
    arr.clear()
    if os.path.exists(snippets_file):
        try:
            with open(snippets_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for s in data:
                    arr.append(Snippet(**s))
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load snippets: {e}")

def save_snippets():
    try:
        with open(snippets_file, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in arr], f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save snippets: {e}")

def get_last_id():
    if not os.path.exists(id_file):
        save_last_id(1)
        return 1
    try:
        with open(id_file, "r") as f:
            return int(f.read().strip())
    except:
        save_last_id(1)
        return 1

def save_last_id(id_val):
    try:
        with open(id_file, "w") as f:
            f.write(str(id_val))
    except Exception as e:
        messagebox.showerror("ID Save Error", str(e))

# ------------------ Reset ID ------------------
def reset_ids():
    def confirm_reset():
        for idx, snippet in enumerate(arr, start=1):
            snippet.id = idx
        save_snippets()
        save_last_id(len(arr) + 1)
        confirm_win.destroy()
        messagebox.showinfo("Reset Complete", "All snippet IDs have been reset.")

    def cancel_reset():
        confirm_win.destroy()

    confirm_win = tk.Toplevel(root)
    confirm_win.title("Confirm Reset")
    confirm_win.geometry("400x150")
    confirm_win.configure(bg="#1b1a27")

    tk.Label(confirm_win, text="Are you sure you want to reset the IDs of the code snippets?",
             wraplength=380, font=("Segoe UI", 10, "bold"), bg="#1b1a27", fg="#ffe066").pack(pady=20)

    btns_frame = tk.Frame(confirm_win, bg="#1b1a27")
    btns_frame.pack()

    ttk.Button(btns_frame, text="Yes", command=confirm_reset).pack(side="left", padx=20)
    ttk.Button(btns_frame, text="No", command=cancel_reset).pack(side="left", padx=20)

# ------------------ GUI Logic ------------------
def clear_display():
    output.config(state='normal')
    output.delete(1.0, tk.END)
    output.config(state='disabled')

def display_message(text):
    output.config(state='normal')
    output.insert(tk.END, text)
    output.config(state='disabled')

def reset_form():
    title_entry.delete(0, tk.END)
    lang_entry.delete(0, tk.END)
    tags_entry.delete(0, tk.END)
    code_text.delete("1.0", tk.END)
    fav_var.set(False)

def add_snippet():
    title = title_entry.get().strip()
    language = lang_entry.get().strip()
    tags = tags_entry.get().strip()
    code = code_text.get("1.0", tk.END).strip()
    is_fav = fav_var.get()

    if not title or not language or not code:
        messagebox.showwarning("Missing Fields", "Please fill out Title, Language, and Code.")
        return

    snippet_id = get_last_id()
    new_snippet = Snippet(snippet_id, title, language, tags, code, is_fav)
    arr.append(new_snippet)

    save_snippets()
    save_last_id(snippet_id + 1)
    reset_form()
    display_message(f"Snippet '{title}' added with ID {snippet_id}\n")

def view_snippets():
    clear_display()
    if not arr:
        display_message("No snippets available.\n")
        return
    for s in arr:
        fav_mark = "*" if s.is_favourite else ""
        display_message(f"[{s.id}] {s.title} ({s.language}) {fav_mark}\nTags: {s.tags}\n{s.code}\n{'-'*40}\n")

def view_favourites():
    clear_display()
    favs = [s for s in arr if s.is_favourite]
    if not favs:
        display_message("No favourite snippets.\n")
        return
    for s in favs:
        display_message(f"[{s.id}] {s.title} ({s.language}) *\nTags: {s.tags}\n{s.code}\n{'-'*40}\n")

def search_snippet():
    try:
        sid = simpledialog.askinteger("Search by ID", "Enter Snippet ID:")
        if sid is None:
            return
        result = next((s for s in arr if s.id == sid), None)
        clear_display()
        if result:
            fav_mark = "*" if result.is_favourite else ""
            display_message(f"[{result.id}] {result.title} ({result.language}) {fav_mark}\nTags: {result.tags}\n{result.code}\n")
        else:
            display_message(f"No snippet found with ID {sid}\n")
    except Exception as e:
        messagebox.showerror("Search Error", str(e))

def edit_snippet():
    try:
        sid = simpledialog.askinteger("Edit Snippet", "Enter Snippet ID to Edit:")
        if sid is None:
            return
        snippet = next((s for s in arr if s.id == sid), None)
        if not snippet:
            messagebox.showerror("Not Found", f"Snippet ID {sid} not found.")
            return

        edit_win = tk.Toplevel(root)
        edit_win.title(f"Edit Snippet ID {sid}")
        edit_win.geometry("600x500")
        edit_win.configure(bg="#1b1a27")

        def label(text, row):
            tk.Label(edit_win, text=text, bg="#1b1a27", fg="white", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", padx=10, pady=5)

        def entry(row, var):
            e = ttk.Entry(edit_win, width=50)
            e.insert(0, var)
            e.grid(row=row, column=1, padx=10, pady=5)
            return e

        label("Title:", 0)
        title_e = entry(0, snippet.title)

        label("Language:", 1)
        lang_e = entry(1, snippet.language)

        label("Tags:", 2)
        tags_e = entry(2, snippet.tags)

        label("Code:", 3)
        code_box = scrolledtext.ScrolledText(edit_win, width=50, height=10, bg="#312244", fg="white", insertbackground="white", font=("Consolas", 10))
        code_box.insert(tk.END, snippet.code)
        code_box.grid(row=3, column=1, padx=10, pady=5)

        fav_var = tk.BooleanVar(value=snippet.is_favourite)
        fav_check = ttk.Checkbutton(edit_win, text="Mark as Favourite", variable=fav_var)
        fav_check.grid(row=4, column=1, sticky="w", padx=10, pady=5)

        def save_changes():
            snippet.title = title_e.get().strip() or snippet.title
            snippet.language = lang_e.get().strip() or snippet.language
            snippet.tags = tags_e.get().strip() or snippet.tags
            snippet.code = code_box.get("1.0", tk.END).strip() or snippet.code
            snippet.is_favourite = fav_var.get()
            save_snippets()
            display_message(f"Snippet ID {sid} updated.\n")
            edit_win.destroy()

        ttk.Button(edit_win, text="Save Changes", command=save_changes).grid(row=5, column=1, pady=15)

    except Exception as e:
        messagebox.showerror("Edit Error", str(e))
def delete_snippet():
    try:
        sid = simpledialog.askinteger("Delete Snippet", "Enter Snippet ID to Delete:")
        if sid is None:
            return
        index = next((i for i, s in enumerate(arr) if s.id == sid), None)
        if index is None:
            messagebox.showerror("Not Found", f"Snippet ID {sid} not found.")
            return
        del arr[index]
        save_snippets()
        display_message(f"Snippet ID {sid} deleted.\n")
    except Exception as e:
        messagebox.showerror("Delete Error", str(e))

def export_snippets():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in arr], f, indent=4)
        messagebox.showinfo("Export", "Snippets exported successfully.")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

def import_snippets():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for s in data:
                arr.append(Snippet(**s))
        save_snippets()
        messagebox.showinfo("Import", "Snippets imported successfully.")
    except Exception as e:
        messagebox.showerror("Import Error", str(e))
def search_by_tag():
    try:
        tag_window = tk.Toplevel(root)
        tag_window.title("Search by Tag")
        tag_window.geometry("400x150")
        tag_window.configure(bg="#1b1a27")

        tk.Label(tag_window, text="Select or type a tag to search:", bg="#1b1a27", fg="white", font=("Segoe UI", 10)).pack(pady=10)

        # Collect all unique tags from existing snippets
        all_tags = set()
        for s in arr:
            all_tags.update(t.strip().lower() for t in s.tags.split(",") if t.strip())
        sorted_tags = sorted(all_tags)

        tag_var = tk.StringVar()
        tag_box = ttk.Combobox(tag_window, textvariable=tag_var, values=sorted_tags, width=40)
        tag_box.pack(pady=5)
        tag_box.focus()

        def search():
            tag_query = tag_var.get().strip().lower()
            tag_window.destroy()
            if not tag_query:
                return
            matched = [s for s in arr if tag_query in s.tags.lower()]
            clear_display()
            if not matched:
                display_message(f"No snippets found with tag: '{tag_query}'\n")
                return
            for s in matched:
                fav_mark = "*" if s.is_favourite else ""
                display_message(f"[{s.id}] {s.title} ({s.language}) {fav_mark}\nTags: {s.tags}\n{s.code}\n{'-'*40}\n")

        ttk.Button(tag_window, text="Search", command=search).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Tag Search Error", str(e))
# ------------------ GUI Setup ------------------
root = tk.Tk()
root.title("Code Snippet Manager")
root.geometry("1000x700")
root.configure(bg="#1b1a27")

arcade_title = tk.Label(root, text=" Code Snippet Manager", font=("Bahnschrift", 18, "bold"), bg="#000000", fg="#ffe066", padx=20, pady=10)
arcade_title.pack(fill="x")

style = ttk.Style()
style.theme_use("clam")
accent_color = "#ff4ff7"
highlight = "#ffe066"
bg_color = "#1b1a27"
fg_color = "#f2f2f2"
entry_bg = "#2d2a45"

style.configure("TLabel", foreground=fg_color, background=bg_color, font=("Segoe UI", 10))
style.configure("TEntry", foreground=fg_color, fieldbackground=entry_bg, background=entry_bg)
style.configure("TButton", foreground=highlight, background=entry_bg)
style.map("TButton", background=[("active", accent_color)])
style.configure("TCheckbutton", foreground=fg_color, background=bg_color)
style.configure("Fav.TCheckbutton", background=bg_color, foreground=highlight, font=("Segoe UI", 10, "bold"))
style.map("Fav.TCheckbutton", background=[("active", entry_bg), ("selected", entry_bg)], foreground=[("selected", accent_color), ("active", highlight)])

form = tk.Frame(root, bg=bg_color)
form.pack(pady=10)

fav_var = tk.BooleanVar()
fields = [("Title", "title_entry"), ("Language", "lang_entry"), ("Tags", "tags_entry")]
for idx, (label, varname) in enumerate(fields):
    ttk.Label(form, text=label + ":").grid(row=idx, column=0, sticky="w", padx=5, pady=2)
    entry = ttk.Entry(form, width=40)
    entry.grid(row=idx, column=1, padx=5, pady=2)
    globals()[varname] = entry

ttk.Label(form, text="Code:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
code_text = scrolledtext.ScrolledText(form, width=60, height=8, bg="#312244", fg=fg_color, insertbackground="white", font=("Consolas", 10))
code_text.grid(row=3, column=1, padx=5, pady=5)

fav_check = ttk.Checkbutton(form, text="* Mark as Favourite", variable=fav_var, style="Fav.TCheckbutton")
fav_check.grid(row=4, column=1, sticky="w", padx=5, pady=5)

btn_frame = tk.Frame(root, bg=bg_color)
btn_frame.pack(pady=10)

btns = [
    ("Add Snippet", add_snippet),
    ("View All Snippets", view_snippets),
    ("View Favourites", view_favourites),
    ("Search by ID", search_snippet),
    ("Search by Tag", search_by_tag),
    ("Edit Snippet", edit_snippet),
    ("Delete Snippet", delete_snippet),
    ("Reset ID", reset_ids),
    ("Export", export_snippets),
    ("Import", import_snippets),
    ("Exit", root.quit),
    ("Clear", clear_display)
    
]

for i, (txt, cmd) in enumerate(btns):
    r, c = divmod(i, 3)
    ttk.Button(btn_frame, text=txt, width=30, command=cmd).grid(row=r, column=c, padx=8, pady=6)

output = scrolledtext.ScrolledText(root, width=120, height=15, state='disabled', bg="#281c39", fg=highlight, insertbackground=highlight, font=("Consolas", 10))
output.pack(padx=10, pady=10)

load_snippets()
root.mainloop()
