import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry # type: ignore
import sqlite3
from datetime import datetime

# Função para criar as tabelas no banco de dados
def criar_tabelas():
    conn = sqlite3.connect('padaria.db')
    cursor = conn.cursor()

    cursor.execute('''DROP TABLE IF EXISTS produtos''')
    cursor.execute('''DROP TABLE IF EXISTS estoque''')
    cursor.execute('''DROP TABLE IF EXISTS receitas''')
    cursor.execute('''DROP TABLE IF EXISTS clientes''')

    cursor.execute('''CREATE TABLE produtos
                      (id INTEGER PRIMARY KEY, nome TEXT, codigo TEXT, lote TEXT, quantidade INTEGER, data_ent TEXT, data_venc TEXT)''')
    cursor.execute('''CREATE TABLE estoque
                      (id INTEGER PRIMARY KEY, nome TEXT, quantidade INTEGER)''')
    cursor.execute('''CREATE TABLE receitas
                      (id INTEGER PRIMARY KEY, nome TEXT, ingredientes TEXT, instrucoes TEXT)''')
    cursor.execute('''CREATE TABLE clientes
                      (id INTEGER PRIMARY KEY, nome TEXT, telefone TEXT, email TEXT, endereco TEXT, data_nasc TEXT)''')
    conn.commit()
    conn.close()

# Função para salvar as informações do produto no banco de dados
def salvar_produto():
    nome = entry_nome.get()
    codigo = entry_codigo.get()
    lote = entry_lote.get()
    quantidade = entry_quantidade.get()
    data_ent = entry_data_ent.get_date()
    data_venc = entry_data_venc.get_date()

    try:
        quantidade = int(quantidade)
    except ValueError:
        messagebox.showerror("Erro", "Quantidade deve ser um número inteiro.")
        return

    data_ent = data_ent.strftime('%Y-%m-%d')
    data_venc = data_venc.strftime('%Y-%m-%d')

    try:
        conn = sqlite3.connect('padaria.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, codigo, lote, quantidade, data_ent, data_venc) VALUES (?, ?, ?, ?, ?, ?)",
                       (nome, codigo, lote, quantidade, data_ent, data_venc))
        conn.commit()

        cursor.execute("SELECT nome, SUM(quantidade) FROM produtos GROUP BY nome")
        estoque = cursor.fetchall()
        cursor.execute("DELETE FROM estoque")
        for nome_prod, quantidade_prod in estoque:
            cursor.execute("INSERT INTO estoque (nome, quantidade) VALUES (?, ?)", (nome_prod, quantidade_prod))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Produto salvo com sucesso!")
        visualizar_produtos()
        visualizar_estoque()
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar produto: {e}")

# Função para visualizar os produtos cadastrados
def visualizar_produtos():
    conn = sqlite3.connect('padaria.db')
    cursor = conn.cursor()

    for item in tree_produtos.get_children():
        tree_produtos.delete(item)

    cursor.execute("SELECT * FROM produtos")
    for row in cursor.fetchall():
        tree_produtos.insert("", "end", values=row, tags=(validade_cor(row[6]),))

    conn.close()

# Função para definir a cor dos produtos com base na validade
def validade_cor(data_vencimento):
    data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d')
    if data_vencimento >= datetime.now():
        return 'dentro_validade'
    else:
        return 'fora_validade'

# Função para visualizar o estoque
def visualizar_estoque():
    conn = sqlite3.connect('padaria.db')
    cursor = conn.cursor()

    # Limpar a exibição anterior do estoque
    for item in tree_estoque.get_children():
        tree_estoque.delete(item)

    # Selecionar os dados corretos da tabela de estoque
    cursor.execute("SELECT nome, quantidade FROM estoque")
    for row in cursor.fetchall():
        tree_estoque.insert("", "end", values=row)

    conn.close()


# Função para salvar as informações da receita no banco de dados
def salvar_receita():
    nome = entry_nome_receita.get()
    ingredientes = entry_ingredientes.get("1.0", tk.END)
    instrucoes = entry_instrucoes.get("1.0", tk.END)

    try:
        conn = sqlite3.connect('padaria.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO receitas (nome, ingredientes, instrucoes) VALUES (?, ?, ?)",
                       (nome, ingredientes, instrucoes))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Receita salva com sucesso!")
        visualizar_receitas()
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar receita: {e}")

