from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class SymbolTableView(QTableWidget):
    """
    Vista para mostrar la tabla de símbolos.
    """
    def __init__(self, parent=None):
        """
        Inicializa la vista de la tabla de símbolos.
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        # Configurar fuente
        font = QFont("Menlo", 10)  # Menlo es una fuente monoespaciada disponible en macOS
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Configurar estilo
        self.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: #a9b7c6;
                gridline-color: #323232;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #214283;
            }
            QHeaderView::section {
                background-color: #3c3f41;
                color: #a9b7c6;
                padding: 5px;
                border: 1px solid #323232;
            }
        """)
        
        # Configurar encabezados
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['Nombre', 'Tipo', 'Valor', 'Línea', 'Columna'])
        
        # Ajustar columnas
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nombre
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Valor
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Línea
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Columna
        
        # Mensaje inicial
        self.setRowCount(1)
        item = QTableWidgetItem("Sin datos")
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.setItem(0, 0, item)
        self.setSpan(0, 0, 1, 5)
    
    def show_symbol_table(self, symbol_table):
        """
        Muestra los símbolos de la tabla de símbolos.
        
        Args:
            symbol_table (SymbolTable): Tabla de símbolos a mostrar
        """
        # Obtener todos los símbolos
        symbols = symbol_table.get_all_symbols()
        print(f"SymbolTableView: recibidos {len(symbols)} símbolos")

        if not symbols:
            # Mostrar mensaje si no hay símbolos
            self.setRowCount(1)
            item = QTableWidgetItem("No hay símbolos en la tabla")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.setItem(0, 0, item)
            self.setSpan(0, 0, 1, 5)
            return
        
        # Configurar tabla para los símbolos
        self.setRowCount(len(symbols))
        self.clearSpans()
        
        # Llenar tabla con símbolos
        for row, symbol in enumerate(symbols):
            # Nombre
            name_item = QTableWidgetItem(symbol.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row, 0, name_item)
            
            # Tipo
            type_item = QTableWidgetItem(symbol.type if symbol.type else "")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            if symbol.type == 'ent':
                type_item.setForeground(QColor("#9876aa"))  # Púrpura para enteros
            elif symbol.type == 'dec':
                type_item.setForeground(QColor("#6897bb"))  # Azul para decimales
            elif symbol.type == 'cadena':
                type_item.setForeground(QColor("#6a8759"))  # Verde para cadenas
            elif symbol.type == 'bool':
                type_item.setForeground(QColor("#cc7832"))  # Naranja para booleanos
            self.setItem(row, 1, type_item)
            
            # Valor
            value_str = str(symbol.value) if symbol.value is not None else ""
            value_item = QTableWidgetItem(value_str)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            if symbol.type == 'cadena' and symbol.value:
                value_item.setForeground(QColor("#6a8759"))  # Verde para cadenas
            elif symbol.type in ('ent', 'dec') and symbol.value is not None:
                value_item.setForeground(QColor("#6897bb"))  # Azul para números
            self.setItem(row, 2, value_item)
            
            # Línea
            line_item = QTableWidgetItem(str(symbol.line) if symbol.line is not None else "")
            line_item.setFlags(line_item.flags() & ~Qt.ItemIsEditable)
            line_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, line_item)
            
            # Columna
            column_item = QTableWidgetItem(str(symbol.column) if symbol.column is not None else "")
            column_item.setFlags(column_item.flags() & ~Qt.ItemIsEditable)
            column_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, column_item)