from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont, QColor, QTextCursor
from PyQt5.QtCore import Qt

class OutputView(QTextEdit):
    """
    Vista para mostrar resultados del análisis.
    """
    def __init__(self, parent=None):
        """
        Inicializa la vista de salida.
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        # Configurar fuente y estilos
        font = QFont("Menlo", 10)  # Menlo es una fuente monoespaciada disponible en macOS
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Solo lectura
        self.setReadOnly(True)
        
        # Configurar colores
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: none;
            }
        """)
        
        # Mensaje inicial
        self.setPlainText("Bienvenido al Analizador Léxico, Sintáctico y Semántico.\n\n"
                         "Utilice los botones o el menú Análisis para comenzar.")
    
    def append_message(self, message, color=None):
        """
        Añade un mensaje a la salida.
        
        Args:
            message (str): Mensaje a añadir
            color (QColor, optional): Color del texto
        """
        self.moveCursor(QTextCursor.End)
        
        if color:
            self.setTextColor(color)
        else:
            self.setTextColor(QColor("#a9b7c6"))  # Color predeterminado
        
        self.insertPlainText(message + "\n")
        self.moveCursor(QTextCursor.End)
    
    def append_error(self, error, indent=0):
        """
        Añade un mensaje de error a la salida.
        
        Args:
            error (CompilerError): Error a mostrar
            indent (int, optional): Nivel de indentación
        """
        indent_str = "  " * indent
        message = f"{indent_str}{error}"
        self.append_message(message, QColor("#ff6b68"))  # Rojo para errores
    
    def show_errors(self, title, errors):
        """
        Muestra una lista de errores.
        
        Args:
            title (str): Título para la sección de errores
            errors (list): Lista de errores a mostrar
        """
        self.clear()
        self.append_message(f"=== {title} ===\n", QColor("#ffc66d"))  # Amarillo para títulos
        
        if not errors:
            self.append_message("No se encontraron errores.")
            return
        
        for error in errors:
            self.append_error(error)
        
        self.append_message(f"\nSe encontraron {len(errors)} errores.")
    
    def show_tokens(self, tokens):
        """
        Muestra los tokens encontrados durante el análisis léxico.
        
        Args:
            tokens (list): Lista de tokens a mostrar
        """
        self.clear()
        self.append_message("=== Tokens Encontrados ===\n", QColor("#ffc66d"))
        
        if not tokens:
            self.append_message("No se encontraron tokens.")
            return
        
        # Encabezado de la tabla
        self.append_message("| Tipo                | Valor              | Línea | Columna |")
        self.append_message("|---------------------|--------------------|---------|----|")
        
        # Contenido de la tabla
        for token in tokens:
            # Ajustar el ancho de las columnas
            type_str = str(token.type)[:19].ljust(19)
            value_str = str(token.value)[:19].ljust(19)
            line_str = str(token.line).ljust(7)
            col_str = str(token.column).ljust(4)
            
            self.append_message(f"| {type_str} | {value_str} | {line_str} | {col_str} |")
        
        self.append_message(f"\nTotal: {len(tokens)} tokens")
    
    def show_ast(self, ast, detailed=False):
        """
        Muestra el AST generado durante el análisis sintáctico.
        
        Args:
            ast (ASTNode): Raíz del AST a mostrar
            detailed (bool, optional): True para mostrar detalles adicionales
        """
        self.clear()
        self.append_message("=== Árbol de Sintaxis Abstracta (AST) ===\n", QColor("#ffc66d"))
        
        if not ast:
            self.append_message("No se generó el AST.")
            return
        
        # Mostrar estructura del AST
        self._print_ast_node(ast, 0, detailed)
        
        self.append_message("\nEl AST se generó correctamente.")
    
    def _print_ast_node(self, node, level=0, detailed=False):
        """
        Imprime recursivamente un nodo del AST.
        
        Args:
            node (ASTNode): Nodo a imprimir
            level (int): Nivel de indentación
            detailed (bool): True para mostrar detalles adicionales
        """
        indent = "  " * level
        node_type = type(node).__name__
        
        # Información básica del nodo
        node_info = f"{indent}+ {node_type}"
        
        # Añadir atributos específicos según el tipo de nodo
        if hasattr(node, 'name'):
            node_info += f" (name: {node.name})"
        elif hasattr(node, 'value') and node.value is not None:
            node_info += f" (value: {node.value})"
        elif hasattr(node, 'operator'):
            node_info += f" (op: {node.operator})"
        elif hasattr(node, 'var_type'):
            node_info += f" (type: {node.var_type})"
        
        # Posición en el código fuente
        if detailed and hasattr(node, 'line') and node.line is not None:
            node_info += f" [line: {node.line}"
            if hasattr(node, 'column') and node.column is not None:
                node_info += f", col: {node.column}"
            node_info += "]"
        
        # Tipo semántico
        if detailed and hasattr(node, 'type') and node.type is not None:
            node_info += f" {{type: {node.type}}}"
        
        self.append_message(node_info)
        
        # Imprimir hijos
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._print_ast_node(child, level + 1, detailed)
        
        # Imprimir hijos específicos según el tipo de nodo
        if hasattr(node, 'left') and node.left:
            self.append_message(f"{indent}  └─ Left:")
            self._print_ast_node(node.left, level + 2, detailed)
        
        if hasattr(node, 'right') and node.right:
            self.append_message(f"{indent}  └─ Right:")
            self._print_ast_node(node.right, level + 2, detailed)
        
        if hasattr(node, 'condition') and node.condition:
            self.append_message(f"{indent}  └─ Condition:")
            self._print_ast_node(node.condition, level + 2, detailed)
        
        if hasattr(node, 'if_body') and node.if_body:
            self.append_message(f"{indent}  └─ If Body:")
            self._print_ast_node(node.if_body, level + 2, detailed)
        
        if hasattr(node, 'else_body') and node.else_body:
            self.append_message(f"{indent}  └─ Else Body:")
            self._print_ast_node(node.else_body, level + 2, detailed)
        
        if hasattr(node, 'body') and node.body:
            self.append_message(f"{indent}  └─ Body:")
            self._print_ast_node(node.body, level + 2, detailed)
        
        if hasattr(node, 'expression') and node.expression:
            self.append_message(f"{indent}  └─ Expression:")
            self._print_ast_node(node.expression, level + 2, detailed)
        
        if hasattr(node, 'statements') and node.statements:
            for i, stmt in enumerate(node.statements):
                self.append_message(f"{indent}  └─ Statement {i+1}:")
                self._print_ast_node(stmt, level + 2, detailed)