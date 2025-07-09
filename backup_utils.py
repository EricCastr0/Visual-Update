import time
from tkinter import messagebox
import pyodbc

def create_backup(self):
    """Cria de fato uma tabela de backup no banco de dados, copiando estrutura e dados das colunas selecionadas."""
    table = self.table_combobox.get()
    db_name = self.db_combobox.get()
    selected_cols = [cb.cget("text") for cb in self.backup_checkboxes if cb.get() == 1]

    if not table or table == "Selecione uma Tabela":
        messagebox.showwarning("Aviso", "Selecione uma tabela.")
        return
    if not selected_cols:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma coluna para o backup.")
        return

    backup_table_name = f"bkp_{table}_{time.strftime('%Y%m%d%H%M%S')}"
    cols_str = ", ".join(selected_cols)

    self.log("--- INICIANDO CRIAÇÃO DE BACKUP ---")
    self.log(f"Ação: Criar uma tabela de backup para a tabela '{table}'.")

    # Buscar tipos das colunas selecionadas
    try:
        # Corrigir: pegar o servidor da instância correta
        server = getattr(self, 'server', None)
        if server is None and hasattr(self, 'db_connector'):
            server = getattr(self.db_connector, 'server', None)
        if not server:
            raise Exception('Servidor não encontrado na instância do App.')
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={db_name};Trusted_Connection=yes;'
        with pyodbc.connect(conn_str, timeout=5, autocommit=False) as conn:
            cursor = conn.cursor()
            col_defs = []
            for col in selected_cols:
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
                """, (table, col))
                row = cursor.fetchone()
                if row:
                    col_name, data_type, char_len = row
                    if char_len and data_type.upper() in ("CHAR", "NCHAR", "VARCHAR", "NVARCHAR"):
                        col_defs.append(f"[{col_name}] {data_type}({char_len})")
                    else:
                        col_defs.append(f"[{col_name}] {data_type}")
                else:
                    col_defs.append(f"[{col}] VARCHAR(255)")  # fallback
            create_sql = f"CREATE TABLE [{backup_table_name}] ({', '.join(col_defs)})"
            self.log(f"SQL Gerado: {create_sql}")
            cursor.execute(create_sql)
            insert_sql = f"INSERT INTO [{backup_table_name}] ({cols_str}) SELECT {cols_str} FROM [{table}]"
            self.log(f"SQL Gerado: {insert_sql}")
            cursor.execute(insert_sql)
            conn.commit()
            self.log("Backup criado com sucesso no banco de dados.")
    except Exception as e:
        self.log(f"Erro ao criar backup real: {e}")
        messagebox.showerror("Erro", f"Erro ao criar backup real: {e}")
    self.log("------------------------------------") 