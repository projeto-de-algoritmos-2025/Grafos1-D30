import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import uuid
import os

DEFAULT_FILE = 'db/courses.json'

class App():
    def __init__(self, root):
        self.root = root
        self.root.title('Gerenciador de Cursos — Topological Demo')
        self.courses = []  # lista de dicionários: {'id':..., 'name':..., 'prereqs':[...]}
        self.current_filepath = DEFAULT_FILE

        # --- UI ---
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Cursos:').grid(row=0, column=0, sticky='w')

        self.listbox = tk.Listbox(frame, height=12, width=40)
        self.listbox.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.listbox.bind('<Double-Button-1>', self.on_edit)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.grid(row=1, column=3, sticky='ns')
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_add = tk.Button(frame, text='Adicionar', width=12, command=self.on_add)
        btn_edit = tk.Button(frame, text='Editar', width=12, command=self.on_edit)
        btn_remove = tk.Button(frame, text='Remover', width=12, command=self.on_remove)
        btn_load = tk.Button(frame, text='Carregar...', width=12, command=self.on_load)
        btn_save = tk.Button(frame, text='Salvar', width=12, command=self.on_save)
        btn_saveas = tk.Button(frame, text='Salvar como...', width=12, command=self.on_save_as)
        btn_quit = tk.Button(frame, text='Sair', width=12, command=root.quit)

        btn_add.grid(row=2, column=0, pady=8, sticky='w')
        btn_edit.grid(row=2, column=1, pady=8)
        btn_remove.grid(row=2, column=2, pady=8, sticky='e')

        btn_load.grid(row=3, column=0, pady=4, sticky='w')
        btn_save.grid(row=3, column=1, pady=4)
        btn_saveas.grid(row=3, column=2, pady=4, sticky='e')

        btn_quit.grid(row=4, column=2, pady=(12,0), sticky='e')

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)

        # Carrega automaticamente o arquivo padrão (se existir)
        if os.path.exists(self.current_filepath):
            try:
                self.load_from_file(self.current_filepath)
            except Exception:
                messagebox.showwarning('Aviso', f'Não foi possível carregar {self.current_filepath}')

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for c in self.courses:
            self.listbox.insert(tk.END, c['name'])

    def on_add(self):
        name = simpledialog.askstring('Adicionar curso', 'Nome do curso:')
        if name:
            # cria objeto de curso
            new_course = {
                'id': uuid.uuid4().hex,
                'name': name.strip(),
                'prereqs': []  # inicialmente vazio; etapas futuras adicionarão disciplinas e pré-reqs
            }
            self.courses.append(new_course)
            self.refresh_listbox()

    def on_edit(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Editar', 'Selecione um curso para editar.')
            return
        idx = sel[0]
        course = self.courses[idx]
        new_name = simpledialog.askstring('Editar curso', 'Nome do curso:', initialvalue=course['name'])
        if new_name:
            course['name'] = new_name.strip()
            self.refresh_listbox()

    def on_remove(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Remover', 'Selecione um curso para remover.')
            return
        idx = sel[0]
        course = self.courses[idx]
        if messagebox.askyesno('Confirmar remoção', f'Deseja remover o curso "{course["name"]}"?'):
            del self.courses[idx]
            self.refresh_listbox()

    def on_load(self):
        filepath = filedialog.askopenfilename(title='Abrir arquivo JSON', filetypes=[('JSON files','*.json'),('All files','*.*')])
        if not filepath:
            return
        try:
            self.load_from_file(filepath)
            self.current_filepath = filepath
            messagebox.showinfo('Carregado', f'Arquivo carregado: {os.path.basename(filepath)}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar JSON:\n{e}')

    def on_save(self):
        try:
            self.save_to_file(self.current_filepath)
            messagebox.showinfo('Salvo', f'Salvo em: {self.current_filepath}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar:\n{e}')

    def on_save_as(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json'),('All files','*.*')])
        if not filepath:
            return
        try:
            self.save_to_file(filepath)
            self.current_filepath = filepath
            messagebox.showinfo('Salvo', f'Salvo em: {self.current_filepath}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar:\n{e}')

    def load_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Validar formato: esperamos uma lista de objetos com 'id' e 'name'
        if not isinstance(data, list):
            raise ValueError('Formato inválido: esperado uma lista de cursos')
        cleaned = []
        for item in data:
            if 'id' in item and 'name' in item:
                # garantir chave prereqs
                item.setdefault('prereqs', [])
                cleaned.append(item)
        self.courses = cleaned
        self.refresh_listbox()

    def save_to_file(self, filepath):
        # criar pasta se necessário
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)
