import pyodbc
from tkinter import messagebox

def apply_update(self):
    """Simula a aplicação de um UPDATE na transação."""
    table = self.table_combobox.get()
    db_name = self.db_combobox.get()
    update_col = self.update_column_combobox.get()
    update_val = self.update_value_entry.get()

    if not all([table, update_col, update_val]) or "Selecione" in table or "Selecione" in update_col:
        messagebox.showwarning("Aviso", "Preencha todos os campos da seção 'Definir a Alteração'.")
        return
    
    where_clause, params = self.build_where_clause()
    if not where_clause:
        messagebox.showwarning("Aviso", "É necessário filtrar os dados antes de aplicar um update.")
        return

    full_params = [update_val] + params

    try:
        server = getattr(self, 'server', None)
        if server is None and hasattr(self, 'db_connector'):
            server = getattr(self.db_connector, 'server', None)
        if not server:
            raise Exception('Servidor não encontrado na instância do App.')
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={db_name};UID={self.user};PWD={self.password};TrustServerCertificate=yes;'
        # Abrir conexão sem autocommit
        self._update_conn = pyodbc.connect(conn_str, timeout=5, autocommit=False)
        self._update_cursor = self._update_conn.cursor()
        sql = f"UPDATE [{table}] SET [{update_col}] = ? {where_clause};"
        self.log(f"SQL Gerado: {sql}")
        self.log(f"Parâmetros: {tuple(full_params)}")
        self._update_cursor.execute(sql, full_params)
        self.log(f"Comando executado. {self._update_cursor.rowcount} linhas afetadas.")
        self.log("Aguardando COMMIT para salvar ou ROLLBACK para cancelar.")
    except Exception as e:
        self.log(f"Erro ao executar update: {e}")
        messagebox.showerror("Erro", f"Erro ao executar update: {e}")
    self.commit_button.configure(state="normal")
    self.rollback_button.configure(state="normal")
    self.apply_button.configure(state="disabled") 