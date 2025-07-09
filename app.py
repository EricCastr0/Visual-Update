import customtkinter as ctk
from tkinter import messagebox
import time
import pyodbc
import socket
import winreg
from where_utils import build_where_clause
from transaction_utils import commit_transaction, rollback_transaction
from result_view import ResultView

# --- Simulação de um Conector de Banco de Dados ---
# Em um aplicativo real, este módulo conteria a lógica para
# se conectar e executar queries reais usando pyodbc, psycopg2, etc.

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ferramenta Visual de Update de Banco de Dados")
        self.geometry("1200x750")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.db_connector = None
        self.filter_condition_rows = []
        self.backup_checkboxes = []

        # Inicialmente, mostra a tela de login
        self.create_login_screen()

    def log(self, message):
        """Adiciona uma mensagem ao log na tela."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end") # Auto-scroll

    def get_local_sql_instances(self):
        """Lista todas as instâncias do SQL Server instaladas localmente no formato NOMEPC\\INSTANCIA."""
        try:
            instances = []
            key_path = r"SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL"
            try:
                hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            except FileNotFoundError:
                hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
            i = 0
            hostname = socket.gethostname()
            while True:
                try:
                    inst_name = winreg.EnumValue(hkey, i)[0]
                    if inst_name == "MSSQLSERVER":
                        instances.append(f"{hostname}")
                    else:
                        instances.append(f"{hostname}\\{inst_name}")
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(hkey)
            return instances
        except Exception as e:
            return []

    def create_login_screen(self):
        """Cria os widgets da tela de conexão."""
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=20, padx=60, fill="both", expand=True)

        label = ctk.CTkLabel(self.login_frame, text="Conectar ao Servidor SQL", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=30)

        # Listar instâncias locais
        local_instances = self.get_local_sql_instances()
        if local_instances:
            self.server_combobox = ctk.CTkComboBox(self.login_frame, values=local_instances, width=350)
            self.server_combobox.pack(pady=25, padx=10)
            self.server_combobox.set("Selecione uma instância SQL Server")
        else:
            self.server_combobox = None

        self.user_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Usuário banco de dados", width=350)
        self.user_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Senha banco de dados", show="*", width=350)
        self.password_entry.pack(pady=12, padx=10)

        connect_button = ctk.CTkButton(self.login_frame, text="Conectar", command=self.attempt_connection)
        connect_button.pack(pady=30, padx=10)

    def attempt_connection(self):
        """Tenta conectar usando pyodbc real."""
        if self.server_combobox and self.server_combobox.get() != "Selecione uma instância SQL Server":
            server = self.server_combobox.get().strip()
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione uma instância SQL Server.")
            return
        user = self.user_entry.get().strip()
        password = self.password_entry.get().strip()

        # Log para depuração
        print(f"Tentando conectar com: servidor='{server}', usuario='{user}', senha='{password}'")

        # Testa conexão real
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};UID={user};PWD={password};TrustServerCertificate=yes;'
            with pyodbc.connect(conn_str, timeout=5, autocommit=False) as conn:
                pass
            self.server = server
            self.user = user
            self.password = password
            self.login_frame.destroy()
            self.create_main_app_screen()
            self.log("Conexão bem-sucedida!")
            self.log("IMPORTANTE: O modo 'autocommit' foi desativado. Alterações requerem Commit/Rollback.")
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor. Verifique as credenciais.\nServidor: {server}\nUsuário: {user}\nSenha: {password}\nErro: {e}")

    def get_databases(self, server, user, password):
        """Lista os bancos de dados reais da instância SQL Server conectada."""
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};UID={user};PWD={password};TrustServerCertificate=yes;'
            with pyodbc.connect(conn_str, timeout=5, autocommit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
                bancos = [row[0] for row in cursor.fetchall()]
                return bancos
        except Exception as e:
            print(f"Erro ao listar bancos: {e}")
            return []

    def get_tables(self, server, user, password, db_name):
        """Lista as tabelas reais do banco de dados selecionado."""
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={db_name};UID={user};PWD={password};TrustServerCertificate=yes;'
            with pyodbc.connect(conn_str, timeout=5, autocommit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                tabelas = [row[0] for row in cursor.fetchall()]
                return tabelas
        except Exception as e:
            print(f"Erro ao listar tabelas: {e}")
            return []

    def get_columns(self, server, user, password, db_name, table_name):
        """Lista as colunas reais da tabela selecionada."""
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={db_name};UID={user};PWD={password};TrustServerCertificate=yes;'
            with pyodbc.connect(conn_str, timeout=5, autocommit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (table_name,))
                colunas = [row[0] for row in cursor.fetchall()]
                return colunas
        except Exception as e:
            print(f"Erro ao listar colunas: {e}")
            return []

    def create_main_app_screen(self):
        """Cria a tela principal da aplicação após o login."""
        # --- Grid Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Frame da Esquerda (Controles) com Scroll ---
        self.controls_scrollable = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.controls_scrollable.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.controls_scrollable.grid_columnconfigure(0, weight=1)

        # --- Frame do Log (Direita) com Scroll ---
        self.log_scrollable = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.log_scrollable.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.log_scrollable.grid_rowconfigure(1, weight=1)
        self.log_scrollable.grid_rowconfigure(2, weight=2)
        self.log_scrollable.grid_columnconfigure(0, weight=1)

        # --- Widgets de Controle ---
        # 1. Seleção de Banco e Tabela
        selection_frame = ctk.CTkFrame(self.controls_scrollable)
        selection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        selection_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(selection_frame, text="Banco de Dados:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        db_values = self.get_databases(self.server, self.user, self.password)
        self.db_combobox = ctk.CTkComboBox(selection_frame, values=db_values, command=self.on_db_select)
        self.db_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.db_combobox.set("Selecione um Banco")

        ctk.CTkLabel(selection_frame, text="Tabela:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.table_combobox = ctk.CTkComboBox(selection_frame, values=[""], command=self.on_table_select, state="disabled", width=175)
        self.table_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.table_combobox.set("Selecione uma Tabela")
        self.table_combobox.bind('<KeyRelease>', self.filter_table_combobox)
        
        # 2. Backup (Solução: Tabela Temporária)
        backup_frame = ctk.CTkFrame(self.controls_scrollable)
        backup_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        backup_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(backup_frame, text="Passo 1: Backup de Segurança (Obrigatório)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.backup_columns_frame = ctk.CTkScrollableFrame(backup_frame, label_text="Colunas para Backup")
        self.backup_columns_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(backup_frame, text="Criar Backup da Seleção", command=self.create_backup).grid(row=2, column=0, padx=10, pady=10)

        # 3. Filtros (Solução: Anti-SQL Injection)
        filter_frame = ctk.CTkFrame(self.controls_scrollable)
        filter_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(filter_frame, text="Passo 2: Construtor de Filtros (WHERE)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        self.filter_conditions_frame = ctk.CTkFrame(filter_frame)
        self.filter_conditions_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkButton(filter_frame, text="Adicionar Condição", command=self.add_filter_condition).grid(row=2, column=0, padx=10, pady=5)

        # 4. Update
        update_frame = ctk.CTkFrame(self.controls_scrollable)
        update_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        update_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(update_frame, text="Passo 3: Definir a Alteração (SET)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=5)
        ctk.CTkLabel(update_frame, text="Coluna a ser alterada:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.update_column_combobox = ctk.CTkComboBox(update_frame, values=[""], state="disabled")
        self.update_column_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(update_frame, text="Novo valor:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.update_value_entry = ctk.CTkEntry(update_frame, placeholder_text="Digite o novo valor para a coluna selecionada")
        self.update_value_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # 5. Ações
        actions_frame = ctk.CTkFrame(self.controls_scrollable)
        actions_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        actions_frame.grid_columnconfigure((0,1,2,3), weight=1)

        ctk.CTkLabel(actions_frame, text="Passo 4: Execução e Confirmação", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=5)
        self.filter_button = ctk.CTkButton(actions_frame, text="Filtrar Dados", command=self.filter_data)
        self.filter_button.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        
        self.apply_button = ctk.CTkButton(actions_frame, text="Aplicar Update", command=self.apply_update, state="disabled", fg_color="goldenrod")
        self.apply_button.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        self.commit_button = ctk.CTkButton(actions_frame, text="Commit", command=self.commit_transaction, state="disabled", fg_color="green")
        self.commit_button.grid(row=1, column=2, padx=5, pady=10, sticky="ew")
        
        self.rollback_button = ctk.CTkButton(actions_frame, text="Rollback", command=self.rollback_transaction, state="disabled", fg_color="darkred")
        self.rollback_button.grid(row=1, column=3, padx=5, pady=10, sticky="ew")

        # --- Widgets do Log ---
        log_label = ctk.CTkLabel(self.log_scrollable, text="Log de Operações", font=ctk.CTkFont(size=16, weight="bold"))
        log_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.log_textbox = ctk.CTkTextbox(self.log_scrollable, state="disabled", corner_radius=10, height=180)
        self.log_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        # Adiciona a tela de resultados abaixo do log
        self.result_view = ResultView(self.log_scrollable, height=220)
        self.result_view.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    def on_db_select(self, db_name):
        """Callback para quando um banco de dados é selecionado."""
        self.log(f"Banco de dados selecionado: {db_name}")
        tables = self.get_tables(self.server, self.user, self.password, db_name)
        self.all_tables = tables  # Salva todas as tabelas para filtro
        self.table_combobox.configure(values=tables, state="normal")
        self.table_combobox.set("Selecione uma Tabela")
        # Limpa o resto da UI
        self.update_column_combobox.configure(values=[""], state="disabled")
        self.clear_backup_columns()
        self.clear_filter_conditions()

    def filter_table_combobox(self, event=None):
        """Filtra as tabelas do combobox conforme o texto digitado."""
        search_text = self.table_combobox.get().lower()
        filtered = [t for t in getattr(self, 'all_tables', []) if search_text in t.lower()]
        self.table_combobox.configure(values=filtered)
        if filtered:
            self.table_combobox.set(filtered[0])
        else:
            self.table_combobox.set("Nenhuma tabela encontrada")

    def on_table_select(self, table_name):
        """Callback para quando uma tabela é selecionada."""
        self.log(f"Tabela selecionada: {table_name}")
        db_name = self.db_combobox.get()
        columns = self.get_columns(self.server, self.user, self.password, db_name, table_name)
        # Popula as áreas relevantes com as colunas
        self.populate_backup_columns(columns)
        self.update_column_combobox.configure(values=columns, state="normal")
        self.update_column_combobox.set("Selecione a coluna")
        # Limpa filtros antigos e habilita a adição de novos
        self.clear_filter_conditions()
        self.log(f"Colunas disponíveis: {', '.join(columns)}")

    def clear_backup_columns(self):
        for checkbox in self.backup_checkboxes:
            checkbox.destroy()
        self.backup_checkboxes = []

    def populate_backup_columns(self, columns):
        self.clear_backup_columns()
        for col in columns:
            checkbox = ctk.CTkCheckBox(self.backup_columns_frame, text=col)
            checkbox.pack(padx=10, pady=5, anchor="w")
            self.backup_checkboxes.append(checkbox)

    def clear_filter_conditions(self):
        for row in self.filter_condition_rows:
            row["frame"].destroy()
        self.filter_condition_rows = []

    def add_filter_condition(self):
        """Adiciona uma nova linha para o usuário montar uma condição WHERE."""
        table_name = self.table_combobox.get()
        if not table_name or table_name == "Selecione uma Tabela":
            messagebox.showwarning("Aviso", "Por favor, selecione uma tabela primeiro.")
            return

        db_name = self.db_combobox.get()
        columns = self.get_columns(self.server, self.user, self.password, db_name, table_name)
        operators = ["=", "!=", ">", "<", ">=", "<=", "LIKE", "NOT LIKE", "IN"]

        row_frame = ctk.CTkFrame(self.filter_conditions_frame)
        row_frame.pack(fill="x", padx=5, pady=2)

        col_combo = ctk.CTkComboBox(row_frame, values=columns, width=150)
        col_combo.pack(side="left", padx=5, pady=5)
        col_combo.set("Coluna")

        op_combo = ctk.CTkComboBox(row_frame, values=operators, width=100)
        op_combo.pack(side="left", padx=5, pady=5)
        op_combo.set("Operador")

        val_entry = ctk.CTkEntry(row_frame, placeholder_text="Valor")
        val_entry.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        
        remove_button = ctk.CTkButton(row_frame, text="X", width=28, fg_color="transparent", border_width=1,
                                      command=lambda rf=row_frame: self.remove_filter_condition(rf))
        remove_button.pack(side="right", padx=5, pady=5)

        self.filter_condition_rows.append({
            "frame": row_frame,
            "column": col_combo,
            "operator": op_combo,
            "value": val_entry
        })
    
    def remove_filter_condition(self, frame_to_remove):
        """Remove uma linha de condição de filtro."""
        new_rows = []
        for row in self.filter_condition_rows:
            if row["frame"] == frame_to_remove:
                row["frame"].destroy()
            else:
                new_rows.append(row)
        self.filter_condition_rows = new_rows

    def build_where_clause(self):
        return build_where_clause(self)

    def create_backup(self):
        from backup_utils import create_backup
        return create_backup(self)

    def filter_data(self):
        """Filtra e exibe apenas o resultado final da consulta (quantidade de linhas encontradas) e mostra os dados na ResultView."""
        table = self.table_combobox.get()
        db_name = self.db_combobox.get()
        if not table or table == "Selecione uma Tabela":
            messagebox.showwarning("Aviso", "Selecione uma tabela.")
            return
        where_clause, params = self.build_where_clause()
        if not where_clause:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma condição de filtro válida.")
            return
        try:
            conn_str = f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={db_name};UID={self.user};PWD={self.password};TrustServerCertificate=yes;'
            with pyodbc.connect(conn_str, timeout=5, autocommit=False) as conn:
                cursor = conn.cursor()
                sql = f"SELECT * FROM [{table}] {where_clause};"
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                self.result_view.show_results(columns, rows)
                # Força o scroll horizontal para o início
                if hasattr(self.result_view, '_canvas') and self.result_view._canvas is not None:
                    self.result_view._canvas.xview_moveto(0)
                self.log(f"Resultado: {len(rows)} linhas encontradas.")
            self.apply_button.configure(state="normal")
        except Exception as e:
            self.log(f"Erro ao filtrar dados: {e}")
            messagebox.showerror("Erro", f"Erro ao filtrar dados: {e}")

    def apply_update(self):
        from update_utils import apply_update
        return apply_update(self)

    def commit_transaction(self):
        return commit_transaction(self)

    def rollback_transaction(self):
        return rollback_transaction(self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
