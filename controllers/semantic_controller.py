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
            node (ASTNode o Tree): Nodo a visitar
            
        Returns:
            varies: El resultado de visitar el nodo
        """
        import lark
        
        # Verificar si es un objeto Tree de Lark
        if isinstance(node, lark.Tree):
            print(f"Advertencia: Se encontró un nodo Tree de Lark de tipo '{node.data}'")
            # Procesar hijos
            for child in node.children:
                self.visit(child)
            return None
        
        # Manejo regular para nodos AST
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
        # Forzar la creación de una nueva tabla de símbolos para cada visitor
        self.symbol_table = symbol_table or SymbolTable()
        self.error_collection = error_collection or ErrorCollection()
        
        # Variables internas para seguimiento - usado para depuración
        self._declared_variables = []
    
    def visit_ProgramNode(self, node):
        """
        Visita el nodo raíz del programa.
        """
        print("Visitando ProgramNode")
        print(f"  Número de hijos: {len(node.children)}")
        
        # Limpiar cualquier estado residual
        self._declared_variables.clear()
        
        # Visitar todos los hijos en orden
        for i, child in enumerate(node.children):
            print(f"  Visitando hijo {i} ({type(child).__name__})")
            self.visit(child)
        
        # Verificar si hay errores semánticos
        return not any(isinstance(e, SemanticError) for e in self.error_collection.get_all_errors())
    
    def visit_DeclarationNode(self, node):
        """
        Visita un nodo de declaración.
        """
        print(f"Visitando DeclarationNode con tipo: {node.var_type}")
        print(f"  Número de hijos: {len(node.children)}")
        
        var_type = node.var_type
        
        # Verificar que el nodo tenga hijos
        if not node.children:
            return False
        
        # Iterar sobre los hijos (lista de identificadores)
        for child in node.children:
            # Verificar que sea un IdentifierListNode
            if hasattr(child, 'identifiers') and child.identifiers:
                # Propagar el tipo a la lista de identificadores
                child.type = var_type
                
                # Procesar cada identificador en la lista
                for id_node in child.children:
                    if hasattr(id_node, 'name'):
                        # Comprobar si la variable ya está declarada en este análisis
                        if id_node.name in self._declared_variables:
                            error = RedeclarationError(
                                id_node.name, 
                                line=id_node.line,
                                column=id_node.column
                            )
                            self.error_collection.add_error(error)
                        else:
                            # Propagar el tipo al nodo de identificador
                            id_node.type = var_type
                            
                            # Insertar en la tabla de símbolos
                            self.symbol_table.insert(
                                name=id_node.name,
                                type=var_type,
                                line=id_node.line,
                                column=id_node.column
                            )
                            
                            # Registrar como declarada en este análisis
                            self._declared_variables.append(id_node.name)
        
        # Continuar visitando los hijos
        for child in node.children:
            self.visit(child)
    
    def visit_IdentifierListNode(self, node):
        """
        Visita un nodo de lista de identificadores.
        """
        print(f"Visitando IdentifierListNode")
        print(f"  Tipo heredado: {node.type}")
        
        # El procesamiento ya se hizo en visit_DeclarationNode
        # Solo para depuración
        if hasattr(node, 'identifiers'):
            print(f"  Identificadores en la lista: {node.identifiers}")
    
    def visit_AssignmentNode(self, node):
        """
        Visita un nodo de asignación.
        """
        print(f"Visitando AssignmentNode: {node.identifier.name if hasattr(node.identifier, 'name') else '?'}")
        
        # Primero visitar la expresión para evaluar su tipo
        self.visit(node.expression)
        
        # Luego visitar el identificador
        self.visit(node.identifier)
        
        # Verificar si la variable está declarada
        identifier = node.identifier
        symbol = self.symbol_table.lookup(identifier.name)
        
        if not symbol:
            error = UndeclaredError(identifier.name, identifier.line, identifier.column)
            self.error_collection.add_error(error)
            return False
        
        # Propagar el tipo del símbolo al identificador
        identifier.type = symbol.type
        
        # Verificar compatibilidad de tipos
        expression = node.expression
        if not expression.type:
            return False
        
        if not self.are_types_compatible(symbol.type, expression.type):
            error = TypeError(
                expected=symbol.type,
                found=expression.type,
                message=f"Tipos incompatibles en asignación: '{symbol.type}' y '{expression.type}'",
                line=node.line,
                column=node.column
            )
            self.error_collection.add_error(error)
            return False
        
        # Si los tipos son compatibles, propagar el tipo a la asignación
        node.type = symbol.type
        
        # Actualizar el valor en la tabla de símbolos si es un valor literal
        if hasattr(expression, 'value') and expression.value is not None:
            self.symbol_table.update(identifier.name, value=expression.value)
        
        return True
    
    def visit_BinaryOpNode(self, node):
        """
        Visita un nodo de operación binaria.
        """
        print(f"Visitando BinaryOpNode con operador: {node.operator}")
        
        # Visitar operandos para obtener sus tipos
        self.visit(node.left)
        self.visit(node.right)
        
        left_type = node.left.type
        right_type = node.right.type
        operator = node.operator
        
        # Verificar que ambos operandos tienen tipo válido
        if left_type is None or right_type is None:
            node.type = None
            return False
        
        # Operadores aritméticos
        if operator in ('+', '-', '*', '/'):
            if left_type == 'ent' and right_type == 'ent':
                node.type = 'ent'
            elif left_type in ('ent', 'dec') and right_type in ('ent', 'dec'):
                node.type = 'dec'
            elif operator == '+' and left_type == 'cadena' and right_type == 'cadena':
                node.type = 'cadena'  # Concatenación
            else:
                error = TypeError(
                    expected="tipos numéricos compatibles",
                    found=f"{left_type} y {right_type}",
                    message=f"Operador '{operator}' no puede aplicarse a tipos '{left_type}' y '{right_type}'",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
                node.type = None
                return False
        
        # Operadores relacionales
        elif operator in ('==', '!=', '>', '<', '>=', '<='):
            if (left_type in ('ent', 'dec') and right_type in ('ent', 'dec')) or \
               (left_type == right_type):
                node.type = 'bool'
            else:
                error = TypeError(
                    expected="tipos compatibles",
                    found=f"{left_type} y {right_type}",
                    message=f"Operador '{operator}' no puede aplicarse a tipos '{left_type}' y '{right_type}'",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
                node.type = None
                return False
        
        # Operadores lógicos
        elif operator in ('&&', '||'):
            if left_type == 'bool' and right_type == 'bool':
                node.type = 'bool'
            else:
                error = TypeError(
                    expected="bool",
                    found=f"{left_type} y {right_type}",
                    message=f"Operador '{operator}' requiere operandos booleanos",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
                node.type = None
                return False
        
        return True
    
    def visit_IfNode(self, node):
        """
        Visita un nodo de condición if.
        """
        print(f"Visitando IfNode")
        
        # Visitar la condición
        self.visit(node.condition)
        
        condition_type = node.condition.type
        
        # Verificar que la condición sea booleana
        if condition_type != 'bool' and condition_type is not None:
            error = TypeError(
                expected="bool",
                found=condition_type,
                message="La condición del 'si' debe ser booleana",
                line=node.condition.line,
                column=node.condition.column
            )
            self.error_collection.add_error(error)
            return False
        
        # Visitar los bloques con nuevos ámbitos
        self.symbol_table.enter_scope()
        self.visit(node.if_body)
        self.symbol_table.exit_scope()
        
        if node.else_body:
            self.symbol_table.enter_scope()
            self.visit(node.else_body)
            self.symbol_table.exit_scope()
        
        return True
    
    def visit_WhileNode(self, node):
        """
        Visita un nodo de bucle while.
        """
        print(f"Visitando WhileNode")
        
        # Visitar la condición
        self.visit(node.condition)
        
        condition_type = node.condition.type
        
        # Verificar que la condición sea booleana
        if condition_type != 'bool' and condition_type is not None:
            error = TypeError(
                expected="bool",
                found=condition_type,
                message="La condición del 'mientras' debe ser booleana",
                line=node.condition.line,
                column=node.condition.column
            )
            self.error_collection.add_error(error)
            return False
        
        # Visitar el bloque con nuevo ámbito
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()
        
        return True
    
    def visit_RepeatNode(self, node):
        """
        Visita un nodo de bucle repeat.
        """
        print(f"Visitando RepeatNode")
        
        # Visitar la expresión de conteo
        self.visit(node.count)
        
        count_type = node.count.type
        
        # Verificar que el contador sea entero
        if count_type != 'ent' and count_type is not None:
            error = TypeError(
                expected="ent",
                found=count_type,
                message="El número de repeticiones debe ser entero",
                line=node.count.line,
                column=node.count.column
            )
            self.error_collection.add_error(error)
            return False
        
        # Visitar el bloque con nuevo ámbito
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()
        
        return True
    
    def visit_PrintNode(self, node):
        """
        Visita un nodo de impresión.
        """
        print(f"Visitando PrintNode")
        
        # Visitar la expresión a imprimir
        self.visit(node.expression)
        
        return True
    
    def visit_InputNode(self, node):
        """
        Visita un nodo de entrada.
        """
        print(f"Visitando InputNode")
        
        var_name = node.variable.name
        symbol = self.symbol_table.lookup(var_name)
        
        if not symbol:
            error = UndeclaredError(var_name, node.variable.line, node.variable.column)
            self.error_collection.add_error(error)
            return False
        
        # Propagar el tipo
        node.variable.type = symbol.type
        return True
    
    def visit_BlockNode(self, node):
        """
        Visita un nodo de bloque.
        """
        print(f"Visitando BlockNode con {len(node.statements)} instrucciones")
        
        # Visitar todas las instrucciones del bloque
        for statement in node.statements:
            self.visit(statement)
        
        return True
    
    def visit_NumberNode(self, node):
        """
        Visita un nodo de número.
        """
        # El tipo ya está establecido durante la construcción del AST
        print(f"Visitando NumberNode: {node.value} de tipo {node.type}")
        return True
    
    def visit_StringNode(self, node):
        """
        Visita un nodo de cadena.
        """
        # El tipo ya está establecido durante la construcción del AST
        print(f"Visitando StringNode: {node.value} de tipo {node.type}")
        return True
    
    def visit_VariableNode(self, node):
        """
        Visita un nodo de variable.
        """
        print(f"Visitando VariableNode: {node.name}")
        
        # Buscar la variable en la tabla de símbolos
        symbol = self.symbol_table.lookup(node.name)
        
        if not symbol:
            error = UndeclaredError(node.name, node.line, node.column)
            self.error_collection.add_error(error)
            return False
        else:
            # Propagar el tipo y valor
            node.type = symbol.type
            node.value = symbol.value
            print(f"  Asignado tipo {node.type} a variable {node.name}")
            return True
    
    def are_types_compatible(self, target_type, source_type):
        """
        Verifica si dos tipos son compatibles para asignación.
        """
        if target_type is None or source_type is None:
            return False
        
        # Mismo tipo
        if target_type == source_type:
            return True
        
        # Conversiones permitidas
        if target_type == 'dec' and source_type == 'ent':
            return True
        
        return False


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
        self.visitor = None  # Lo crearemos nuevo en cada análisis
    
    def analyze(self, ast):
        """
        Realiza el análisis semántico del AST.
        """
        if ast is None:
            print("Error: AST es None")
            return False
        
        print(f"Iniciando análisis semántico. Tipo de AST: {type(ast).__name__}")
        
        # Limpiar errores semánticos
        self.error_collection.semantic_errors.clear()
        
        # Crear una nueva tabla de símbolos y un nuevo visitor cada vez
        self.symbol_table = SymbolTable()
        self.visitor = SemanticVisitor(self.symbol_table, self.error_collection)
        
        # Ejecutar el análisis semántico
        result = self.visitor.visit(ast)
        
        # Para depuración
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