def build_where_clause(self):
    """Constrói a cláusula WHERE de forma segura (parametrizada)."""
    clauses = []
    params = []
    for row in self.filter_condition_rows:
        col = row["column"].get()
        op = row["operator"].get()
        val = row["value"].get()
        if col != "Coluna" and op != "Operador" and val != "":
            # Para o operador 'IN', o tratamento do parâmetro é diferente
            if op.upper() == "IN":
                # Cria múltiplos '?' para a quantidade de itens na cláusula IN
                in_params = [v.strip() for v in val.split(',')]
                placeholders = ", ".join(["?"] * len(in_params))
                clauses.append(f"{col} {op} ({placeholders})")
                params.extend(in_params)
            else:
                clauses.append(f"{col} {op} ?")
                params.append(val)
    if not clauses:
        return "", []
    where_string = "WHERE " + " AND ".join(clauses)
    return where_string, params 