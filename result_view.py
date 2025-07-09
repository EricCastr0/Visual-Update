import customtkinter as ctk

class ResultView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.headers = []
        self.rows = []
        self.header_labels = []
        self.cell_labels = []
        # Adiciona scrollbar horizontal se o canvas existir
        canvas = getattr(self, '_canvas', None)
        if canvas is None:
            canvas = getattr(self, '_scrollable_canvas', None)
        self._canvas = canvas
        if self._canvas is not None:
            self._hscroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self._canvas.xview)
            self._canvas.configure(xscrollcommand=self._hscroll.set)
            self._hscroll.grid(row=99, column=0, columnspan=999, sticky="ew")
        else:
            self._hscroll = None

    def show_results(self, columns, data):
        # Limpa resultados anteriores
        for lbl in self.header_labels:
            lbl.destroy()
        for row in self.cell_labels:
            for lbl in row:
                lbl.destroy()
        self.header_labels = []
        self.cell_labels = []

        # Exibe cabeçalhos
        for j, col in enumerate(columns):
            lbl = ctk.CTkLabel(self, text=col, font=ctk.CTkFont(size=12, weight="bold"))
            lbl.grid(row=0, column=j, padx=4, pady=2, sticky="nsew")
            self.header_labels.append(lbl)

        # Exibe dados
        for i, row in enumerate(data):
            row_labels = []
            for j, value in enumerate(row):
                lbl = ctk.CTkLabel(self, text=str(value), font=ctk.CTkFont(size=11))
                lbl.grid(row=i+1, column=j, padx=4, pady=2, sticky="nsew")
                row_labels.append(lbl)
            self.cell_labels.append(row_labels)
        # Força atualização do canvas para o scrollbar funcionar
        if self._canvas is not None:
            self._canvas.update_idletasks() 