# Função para visualizar as receitas cadastradas
def visualizar_receitas():
    conn = sqlite3.connect('padaria.db')
    cursor = conn.cursor()

    for item in tree_receitas.get_children():
        tree_receitas.delete(item)

    cursor.execute("SELECT * FROM receitas")
    for row in cursor.fetchall():
        tree_receitas.insert("", "end", values=row)

    conn.close()

# Função para salvar as informações do cliente no banco de dados
def salvar_cliente():
    nome = entry_nome_cliente.get()
    telefone = entry_telefone.get()
    email = entry_email.get()
    endereco = entry_endereco.get()
    data_nasc = entry_data_nasc.get_date()

    data_nasc = data_nasc.strftime('%Y-%m-%d')

    try:
        conn = sqlite3.connect('padaria.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, telefone, email, endereco, data_nasc) VALUES (?, ?, ?, ?, ?)",
                       (nome, telefone, email, endereco, data_nasc))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!")
        visualizar_clientes()
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar cliente: {e}")

# Função para visualizar os clientes cadastrados
def visualizar_clientes():
    conn = sqlite3.connect('padaria.db')
    cursor = conn.cursor()

    for item in tree_clientes.get_children():
        tree_clientes.delete(item)

    cursor.execute("SELECT * FROM clientes")
    for row in cursor.fetchall():
        tree_clientes.insert("", "end", values=row)

    conn.close()

# Criar janela principal
root = tk.Tk()
root.title("Padaria da Celinha Vai")
root.geometry("920x700")
root.configure(bg='#1F0705')

# Estilo para as abas
style = ttk.Style()
style.theme_create('custom', parent='alt', settings={
    'TNotebook': {'configure': {'tabmargins': [2, 5, 2, 0]}},
    'TNotebook.Tab': {
        'configure': {'padding': [10, 5], 'background': '#FFA500', 'foreground': 'black'},
        'map':       {'background': [('selected', '#FFD700')], 'expand': [('selected', [1, 1, 1, 0])]}}})
style.theme_use('custom')

# Título
title_frame = tk.Frame(root, bg='#1F0705', bd=2, relief=tk.SUNKEN)
title_frame.pack(fill='x', pady=10)

logo_label = tk.Label(title_frame, text="Padaria da Celinha Vai", font=("Arial", 24), fg='#FFA500', bg='#1F0705')
logo_label.pack(padx=10)

# Abas
tab_control = ttk.Notebook(root)

# Aba de Produtos
produtos_frame = tk.Frame(tab_control, bg='#FFA500')
tab_control.add(produtos_frame, text='Produtos')

columns_produtos = ('ID', 'Nome', 'Código', 'Lote', 'Quantidade', 'Data Ent.', 'Data Venc.')
tree_produtos = ttk.Treeview(produtos_frame, columns=columns_produtos, show='headings')

# Configuração das cores das linhas
tree_produtos.tag_configure('dentro_validade', background='#90EE90')  # verde suave
tree_produtos.tag_configure('fora_validade', background='#FFB6C1')  # vermelho suave

for col in columns_produtos:
    tree_produtos.heading(col, text=col, anchor=tk.CENTER)
    tree_produtos.column(col, width=120, anchor=tk.CENTER)

tree_produtos.pack(expand=True, fill='both', pady=10, padx=10)

# Adicionar barra de rolagem vertical e horizontal para a tabela de produtos
scrollbar_produtos_y = ttk.Scrollbar(produtos_frame, orient="vertical", command=tree_produtos.yview)
scrollbar_produtos_y.pack(side="right", fill="y")
tree_produtos.configure(yscrollcommand=scrollbar_produtos_y.set)

scrollbar_produtos_x = ttk.Scrollbar(produtos_frame, orient="horizontal", command=tree_produtos.xview)
scrollbar_produtos_x.pack(side="bottom", fill="x")
tree_produtos.configure(xscrollcommand=scrollbar_produtos_x.set)

# Adicionar Produto
entry_frame_produtos = tk.Frame(produtos_frame, bg='#FFA500')
entry_frame_produtos.pack(fill='x', padx=10, pady=5)

