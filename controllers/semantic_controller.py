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
        return node.accept(self)
    
    def generic_visit(self, node):
        """
        Método genérico para visitar un nodo.
        
        Args:
            node (ASTNode): Nodo a visitar
            
        Returns:
            varies: El resultado de visitar el nodo
        """
        for child in node.children:
            self.visit(child)


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
    
    def visit_ProgramNode(self, node):
        """
        Visita el nodo raíz del programa.
        """
        print("Visitando ProgramNode")
        print(f"  Número de hijos: {len(node.children)}")
        
        # Visitar todos los hijos
        for i, child in enumerate(node.children):
            print(f"  Hijo {i}: {type(child).__name__}")
            self.visit(child)
        
        # Verificar si hay errores semánticos
        return not any(isinstance(e, SemanticError) for e in self.error_collection.get_all_errors())
    
    def visit_DeclarationNode(self, node):
        """
        Visita un nodo de declaración.
        """
        print(f"Visitando DeclarationNode con tipo: {node.var_type}")
        print(f"  Número de hijos: {len(node.children)}")
        
        # Propagar el tipo a la lista de identificadores
        for i, child in enumerate(node.children):
            print(f"  Hijo {i}: {type(child).__name__}")
            if isinstance(child, IdentifierListNode):
                print(f"  Propagando tipo {node.var_type} a lista de identificadores")
                child.type = node.var_type
                self.visit(child)
            else:
                print(f"  ADVERTENCIA: Hijo no es IdentifierListNode")
    def visit_IdentifierListNode(self, node):
        """Visita un nodo de lista de identificadores."""
        print(f"Visitando IdentifierListNode")
        print(f"  Tipo heredado: {node.type}")
        print(f"  Identificadores: {node.identifiers if hasattr(node, 'identifiers') else 'ninguno'}")
        print(f"  Número de hijos: {len(node.children)}")
        
        # Insertar cada identificador en la tabla de símbolos
        for child in node.children:
            print(f"  Procesando hijo: {type(child).__name__}")
            if isinstance(child, IdentifierNode):
                print(f"    Nombre identificador: {child.name}")
                child.type = node.type  # Propagar el tipo heredado
                
                # Verificar si ya existe
                if self.symbol_table.lookup(child.name):
                    print(f"    ¡Ya existe! No se inserta")
                    error = RedeclarationError(child.name, child.line, child.column)
                    self.error_collection.add_error(error)
                else:
                    # Insertar en la tabla de símbolos
                    print(f"    Insertando en tabla: {child.name} ({node.type})")
                    self.symbol_table.insert(
                        name=child.name,
                        type=child.type,
                        line=child.line,
                        column=child.column
                    )
    def visit_AssignmentNode(self, node):
        """
        Visita un nodo de asignación.
        
        Args:
            node (AssignmentNode): Nodo a visitar
        """
        # Visitar la expresión para evaluar su tipo
        self.visit(node.expression)
        
        # Buscar la variable en la tabla de símbolos
        var_name = node.identifier.name
        symbol = self.symbol_table.lookup(var_name)
        
        if not symbol:
            # Variable no declarada
            error = UndeclaredError(var_name, node.identifier.line, node.identifier.column)
            self.error_collection.add_error(error)
        else:
            # Verificar compatibilidad de tipos
            var_type = symbol.type
            expr_type = node.expression.type
            
            if not self._are_types_compatible(var_type, expr_type):
                error = TypeError(
                    expected=var_type,
                    found=expr_type,
                    message=f"Incompatible types in assignment: '{var_type}' and '{expr_type}'",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
            else:
                # Actualizar tipo y valor en el nodo
                node.identifier.type = var_type
                
                # Si es una asignación de un valor literal, podemos actualizar el valor
                if isinstance(node.expression, (NumberNode, StringNode)):
                    self.symbol_table.update(var_name, value=node.expression.value)
    
    def visit_BinaryOpNode(self, node):
        """
        Visita un nodo de operación binaria.
        
        Args:
            node (BinaryOpNode): Nodo a visitar
        """
        # Visitar operandos
        self.visit(node.left)
        self.visit(node.right)
        
        # Verificar compatibilidad de tipos según el operador
        left_type = node.left.type
        right_type = node.right.type
        
        # Verificar que los tipos no sean None (por ejemplo, variable no declarada)
        if left_type is None or right_type is None:
            node.type = None
            return
        
        # Operadores aritméticos
        if node.operator in ('+', '-', '*', '/'):
            # Verificar si los tipos son compatibles para operaciones aritméticas
            if left_type == 'ent' and right_type == 'ent':
                node.type = 'ent'
            elif left_type in ('ent', 'dec') and right_type in ('ent', 'dec'):
                node.type = 'dec'
            else:
                error = TypeError(
                    expected="ent or dec",
                    found=f"{left_type} and {right_type}",
                    message=f"Operador '{node.operator}' no puede aplicarse a tipos '{left_type}' y '{right_type}'",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
                node.type = None
        
        # Operadores relacionales
        elif node.operator in ('==', '!=', '>', '<', '>=', '<='):
            # Los tipos deben ser compatibles para comparación
            if (left_type in ('ent', 'dec') and right_type in ('ent', 'dec')) or \
               (left_type == 'cadena' and right_type == 'cadena'):
                node.type = 'bool'
            else:
                error = TypeError(
                    expected="compatible types",
                    found=f"{left_type} and {right_type}",
                    message=f"Operador '{node.operator}' no puede aplicarse a tipos '{left_type}' y '{right_type}'",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
                node.type = None
        
        # Operadores lógicos
        elif node.operator in ('&&', '||'):
            # Ambos operandos deben ser booleanos
            if left_type == 'bool' and right_type == 'bool':
                node.type = 'bool'
            else:
                error = TypeError(
                    expected="bool",
                    found=f"{left_type} and {right_type}",
                    message=f"Operador '{node.operator}' requiere operandos de tipo 'bool'",
                    line=node.line,
                    column=node.column
                )
                self.error_collection.add_error(error)
                node.type = None
    
    def visit_IfNode(self, node):
        """
        Visita un nodo de condición if.
        
        Args:
            node (IfNode): Nodo a visitar
        """
        # Visitar la condición
        self.visit(node.condition)
        
        # Verificar que la condición sea de tipo bool
        condition_type = node.condition.type
        if condition_type != 'bool' and condition_type is not None:
            error = TypeError(
                expected="bool",
                found=condition_type,
                message="La condición del 'si' debe ser de tipo booleano",
                line=node.condition.line,
                column=node.condition.column
            )
            self.error_collection.add_error(error)
        
        # Visitar los bloques
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
        
        Args:
            node (WhileNode): Nodo a visitar
        """
        # Visitar la condición
        self.visit(node.condition)
        
        # Verificar que la condición sea de tipo bool
        condition_type = node.condition.type
        if condition_type != 'bool' and condition_type is not None:
            error = TypeError(
                expected="bool",
                found=condition_type,
                message="La condición del 'mientras' debe ser de tipo booleano",
                line=node.condition.line,
                column=node.condition.column
            )
            self.error_collection.add_error(error)
        
        # Visitar el bloque
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()
    
    def visit_RepeatNode(self, node):
        """
        Visita un nodo de bucle repeat.
        
        Args:
            node (RepeatNode): Nodo a visitar
        """
        # Visitar la expresión de conteo
        self.visit(node.count)
        
        # Verificar que el conteo sea de tipo entero
        count_type = node.count.type
        if count_type != 'ent' and count_type is not None:
            error = TypeError(
                expected="ent",
                found=count_type,
                message="El número de repeticiones debe ser de tipo entero",
                line=node.count.line,
                column=node.count.column
            )
            self.error_collection.add_error(error)
        
        # Visitar el bloque
        self.symbol_table.enter_scope()
        self.visit(node.body)
        self.symbol_table.exit_scope()
    
    def visit_PrintNode(self, node):
        """
        Visita un nodo de impresión.
        
        Args:
            node (PrintNode): Nodo a visitar
        """
        # Visitar la expresión a imprimir
        self.visit(node.expression)
        
        # No se requiere validación de tipos adicional, cualquier tipo puede imprimirse
    
    def visit_InputNode(self, node):
        """
        Visita un nodo de entrada.
        
        Args:
            node (InputNode): Nodo a visitar
        """
        # Verificar que la variable esté declarada
        var_name = node.variable.name
        symbol = self.symbol_table.lookup(var_name)
        
        if not symbol:
            error = UndeclaredError(var_name, node.variable.line, node.variable.column)
            self.error_collection.add_error(error)
        else:
            # Propagar el tipo
            node.variable.type = symbol.type
    
    def visit_BlockNode(self, node):
        """
        Visita un nodo de bloque.
        
        Args:
            node (BlockNode): Nodo a visitar
        """
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
        pass
    
    def visit_StringNode(self, node):
        """
        Visita un nodo de cadena.
        
        Args:
            node (StringNode): Nodo a visitar
        """
        # El tipo ya está establecido durante la construcción del AST
        pass
    
    def visit_VariableNode(self, node):
        """
        Visita un nodo de variable.
        
        Args:
            node (VariableNode): Nodo a visitar
        """
        # Buscar la variable en la tabla de símbolos
        symbol = self.symbol_table.lookup(node.name)
        
        if not symbol:
            error = UndeclaredError(node.name, node.line, node.column)
            self.error_collection.add_error(error)
        else:
            # Propagar el tipo y valor
            node.type = symbol.type
            node.value = symbol.value
    
    def _are_types_compatible(self, target_type, source_type):
        """
        Verifica si dos tipos son compatibles para asignación.
        
        Args:
            target_type (str): Tipo de destino
            source_type (str): Tipo de origen
            
        Returns:
            bool: True si los tipos son compatibles, False en caso contrario
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