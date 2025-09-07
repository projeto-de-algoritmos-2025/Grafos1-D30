from src.classes import course, subject
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import uuid
import os

DEFAULT_FILE = 'db/courses.json'

class App():
    def __init__(self, root):
        self.root = root
        self.root.title('OrdenaFluxo')
        self.courses = []  # lista de dicionários: {'id':..., 'name':..., 'prereqs':[...]}
        self.current_filepath = DEFAULT_FILE

        # --- UI ---
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Cursos:').grid(row=0, column=0, sticky='w')

        self.listbox = tk.Listbox(frame, height=20, width=120)
        self.listbox.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.listbox.bind('<Double-Button-1>', self.on_edit_name)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.grid(row=1, column=3, sticky='ns')
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_add = tk.Button(frame, text='Adicionar', width=12, command=self.on_add)
        btn_edit_name = tk.Button(frame, text='Editar Nome', width=12, command=self.on_edit_name)
        btn_remove = tk.Button(frame, text='Remover', width=12, command=self.on_remove)
        btn_edit_order = tk.Button(frame, text='Editar Disciplinas', width=12, command=self.on_manage_disciplines)
        btn_save = tk.Button(frame, text='Salvar', width=12, command=self.on_save)
        btn_view = tk.Button(frame, text='Gerar Ordem', width=12, command=self.on_view)
        btn_quit = tk.Button(frame, text='Sair', width=12, command=root.quit)

        btn_add.grid(row=2, column=0, pady=8, sticky='w')
        btn_remove.grid(row=3, column=0, pady=4, sticky='w')

        btn_edit_name.grid(row=2, column=1, pady=8)
        btn_edit_order.grid(row=2, column=2, pady=8, sticky='e')
        btn_save.grid(row=3, column=1, pady=4)
        btn_view.grid(row=3, column=2, pady=4, sticky='e')

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
            self.listbox.insert(tk.END, c.name)

    def on_add(self):
        name = simpledialog.askstring('Adicionar curso', 'Nome do curso:')
        if name:
            # cria objeto de curso
            new_course = course(name.strip())
            self.courses.append(new_course)
            self.refresh_listbox()

    def on_remove(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Remover', 'Selecione um curso para remover.')
            return
        idx = sel[0]
        course = self.courses[idx]
        if messagebox.askyesno('Confirmar remoção', f'Deseja remover o curso "{course.name}"?'):
            del self.courses[idx]
            self.refresh_listbox()

    def on_edit_name(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Editar', 'Selecione um curso para editar.')
            return
        idx = sel[0]
        course = self.courses[idx]
        new_name = simpledialog.askstring('Editar curso', 'Nome do curso:', initialvalue=course.name)
        if new_name:
            course.name = new_name.strip()
            self.refresh_listbox()

    def on_view(self):
        pass

    def on_save(self):
        try:
            self.save_to_file(self.current_filepath)
            messagebox.showinfo('Salvo', f'Salvo em: {self.current_filepath}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar:\n{e}')

    def save_to_file(self, filepath):
        # criar pasta se necessário
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            db_dump = []
            for c in self.courses:
                db_dump.append(c.data_list())
            json.dump(db_dump, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # deserialization start
        db_courses = []
        
        for d in data:
            db_subjects = []
            for key, value in d['subjects'].items():
                db_subject = subject(key)
                db_subject.prereqs = value
                db_subjects.append(db_subject)

            db_course = course(d['name'])
            db_course.id = d['id']
            db_course.subjects = db_subjects
            db_courses.append(db_course)
        # deserialization end

        if not isinstance(data, list):
            raise ValueError('Formato inválido: esperado uma lista de cursos')
        self.courses = db_courses
        self.refresh_listbox()





    def on_manage_disciplines(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Disciplinas', 'Selecione um curso para gerenciar as disciplinas.')
            return
        idx = sel[0]
        course = self.courses[idx]
        self.open_disciplines_window(course)

    def open_disciplines_window(self, course):
        """Abre uma janela (Toplevel) para listar/adicionar/editar/remover disciplinas do curso."""
        win = tk.Toplevel(self.root)
        win.title(f"Disciplinas — {course.name}")
        win.geometry('450x320')

        lbl = tk.Label(win, text=f"Disciplinas do curso: {course.name}")
        lbl.pack(anchor='w', padx=8, pady=(8,0))

        lf = tk.Frame(win, padx=8, pady=8)
        lf.pack(fill=tk.BOTH, expand=True)

        lb = tk.Listbox(lf, height=12)
        lb.grid(row=0, column=0, columnspan=3, sticky='nsew')

        sb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=lb.yview)
        sb.grid(row=0, column=3, sticky='ns')
        lb.configure(yscrollcommand=sb.set)

        def refresh_disc_list():
            lb.delete(0, tk.END)
            for d in course.subjects:
                lb.insert(tk.END, d.name)

        def add_disc():
            name = simpledialog.askstring('Adicionar disciplina', 'Nome da disciplina:', parent=win)
            if name:
                course.create_subject(name.strip())

                refresh_disc_list()
                self.refresh_listbox()



        def edit_disc():
            s = lb.curselection()
            if not s:
                messagebox.showinfo('Editar', 'Selecione uma disciplina para editar.', parent=win)
                return
            i = s[0]
            disc = course.subjects[i]

            # Janela de edição: permite alterar nome e selecionar pré-requisitos
            ed = tk.Toplevel(win)
            ed.title(f"Editar — {disc.name}")
            ed.grab_set()

            tk.Label(ed, text='Nome:').grid(row=0, column=0, sticky='w', padx=8, pady=(8,0))
            name_var = tk.StringVar(value=disc.name)
            entry = tk.Entry(ed, textvariable=name_var, width=40)
            entry.grid(row=0, column=1, padx=8, pady=(8,0))

            tk.Label(ed, text='Pré-requisitos (selecione múltiplos):').grid(row=1, column=0, columnspan=2, sticky='w', padx=8, pady=(8,0))

            # Lista de possíveis pré-reqs: todas as outras disciplinas do mesmo curso
            candidates = [d for d in course.subjects if d.name != disc.name]
            listbox_pr = tk.Listbox(ed, selectmode=tk.MULTIPLE, height=10, width=50)
            listbox_pr.grid(row=2, column=0, columnspan=2, padx=8, pady=(4,8))

            # preencher
            id_to_index = {}
            for idx_c, cand in enumerate(candidates):
                listbox_pr.insert(tk.END, cand.name)
                id_to_index[cand.name] = idx_c

            # pre-selecionar os que já são pré-reqs
            existing = disc.prereqs
            for pid in existing:
                if pid in id_to_index:
                    listbox_pr.selection_set(id_to_index[pid])

            def save_edit():
                new_name = name_var.get().strip()
                if not new_name:
                    messagebox.showwarning('Validação', 'O nome não pode ficar vazio.', parent=ed)
                    return
                # coletar seleções e mapear para ids
                sel_idxs = listbox_pr.curselection()
                selected_ids = [candidates[j].name for j in sel_idxs]

                # salvar
                disc.name = new_name
                disc.prereqs = selected_ids

                refresh_disc_list()
                self.refresh_listbox()
                ed.destroy()

            btn_save = tk.Button(ed, text='Salvar', width=12, command=save_edit)
            btn_cancel = tk.Button(ed, text='Cancelar', width=12, command=ed.destroy)
            btn_save.grid(row=3, column=0, pady=8, padx=8, sticky='e')
            btn_cancel.grid(row=3, column=1, pady=8, padx=8, sticky='w')

            # focar na entrada
            entry.focus_set()



        def remove_disc():
            s = lb.curselection()
            if not s:
                messagebox.showinfo('Remover', 'Selecione uma disciplina para remover.', parent=win)
                return
            i = s[0]
            disc = course.subjects[i]
            if messagebox.askyesno('Confirmar remoção', f'Deseja remover a disciplina "{disc.name}"?', parent=win):
                del course.subjects[i]
                refresh_disc_list()
                self.refresh_listbox()

        btn_add = tk.Button(lf, text='Adicionar', width=12, command=add_disc)
        btn_edit = tk.Button(lf, text='Editar', width=12, command=edit_disc)
        btn_remove = tk.Button(lf, text='Remover', width=12, command=remove_disc)

        btn_add.grid(row=1, column=0, pady=8, sticky='w')
        btn_edit.grid(row=1, column=1, pady=8)
        btn_remove.grid(row=1, column=2, pady=8, sticky='e')

        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)

        refresh_disc_list()