tk.Label(entry_frame_produtos, text="Nome:", bg='#FFA500').grid(row=0, column=0)
entry_nome = tk.Entry(entry_frame_produtos)
entry_nome.grid(row=0, column=1)

tk.Label(entry_frame_produtos, text="Código:", bg='#FFA500').grid(row=1, column=0)
entry_codigo = tk.Entry(entry_frame_produtos)
entry_codigo.grid(row=1, column=1)

tk.Label(entry_frame_produtos, text="Lote:", bg='#FFA500').grid(row=2, column=0)
entry_lote = tk.Entry(entry_frame_produtos)
entry_lote.grid(row=2, column=1)

tk.Label(entry_frame_produtos, text="Quantidade:", bg='#FFA500').grid(row=3, column=0)
entry_quantidade = tk.Entry(entry_frame_produtos)
entry_quantidade.grid(row=3, column=1)

tk.Label(entry_frame_produtos, text="Data de Entrada:", bg='#FFA500').grid(row=4, column=0)
entry_data_ent = DateEntry(entry_frame_produtos, date_pattern='yyyy-mm-dd')
entry_data_ent.grid(row=4, column=1)

tk.Label(entry_frame_produtos, text="Data de Vencimento:", bg='#FFA500').grid(row=5, column=0)
entry_data_venc = DateEntry(entry_frame_produtos, date_pattern='yyyy-mm-dd')
entry_data_venc.grid(row=5, column=1)

button_salvar_produto = tk.Button(entry_frame_produtos, text="Salvar Produto", command=salvar_produto, bg='#1F0705', fg='#FFA500')
button_salvar_produto.grid(row=6, columnspan=2, pady=10)

# Aba de Estoque
estoque_frame = tk.Frame(tab_control, bg='#FFA500')
tab_control.add(estoque_frame, text='Estoque')

columns_estoque = ('Nome', 'Quantidade')
tree_estoque = ttk.Treeview(estoque_frame, columns=columns_estoque, show='headings')

for col in columns_estoque:
    tree_estoque.heading(col, text=col, anchor=tk.CENTER)
    tree_estoque.column(col, width=150, anchor=tk.CENTER)

tree_estoque.pack(expand=True, fill='both', pady=10, padx=10)

# Adicionar barra de rolagem vertical e horizontal para a tabela de estoque
scrollbar_estoque_y = ttk.Scrollbar(estoque_frame, orient="vertical", command=tree_estoque.yview)
scrollbar_estoque_y.pack(side="right", fill="y")
tree_estoque.configure(yscrollcommand=scrollbar_estoque_y.set)

scrollbar_estoque_x = ttk.Scrollbar(estoque_frame, orient="horizontal", command=tree_estoque.xview)
scrollbar_estoque_x.pack(side="bottom", fill="x")
tree_estoque.configure(xscrollcommand=scrollbar_estoque_x.set)

# Aba de Receitas
receitas_frame = tk.Frame(tab_control, bg='#FFA500')
tab_control.add(receitas_frame, text='Receitas')

columns_receitas = ('ID', 'Nome', 'Ingredientes', 'Instruções')
tree_receitas = ttk.Treeview(receitas_frame, columns=columns_receitas, show='headings')

for col in columns_receitas:
    tree_receitas.heading(col, text=col, anchor=tk.CENTER)
    tree_receitas.column(col, width=150, anchor=tk.CENTER)

tree_receitas.pack(expand=True, fill='both', pady=10, padx=10)

# Adicionar barra de rolagem vertical e horizontal para a tabela de receitas
scrollbar_receitas_y = ttk.Scrollbar(receitas_frame, orient="vertical", command=tree_receitas.yview)
scrollbar_receitas_y.pack(side="right", fill="y")
tree_receitas.configure(yscrollcommand=scrollbar_receitas_y.set)

scrollbar_receitas_x = ttk.Scrollbar(receitas_frame, orient="horizontal", command=tree_receitas.xview)
scrollbar_receitas_x.pack(side="bottom", fill="x")
tree_receitas.configure(xscrollcommand=scrollbar_receitas_x.set)

