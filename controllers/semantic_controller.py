from models.symbol_table import SymbolTable
from models.ast_nodes import *
from models.error import SemanticError, TypeError, UndeclaredError, RedeclarationError, ErrorCollection

class ASTVisitor:
    """
    Clase base para implementar el patrón Visitor para recorrer el AST.
    """
    def visit(self, node):
        """
        Visita un nodo del AST.
        
        Args:
            node (ASTNode): Nodo a visitar
            
        Returns:
            varies: El resultado de visitar el nodo
        """
        if hasattr(node, 'accept'):
            return node.accept(self)
        else:
            print(f"Warning: Node {type(node).__name__} does not have 'accept' method")
            return self.generic_visit(node)
    
    def generic_visit(self, node):
        """
        Método genérico para visitar un nodo.
        
        Args:
            node (ASTNode): Nodo a visitar
            
        Returns:
            varies: El resultado de visitar el nodo
        """
        if hasattr(node, 'children'):
            for child in node.children:
                self.visit(child)
        return None


class SemanticVisitor(ASTVisitor):
    """
    Visitor para realizar el análisis semántico.
    """
    def __init__(self, symbol_table=None, error_collection=None):
        """
        Inicializa el visitor semántico.
        
        Args:
            symbol_table (SymbolTable, optional): Tabla de símbolos
            error_collection (ErrorCollection, optional): Colección para almacenar errores
        """
        self.symbol_table = symbol_table or SymbolTable()
        self.error_collection = error_collection or ErrorCollection()
        
        # Usar el manejador de atributos para la gramática atributada
        from attribute_grammar import AttributeHandler
        self.attr_handler = AttributeHandler(self.symbol_table, self.error_collection)
    
    def visit_ProgramNode(self, node):
        """
        Visita el nodo raíz del programa.
        """
        print("Visitando ProgramNode")
        print(f"  Número de hijos: {len(node.children)}")
        
        # Visitar todos los hijos en orden
        for i, child in enumerate(node.children):
            print(f"  Visitando hijo {i} ({type(child).__name__})")
            self.visit(child)
        
        # Verificar si hay errores semánticos
        return not any(isinstance(e, SemanticError) for e in self.error_collection.get_all_errors())
    
    def visit_DeclarationNode(self, node):
        """
        Visita un nodo de declaración.
        Aplica la regla: D ::= T L { L.tipo = T.tipo; D.tipo = L.tipo; }
        """
        print(f"Visitando DeclarationNode con tipo: {node.var_type}")
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_declaration(node)
        
        # Visitar hijos para propagar los atributos
        for child in node.children:
            self.visit(child)
    
    def visit_IdentifierListNode(self, node):
        """
        Visita un nodo de lista de identificadores.
        Aplica la regla: L ::= i { i.tipo = L.tipo; insertar(TablaSimbolos, i, L.tipo); }
        """
        print(f"Visitando IdentifierListNode")
        print(f"  Tipo heredado: {node.type}")
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_identifier_list(node)
        
        # No es necesario visitar los identificadores aquí, ya fueron procesados
    
    def visit_AssignmentNode(self, node):
        """
        Visita un nodo de asignación.
        Aplica la regla: A ::= i = E { si i ∈ TablaSimbolos ∧ i.tipo == E.tipo entonces A.tipo = E.tipo; }
        
        Args:
            node (AssignmentNode): Nodo a visitar
        """
        print(f"Visitando AssignmentNode: {node.identifier.name if hasattr(node.identifier, 'name') else '?'}")
        
        # Primero visitar la expresión para evaluar su tipo
        self.visit(node.expression)
        
        # Luego visitar el identificador
        self.visit(node.identifier)
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_assignment(node)
    
    def visit_BinaryOpNode(self, node):
        """
        Visita un nodo de operación binaria.
        Aplica las reglas para operaciones según el operador.
        
        Args:
            node (BinaryOpNode): Nodo a visitar
        """
        print(f"Visitando BinaryOpNode con operador: {node.operator}")
        
        # Visitar operandos para obtener sus tipos
        self.visit(node.left)
        self.visit(node.right)
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_binary_op(node)
    
    def visit_IfNode(self, node):
        """
        Visita un nodo de condición if.
        Aplica la regla para verificar que la condición sea booleana.
        
        Args:
            node (IfNode): Nodo a visitar
        """
        print(f"Visitando IfNode")
        
        # Visitar la condición
        self.visit(node.condition)
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_if_condition(node)
        
        # Visitar los bloques con nuevos ámbitos
        self.symbol_table.enter_scope()
        self.visit(node.if_body)
        self.symbol_table.exit_scope()
        
        if node.else_body:
            self.symbol_table.enter_scope()
            self.visit(node.else_body)
            self.symbol_table.exit_scope()
    
    def visit_WhileNode(self, node):
        """
        Visita un nodo de bucle while.
        Aplica la regla para verificar que la condición sea booleana.
        
        Args:
            node (WhileNode): Nodo a visitar
        """
        print(f"Visitando WhileNode")
        
        # Visitar la condición
        self.visit(node.condition)
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_while_loop(node)
        
        # Visitar el bloque con nuevo ámbito
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()
    
    def visit_RepeatNode(self, node):
        """
        Visita un nodo de bucle repeat.
        Aplica la regla para verificar que el contador sea entero.
        
        Args:
            node (RepeatNode): Nodo a visitar
        """
        print(f"Visitando RepeatNode")
        
        # Visitar la expresión de conteo
        self.visit(node.count)
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_repeat_loop(node)
        
        # Visitar el bloque con nuevo ámbito
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()
    
    def visit_PrintNode(self, node):
        """
        Visita un nodo de impresión.
        
        Args:
            node (PrintNode): Nodo a visitar
        """
        print(f"Visitando PrintNode")
        
        # Visitar la expresión a imprimir
        self.visit(node.expression)
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_print(node)
    
    def visit_InputNode(self, node):
        """
        Visita un nodo de entrada.
        
        Args:
            node (InputNode): Nodo a visitar
        """
        print(f"Visitando InputNode")
        
        # Aplicar regla de la gramática atributada
        self.attr_handler.handle_input(node)
    
    def visit_BlockNode(self, node):
        """
        Visita un nodo de bloque.
        
        Args:
            node (BlockNode): Nodo a visitar
        """
        print(f"Visitando BlockNode con {len(node.statements)} instrucciones")
        
        # Visitar todas las instrucciones del bloque
        for statement in node.statements:
            self.visit(statement)
    
    def visit_NumberNode(self, node):
        """
        Visita un nodo de número.
        
        Args:
            node (NumberNode): Nodo a visitar
        """
        # El tipo ya está establecido durante la construcción del AST
        print(f"Visitando NumberNode: {node.value} de tipo {node.type}")
    
    def visit_StringNode(self, node):
        """
        Visita un nodo de cadena.
        
        Args:
            node (StringNode): Nodo a visitar
        """
        # El tipo ya está establecido durante la construcción del AST
        print(f"Visitando StringNode: {node.value} de tipo {node.type}")
    
    def visit_VariableNode(self, node):
        """
        Visita un nodo de variable.
        
        Args:
            node (VariableNode): Nodo a visitar
        """
        print(f"Visitando VariableNode: {node.name}")
        
        # Buscar la variable en la tabla de símbolos
        symbol = self.symbol_table.lookup(node.name)
        
        if not symbol:
            error = UndeclaredError(node.name, node.line, node.column)
            self.error_collection.add_error(error)
        else:
            # Propagar el tipo y valor
            node.type = symbol.type
            node.value = symbol.value
            print(f"  Asignado tipo {node.type} a variable {node.name}")


