from src.classes import course, subject
from src.topological_ordering import top_order
from tkinter import messagebox, simpledialog, Toplevel, Canvas, Scrollbar
import tkinter.font as tkfont
import tkinter as tk
import json
import uuid
import os

DEFAULT_FILE = 'db/courses.json'

class App():
    def __init__(self, root):
        self.root = root
        self.root.title('OrdenaFluxo')
        self.courses = []
        self.current_filepath = DEFAULT_FILE

        # --- UI ---
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Cursos:').grid(row=0, column=0, sticky='w')

        self.listbox = tk.Listbox(frame, height=10, width=60)
        self.listbox.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.listbox.bind('<Double-Button-1>', self.on_edit)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.grid(row=1, column=3, sticky='ns')
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_add = tk.Button(frame, text='Adicionar', width=12, command=self.on_add)
        btn_remove = tk.Button(frame, text='Remover', width=12, command=self.on_remove)
        btn_save = tk.Button(frame, text='Salvar em JSON', width=12, command=self.on_save)
        btn_view = tk.Button(frame, text='Gerar Topologia', width=12, command=self.on_view)
        btn_quit = tk.Button(frame, text='Sair', width=12, command=root.quit)

        btn_add.grid(row=2, column=0, pady=8, sticky='w')
        btn_remove.grid(row=3, column=0, pady=4, sticky='w')
        btn_save.grid(row=2, column=2, pady=4, sticky='e')
        btn_view.grid(row=3, column=2, pady=4, sticky='e')

        btn_quit.grid(row=4, column=2, pady=(12,0), sticky='e')

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

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
        names = [item.name for item in self.courses]
        if name in names:
            messagebox.showwarning('Erro', 'Já existe um curso com esse nome.')
            return
        elif name == '':
            messagebox.showwarning('Erro', 'O nome não deve ser vazio.')
            return
        else:
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

    def on_edit(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Disciplinas', 'Selecione um curso para gerenciar as disciplinas.')
            return
        idx = sel[0]
        course = self.courses[idx]
        self.open_disciplines_window(course)

    def open_disciplines_window(self, course):
        win = tk.Toplevel(self.root)
        win.title(f"Disciplinas — {course.name}")
        win.grab_set()

        tk.Label(win, text='Nome:').grid(row=0, column=0, sticky='w', padx=8, pady=(8,0))
        name_disc = tk.StringVar(value=course.name)
        entry = tk.Entry(win, textvariable=name_disc, width=40)
        entry.grid(row=0, column=1, padx=8, pady=(8,0), sticky='nsew')

        tk.Label(win, text='Disciplinas:').grid(row=1, column=0, columnspan=2, sticky='w', padx=8, pady=(8,0))
        lb = tk.Listbox(win, height=12)
        lb.grid(row=2, column=0, columnspan=2, padx=8, pady=(4,8), sticky='nsew')

        sb = tk.Scrollbar(win, orient=tk.VERTICAL, command=lb.yview)
        sb.grid(row=2, column=2, sticky='ns')
        lb.configure(yscrollcommand=sb.set)

        def refresh_disc_list():
            lb.delete(0, tk.END)
            for d in course.subjects:
                lb.insert(tk.END, d.name)

        def add_disc():
            name = simpledialog.askstring('Adicionar disciplina', 'Nome da disciplina:', parent=win)
            names = [item.name for item in course.subjects]
            if name in names:
                messagebox.showwarning('Erro', 'Já existe uma disciplina com esse nome.', parent=win)
                return
            elif name == '':
                messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=win)
                return
            else:
                course.create_subject(name.strip())
                refresh_disc_list()
                self.refresh_listbox()

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

        def save_disc():
            new_name = name_disc.get().strip()
            names = [item.name for item in self.courses]
            if (new_name in names) and (new_name != course.name):
                messagebox.showwarning('Erro', 'Já existe um curso com esse nome.', parent=win)
                return
            elif new_name == '':
                messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=win)
                return
            else:
                course.name = new_name
                refresh_disc_list()
                self.refresh_listbox()
                win.destroy()

        def edit_disc(self):
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
            entry = tk.Entry(ed, textvariable=name_var, width=20)
            entry.grid(row=0, column=1, padx=8, pady=(8,0), sticky='nsew')

            tk.Label(ed, text='Pré-requisitos (selecione múltiplos):').grid(row=1, column=0, columnspan=2, sticky='w', padx=8, pady=(8,0))

            # Lista de possíveis pré-reqs: todas as outras disciplinas do mesmo curso
            candidates = [d for d in course.subjects if d.name != disc.name]
            listbox_pr = tk.Listbox(ed, selectmode=tk.MULTIPLE, height=10, width=40)
            listbox_pr.grid(row=2, column=0, columnspan=2, padx=8, pady=(4,8), sticky='nsew')

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
                names = [item.name for item in course.subjects]
                if (new_name in names) and (new_name != disc.name):
                    messagebox.showwarning('Erro', 'Já existe uma disciplina com esse nome.', parent=ed)
                    return
                elif new_name == '':
                    messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=ed)
                    return
                
                # coletar seleções e mapear para ids
                sel_idxs = listbox_pr.curselection()
                selected_ids = [candidates[j].name for j in sel_idxs]

                # salvar
                disc.name = new_name
                disc.prereqs = selected_ids

                refresh_disc_list()
                ed.destroy()

            btn_save = tk.Button(ed, text='Salvar', width=12, command=save_edit)
            btn_cancel = tk.Button(ed, text='Cancelar', width=12, command=ed.destroy)
            btn_save.grid(row=3, column=0, pady=8, padx=8, sticky='w')
            btn_cancel.grid(row=3, column=1, pady=8, padx=8, sticky='e')

            ed.grid_rowconfigure(1, weight=1)
            ed.grid_rowconfigure(2, weight=1)
            ed.grid_columnconfigure(1, weight=1)

            # focar na entrada
            entry.focus_set()

        lb.bind('<Double-Button-1>', edit_disc)
        btn_add = tk.Button(win, text='Adicionar', width=12, command=add_disc)
        btn_remove = tk.Button(win, text='Remover', width=12, command=remove_disc)
        btn_save = tk.Button(win, text='Salvar', width=12, command=save_disc)
        btn_cancel = tk.Button(win, text='Cancelar', width=12, command=win.destroy)

        btn_add.grid(row=3, column=0, pady=4, padx=8, sticky='w')
        btn_remove.grid(row=4, column=0, pady=8, padx=8, sticky='w')
        btn_save.grid(row=3, column=1, pady=4, padx=8, sticky='e')
        btn_cancel.grid(row=4, column=1, pady=8, padx=8, sticky='e')

        win.grid_rowconfigure(1, weight=1)
        win.grid_rowconfigure(2, weight=1)
        win.grid_columnconfigure(1, weight=1)

        refresh_disc_list()


    def on_view(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Gerar Ordem', 'Selecione um curso para gerar a ordem topológica.')
            return
        idx = sel[0]
        course = self.courses[idx]
        ordered_subjects = top_order(course.subjects)
        if ordered_subjects == []:
            messagebox.showinfo('Gerar Ordem', 'Há um erro de precedência nas disciplinas')
            return

        win = Toplevel(self.root)
        win.title("Ordenação Topológica")
        win.geometry('900x240')

        # Canvas + scrollbar horizontal
        canvas_frame = tk.Frame(win)
        canvas_frame.pack(fill='both', expand=True)

        hbar = Scrollbar(canvas_frame, orient='horizontal')
        hbar.pack(side='bottom', fill='x')

        canvas = Canvas(canvas_frame, height=180, background='white', xscrollcommand=hbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        hbar.config(command=canvas.xview)

        # Font e medidas
        font = tkfont.nametofont("TkDefaultFont")
        padding_x = 24
        min_width = 120
        max_width = 300
        box_height = 64
        gap = 48  # espaço entre caixas
        top_margin = 40

        # construir lookup por name (fallback)
        name_to_index = {}
        for idx, item in enumerate(ordered_subjects):
            name_to_index[item.name] = idx

        # calcular larguras dos boxes
        widths = []
        for item in ordered_subjects:
            name = item.name
            text_w = font.measure(name)
            w = max(min_width, text_w + padding_x)
            w = min(w, max_width)
            widths.append(w)

        # posições X
        x_positions = []
        x = 20
        for w in widths:
            x_positions.append(x)
            x += w + gap
        total_width = x + 20
        canvas.config(scrollregion=(0,0,total_width, 240))

        # guardar centros e coords dos boxes para desenhar setas
        boxes = []  # lista de dicts: {'left':, 'right':, 'mid_y':, 'center_x':, 'top':, 'bottom':}
        y_top = top_margin

        def on_box_click(index):
            item = ordered_subjects[index]
            name = item.name
            prereqs = item.prereqs
            if not prereqs:
                ptext = '(nenhum pré-requisito)'
            else:
                visible = []
                for p in prereqs:
                    visible.append(str(p))
                ptext = '\n'.join(visible)
            messagebox.showinfo(f'Disciplina: {name}', f'Nome: {name}\nPré-requisitos:\n{ptext}', parent=win)

        # desenha caixas
        for i, item in enumerate(ordered_subjects):
            w = widths[i]
            xp = x_positions[i]
            x1 = xp
            y1 = y_top
            x2 = xp + w
            y2 = y_top + box_height
            # rectangle
            rect = canvas.create_rectangle(x1, y1, x2, y2, width=1.2, outline='#333', fill='#f7fbff')
            # text (com wrap)
            text_id = canvas.create_text((x1+x2)/2, (y1+y2)/2, text=item.name, font=font, width=w-14)
            # ligar cliques tanto ao retângulo quanto ao texto
            canvas.tag_bind(rect, '<Button-1>', lambda ev, idx=i: on_box_click(idx))
            canvas.tag_bind(text_id, '<Button-1>', lambda ev, idx=i: on_box_click(idx))

            boxes.append({
                'left': x1,
                'right': x2,
                'mid_y': (y1+y2)/2,
                'center_x': (x1+x2)/2,
                'top': y1,
                'bottom': y2
            })

        # desenhar setas de pré-requisito -> disciplina
        # para cada disciplina, varrer seus prereqs; se encontrar o índice do prereq, desenhar curva
        for tgt_idx, item in enumerate(ordered_subjects):
            tgt_box = boxes[tgt_idx]
            prereqs = item.prereqs
            for p in prereqs:
                src_idx = None
                if str(p) in name_to_index:
                    src_idx = name_to_index[str(p)]
                else:
                    # não encontrado: ignorar
                    continue
                # garantir que pré venha antes (em topological order deve acontecer)
                src_box = boxes[src_idx]
                # coords: sair do lado direito do src, apontar ao lado esquerdo do target
                start_x = src_box['right']
                start_y = src_box['mid_y']
                end_x = tgt_box['left']
                end_y = tgt_box['mid_y']

                # calcular ponto de controle para curvar a linha (quanto mais distantes, maior a curvatura)
                mid_x = (start_x + end_x) / 2
                distance = abs(tgt_idx - src_idx)
                # curvatura para cima (negativa) — evita colidir com caixas; escala com distância
                curv = 30 + min(80, distance * 8)
                control_y = start_y - curv

                # desenhar curva com três pontos: start -> controle -> end (smooth)
                # empurrar um pouco para fora das bordas das caixas
                sx = start_x + 6
                ex = end_x - 6
                canvas.create_line(sx, start_y, mid_x, control_y, ex, end_y,
                                smooth=True, width=2, arrow='last', arrowshape=(12,14,5))

        # botão fechar
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill='x', pady=(6,6))
        close_btn = tk.Button(btn_frame, text='Fechar', command=win.destroy, width=12)
        close_btn.pack(side='right', padx=10)

        win.transient(self.root)
        win.grab_set()
        win.focus_force()