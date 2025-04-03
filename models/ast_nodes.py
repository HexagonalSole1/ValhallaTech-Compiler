"""
Definición de nodos para el Árbol de Sintaxis Abstracta (AST)
basado en la gramática atributada del lenguaje personalizado.
"""

class ASTNode:
    """Clase base para todos los nodos del AST."""
    def __init__(self, line=None, column=None):
        self.line = line
        self.column = column
        self.children = []
        # Atributos semánticos comunes
        self.type = None  # Tipo de dato resultante
        self.value = None  # Valor calculado (si es aplicable)
    
    def add_child(self, child):
        """Añade un nodo hijo a este nodo."""
        self.children.append(child)
        return child
    
    def accept(self, visitor):
        """Método para implementar el patrón Visitor."""
        method_name = f'visit_{type(self).__name__}'
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


# Nodos para el programa principal
class ProgramNode(ASTNode):
    """Representa el nodo raíz del programa."""
    def __init__(self, line=None, column=None):
        super().__init__(line, column)


# Nodos para declaraciones
class DeclarationNode(ASTNode):
    """Representa una declaración de variable."""
    def __init__(self, var_type, line=None, column=None):
        super().__init__(line, column)
        self.var_type = var_type  # ent, dec, cadena
        self.type = var_type  # Atributo heredado para propagar el tipo


class IdentifierListNode(ASTNode):
    """Representa una lista de identificadores en una declaración."""
    def __init__(self, line=None, column=None):
        super().__init__(line, column)
        self.identifiers = []  # Lista de nombres de identificadores
        self.type = None  # Atributo heredado para recibir el tipo desde DeclarationNode


class IdentifierNode(ASTNode):
    """Representa un identificador (variable)."""
    def __init__(self, name, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        self.type = None  # Se establecerá durante el análisis semántico


# Nodos para expresiones
class AssignmentNode(ASTNode):
    """Representa una asignación de valor a una variable."""
    def __init__(self, identifier, expression, line=None, column=None):
        super().__init__(line, column)
        self.identifier = identifier  # IdentifierNode
        self.expression = expression  # ExpressionNode


class BinaryOpNode(ASTNode):
    """Representa una operación binaria (suma, resta, etc.)."""
    def __init__(self, operator, left, right, line=None, column=None):
        super().__init__(line, column)
        self.operator = operator  # Tipo de operador (+, -, *, /, etc.)
        self.left = left          # Nodo izquierdo
        self.right = right        # Nodo derecho


class UnaryOpNode(ASTNode):
    """Representa una operación unaria (negación, etc.)."""
    def __init__(self, operator, expression, line=None, column=None):
        super().__init__(line, column)
        self.operator = operator    # Tipo de operador (-, !, etc.)
        self.expression = expression  # Nodo de expresión


class NumberNode(ASTNode):
    """Representa un número literal (entero o flotante)."""
    def __init__(self, value, line=None, column=None):
        super().__init__(line, column)
        self.value = value
        # Determinar tipo automáticamente
        self.type = 'dec' if '.' in str(value) else 'ent'


class StringNode(ASTNode):
    """Representa una cadena literal."""
    def __init__(self, value, line=None, column=None):
        super().__init__(line, column)
        self.value = value
        self.type = 'cadena'


class VariableNode(ASTNode):
    """Representa el uso de una variable."""
    def __init__(self, name, line=None, column=None):
        super().__init__(line, column)
        self.name = name
        # El tipo se asignará durante el análisis semántico
        self.type = None


# Nodos para estructuras de control
class IfNode(ASTNode):
    """Representa una estructura condicional (si-oNo)."""
    def __init__(self, condition, if_body, else_body=None, line=None, column=None):
        super().__init__(line, column)
        self.condition = condition  # Condición
        self.if_body = if_body      # Cuerpo del si
        self.else_body = else_body  # Cuerpo del oNo (opcional)


class WhileNode(ASTNode):
    """Representa un bucle mientras."""
    def __init__(self, condition, body, line=None, column=None):
        super().__init__(line, column)
        self.condition = condition  # Condición
        self.body = body            # Cuerpo del bucle


class RepeatNode(ASTNode):
    """Representa un bucle repetir."""
    def __init__(self, count, body, line=None, column=None):
        super().__init__(line, column)
        self.count = count  # Número de repeticiones
        self.body = body    # Cuerpo del bucle


# Nodos para entrada/salida
class PrintNode(ASTNode):
    """Representa una instrucción de salida (sout)."""
    def __init__(self, expression, line=None, column=None):
        super().__init__(line, column)
        self.expression = expression  # Lo que se va a imprimir


class InputNode(ASTNode):
    """Representa una instrucción de entrada (scan)."""
    def __init__(self, variable, line=None, column=None):
        super().__init__(line, column)
        self.variable = variable  # Variable donde se almacenará la entrada


# Nodos para bloques y secuencias
class BlockNode(ASTNode):
    """Representa un bloque de código entre llaves {}."""
    def __init__(self, statements=None, line=None, column=None):
        super().__init__(line, column)
        self.statements = statements or []  # Lista de instrucciones
    
    def add_statement(self, statement):
        """Añade una instrucción al bloque."""
        self.statements.append(statement)
        return statement