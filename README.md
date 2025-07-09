# Ferramenta Visual de Update de Banco de Dados

Este projeto é uma aplicação desktop em Python com interface gráfica (CustomTkinter) para manipulação segura de bancos de dados SQL Server.

## Funcionalidades
- Conexão com instâncias SQL Server locais
- Listagem de bancos, tabelas e colunas reais
- Filtros avançados (WHERE) e atualização de registros (UPDATE)
- Backup de dados selecionados
- Controle transacional (Commit/Rollback)
- Visualização dos resultados em tabela com scroll

## Requisitos
- Python 3.8+
- SQL Server (local ou rede)
- Dependências Python:
  - customtkinter
  - pyodbc

## Instalação
1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd <nome-da-pasta>
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Como executar
```bash
python app.py
```

## Estrutura dos arquivos
- `app.py` — Interface principal e lógica de navegação
- `update_utils.py` — Função de update transacional
- `transaction_utils.py` — Funções de commit/rollback
- `backup_utils.py` — Função de backup de dados
- `where_utils.py` — Função utilitária para construção do WHERE
- `result_view.py` — Componente visual para exibição dos resultados

## Observações
- O programa não utiliza autocommit. Todas as alterações só são salvas após pressionar o botão Commit.
- Para rodar em Windows, é necessário o driver ODBC do SQL Server instalado.

---

Desenvolvido para facilitar operações seguras e visuais em bancos SQL Server. 