class SemanticController:
    """
    Controlador para el análisis semántico.
    """
    def __init__(self, error_collection=None):
        """
        Inicializa el controlador del analizador semántico.
        
        Args:
            error_collection (ErrorCollection, optional): Colección para almacenar errores
        """
        self.error_collection = error_collection or ErrorCollection()
        self.symbol_table = SymbolTable()
        self.visitor = SemanticVisitor(self.symbol_table, self.error_collection)
    
    def analyze(self, ast):
        """
        Realiza el análisis semántico del AST.
        """
        if ast is None:
            print("Error: AST es None")
            return False
        
        print(f"Iniciando análisis semántico. Tipo de AST: {type(ast).__name__}")
        
        # Reiniciar la tabla de símbolos
        self.symbol_table = SymbolTable()
        self.visitor.symbol_table = self.symbol_table
        
        # Ejecutar el análisis semántico
        result = self.visitor.visit(ast)
        
        print(f"Análisis semántico completado. Resultado: {result}")
        print(f"Símbolos encontrados: {len(self.symbol_table.get_all_symbols())}")
        for symbol in self.symbol_table.get_all_symbols():
            print(f"  - {symbol.name} ({symbol.type})")
        
        return result
    
    def get_symbol_table(self):
        """
        Obtiene la tabla de símbolos.
        
        Returns:
            SymbolTable: La tabla de símbolos
        """
        return self.symbol_table
    
    def has_errors(self):
        """
        Comprueba si se produjeron errores durante el análisis semántico.
        
        Returns:
            bool: True si hay errores, False en caso contrario
        """
        return any(isinstance(e, SemanticError) for e in self.error_collection.get_all_errors())