# Adicionar Receita
entry_frame_receitas = tk.Frame(receitas_frame, bg='#FFA500')
entry_frame_receitas.pack(fill='x', padx=10, pady=5)

tk.Label(entry_frame_receitas, text="Nome:", bg='#FFA500').grid(row=0, column=0)
entry_nome_receita = tk.Entry(entry_frame_receitas)
entry_nome_receita.grid(row=0, column=1)

tk.Label(entry_frame_receitas, text="Ingredientes:", bg='#FFA500').grid(row=1, column=0)
entry_ingredientes = tk.Text(entry_frame_receitas, height=5, width=50)
entry_ingredientes.grid(row=1, column=1)

tk.Label(entry_frame_receitas, text="Instruções:", bg='#FFA500').grid(row=2, column=0)
entry_instrucoes = tk.Text(entry_frame_receitas, height=5, width=50)
entry_instrucoes.grid(row=2, column=1)

button_salvar_receita = tk.Button(entry_frame_receitas, text="Salvar Receita", command=salvar_receita, bg='#1F0705', fg='#FFA500')
button_salvar_receita.grid(row=3, columnspan=2, pady=10)

# Aba de Clientes
clientes_frame = tk.Frame(tab_control, bg='#FFA500')
tab_control.add(clientes_frame, text='Clientes')

columns_clientes = ('ID', 'Nome', 'Telefone', 'Email', 'Endereço', 'Data de Nascimento')
tree_clientes = ttk.Treeview(clientes_frame, columns=columns_clientes, show='headings')

for col in columns_clientes:
    tree_clientes.heading(col, text=col, anchor=tk.CENTER)
    tree_clientes.column(col, width=150, anchor=tk.CENTER)

tree_clientes.pack(expand=True, fill='both', pady=10, padx=10)

# Adicionar barra de rolagem vertical e horizontal para a tabela de clientes
scrollbar_clientes_y = ttk.Scrollbar(clientes_frame, orient="vertical", command=tree_clientes.yview)
scrollbar_clientes_y.pack(side="right", fill="y")
tree_clientes.configure(yscrollcommand=scrollbar_clientes_y.set)

scrollbar_clientes_x = ttk.Scrollbar(clientes_frame, orient="horizontal", command=tree_clientes.xview)
scrollbar_clientes_x.pack(side="bottom", fill="x")
tree_clientes.configure(xscrollcommand=scrollbar_clientes_x.set)

# Adicionar Cliente
entry_frame_clientes = tk.Frame(clientes_frame, bg='#FFA500')
entry_frame_clientes.pack(fill='x', padx=10, pady=5)

tk.Label(entry_frame_clientes, text="Nome:", bg='#FFA500').grid(row=0, column=0)
entry_nome_cliente = tk.Entry(entry_frame_clientes)
entry_nome_cliente.grid(row=0, column=1)

tk.Label(entry_frame_clientes, text="Telefone:", bg='#FFA500').grid(row=1, column=0)
entry_telefone = tk.Entry(entry_frame_clientes)
entry_telefone.grid(row=1, column=1)

tk.Label(entry_frame_clientes, text="Email:", bg='#FFA500').grid(row=2, column=0)
entry_email = tk.Entry(entry_frame_clientes)
entry_email.grid(row=2, column=1)

tk.Label(entry_frame_clientes, text="Endereço:", bg='#FFA500').grid(row=3, column=0)
entry_endereco = tk.Entry(entry_frame_clientes)
entry_endereco.grid(row=3, column=1)

tk.Label(entry_frame_clientes, text="Data de Nascimento:", bg='#FFA500').grid(row=4, column=0)
entry_data_nasc = DateEntry(entry_frame_clientes, date_pattern='yyyy-mm-dd')
entry_data_nasc.grid(row=4, column=1)

button_salvar_cliente = tk.Button(entry_frame_clientes, text="Salvar Cliente", command=salvar_cliente, bg='#1F0705', fg='#FFA500')
button_salvar_cliente.grid(row=5, columnspan=2, pady=10)

# Exibir Abas
tab_control.pack(expand=1, fill='both')

# Inicializar as tabelas e carregar dados
criar_tabelas()
visualizar_produtos()
visualizar_estoque()
visualizar_receitas()
visualizar_clientes()

root.mainloop()


