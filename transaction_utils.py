import pyodbc
from tkinter import messagebox

def commit_transaction(self):
    """Executa um COMMIT real no banco de dados, usando a transação aberta."""
    try:
        if hasattr(self, '_update_conn') and self._update_conn:
            self._update_conn.commit()
            self._update_cursor.close()
            self._update_conn.close()
            self._update_conn = None
            self._update_cursor = None
            self.log("=====================================")
            self.log("✅ COMMIT EXECUTADO. As alterações foram salvas permanentemente.")
            self.log("=====================================")
            self.commit_button.configure(state="disabled")
            self.rollback_button.configure(state="disabled")
        else:
            self.log("Nenhuma transação aberta para commit.")
            messagebox.showwarning("Aviso", "Nenhuma transação aberta para commit.")
    except Exception as e:
        self.log(f"Erro ao executar COMMIT: {e}")
        messagebox.showerror("Erro", f"Erro ao executar COMMIT: {e}")

def rollback_transaction(self):
    """Executa um ROLLBACK real no banco de dados, usando a transação aberta."""
    try:
        if hasattr(self, '_update_conn') and self._update_conn:
            self._update_conn.rollback()
            self._update_cursor.close()
            self._update_conn.close()
            self._update_conn = None
            self._update_cursor = None
            self.log("=====================================")
            self.log("❌ ROLLBACK EXECUTADO. As alterações foram descartadas.")
            self.log("=====================================")
            self.commit_button.configure(state="disabled")
            self.rollback_button.configure(state="disabled")
        else:
            self.log("Nenhuma transação aberta para rollback.")
            messagebox.showwarning("Aviso", "Nenhuma transação aberta para rollback.")
    except Exception as e:
        self.log(f"Erro ao executar ROLLBACK: {e}")
        messagebox.showerror("Erro", f"Erro ao executar ROLLBACK: {e}") 