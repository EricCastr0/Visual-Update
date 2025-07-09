# 🖥️ Ferramenta Visual de Update de Banco de Dados

Aplicação desktop em Python para manipulação **segura** de bancos SQL Server, com interface gráfica moderna (CustomTkinter).

---

## ✨ Funcionalidades
- 🔗 Conexão fácil com SQL Server local
- 📋 Listagem de bancos, tabelas e colunas reais
- 🎯 Filtros avançados (WHERE) e atualização de registros (UPDATE)
- 💾 Backup de dados selecionados
- 🔒 Controle transacional (Commit/Rollback)
- 👀 Visualização dos resultados em tabela com scroll

## 🛠️ Requisitos
- Python 3.8+
- SQL Server (local ou rede)
- Dependências Python:
  - customtkinter
  - pyodbc

## 🚀 Instalação
```bash
git clone <url-do-repositorio>
cd <nome-da-pasta>
pip install -r requirements.txt
```

## ▶️ Como executar
```bash
python app.py
```

## 📁 Estrutura dos arquivos
- `app.py` — Interface principal
- `update_utils.py` — Update transacional
- `transaction_utils.py` — Commit/Rollback
- `backup_utils.py` — Backup de dados
- `where_utils.py` — Filtros WHERE
- `result_view.py` — Visualização dos resultados

## ⚠️ Observações
- O programa **NÃO** utiliza autocommit. Use o botão Commit para salvar.
- Necessário driver ODBC do SQL Server no Windows.

---

Desenvolvido para facilitar operações seguras e visuais em bancos SQL Server. 