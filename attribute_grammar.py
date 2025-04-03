from models.symbol_table import SymbolTable
from models.error import SemanticError, TypeError, UndeclaredError, RedeclarationError

class AttributeHandler:
    """
    Implementación de la gramática atributada para el análisis semántico.
    Esta clase maneja los atributos sintéticos y heredados entre nodos del AST.
    """
    def __init__(self, symbol_table=None, error_collection=None):
        self.symbol_table = symbol_table or SymbolTable()
        self.error_collection = error_collection
        self.current_context = "global"
    
    def handle_declaration(self, decl_node):
        """
        Maneja la regla de declaración, insertando símbolos en la tabla.
        
        Args:
            decl_node (DeclarationNode): Nodo de declaración
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        var_type = decl_node.var_type
        
        # Verificar que el nodo tenga hijos
        if not decl_node.children:
            return False
        
        # Iterar sobre los hijos (lista de identificadores)
        for child in decl_node.children:
            # Verificar que sea un IdentifierListNode
            if hasattr(child, 'identifiers') and child.identifiers:
                # Propagar el tipo a la lista de identificadores
                child.type = var_type
                
                # Simplemente delegar el procesamiento al método de manejo de lista de identificadores
                self.handle_identifier_list(child)
        
        return True
    
    def handle_identifier_list(self, list_node):
        """
        Maneja la regla de lista de identificadores.
        
        Args:
            list_node (IdentifierListNode): Nodo de lista de identificadores
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga tipo
        if not hasattr(list_node, 'type') or not list_node.type:
            return False
        
        inherited_type = list_node.type
        
        # Lista para almacenar identificadores procesados
        processed_ids = []
        
        # Primera pasada: verificar redeclaraciones entre identificadores de la misma lista
        for child in list_node.children:
            if hasattr(child, 'name'):
                name = child.name
                
                # Verificar si este nombre ya fue procesado en esta misma lista
                if name in processed_ids:
                    error = RedeclarationError(name, child.line, child.column)
                    self.error_collection.add_error(error)
                    continue
                
                # Verificar si ya existe en la tabla de símbolos
                if self.symbol_table.lookup(name):
                    error = RedeclarationError(name, child.line, child.column)
                    self.error_collection.add_error(error)
                else:
                    # Propagar el tipo al nodo de identificador
                    child.type = inherited_type
                    
                    # Insertar en la tabla de símbolos
                    self.symbol_table.insert(
                        name=name,
                        type=inherited_type,
                        line=child.line,
                        column=child.column
                    )
                
                # Marcar este identificador como procesado
                processed_ids.append(name)
        
        return True
    
    def handle_assignment(self, assign_node):
        """
        Maneja la regla de asignación.
        
        Args:
            assign_node (AssignmentNode): Nodo de asignación
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga identificador y expresión
        if not hasattr(assign_node, 'identifier') or not hasattr(assign_node, 'expression'):
            return False
        
        identifier = assign_node.identifier
        expression = assign_node.expression
        
        # Verificar si la variable está declarada
        symbol = self.symbol_table.lookup(identifier.name)
        if not symbol:
            error = UndeclaredError(identifier.name, identifier.line, identifier.column)
            self.error_collection.add_error(error)
            return False
        
        # Propagar el tipo del símbolo al identificador
        identifier.type = symbol.type
        
        # Verificar compatibilidad de tipos
        if not expression.type:
            # Si la expresión no tiene tipo, no podemos verificar compatibilidad
            return False
        
        if not self.are_types_compatible(symbol.type, expression.type):
            error = TypeError(
                expected=symbol.type,
                found=expression.type,
                message=f"Tipos incompatibles en asignación: '{symbol.type}' y '{expression.type}'",
                line=assign_node.line,
                column=assign_node.column
            )
            self.error_collection.add_error(error)
            return False
        
        # Si los tipos son compatibles, propagar el tipo a la asignación
        assign_node.type = symbol.type
        
        # Actualizar el valor en la tabla de símbolos si es un valor literal
        if hasattr(expression, 'value') and expression.value is not None:
            self.symbol_table.update(identifier.name, value=expression.value)
        
        return True
    
    def handle_binary_op(self, bin_op_node):
        """
        Maneja las reglas de operaciones binarias.
        
        Args:
            bin_op_node (BinaryOpNode): Nodo de operación binaria
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga operandos y operador
        if not hasattr(bin_op_node, 'left') or not hasattr(bin_op_node, 'right') or not hasattr(bin_op_node, 'operator'):
            return False
        
        # Verificar que ambos operandos tengan tipo
        if not hasattr(bin_op_node.left, 'type') or not hasattr(bin_op_node.right, 'type'):
            return False
        
        left_type = bin_op_node.left.type
        right_type = bin_op_node.right.type
        operator = bin_op_node.operator
        
        # Verificar que ambos operandos tienen tipo válido
        if left_type is None or right_type is None:
            bin_op_node.type = None
            return False
        
        # Operadores aritméticos
        if operator in ('+', '-', '*', '/'):
            if left_type == 'ent' and right_type == 'ent':
                bin_op_node.type = 'ent'
            elif left_type in ('ent', 'dec') and right_type in ('ent', 'dec'):
                bin_op_node.type = 'dec'
            elif operator == '+' and left_type == 'cadena' and right_type == 'cadena':
                bin_op_node.type = 'cadena'  # Concatenación
            else:
                error = TypeError(
                    expected="tipos numéricos compatibles",
                    found=f"{left_type} y {right_type}",
                    message=f"Operador '{operator}' no puede aplicarse a tipos '{left_type}' y '{right_type}'",
                    line=bin_op_node.line,
                    column=bin_op_node.column
                )
                self.error_collection.add_error(error)
                bin_op_node.type = None
                return False
        
        # Operadores relacionales
        elif operator in ('==', '!=', '>', '<', '>=', '<='):
            if (left_type in ('ent', 'dec') and right_type in ('ent', 'dec')) or \
               (left_type == right_type):
                bin_op_node.type = 'bool'
            else:
                error = TypeError(
                    expected="tipos compatibles",
                    found=f"{left_type} y {right_type}",
                    message=f"Operador '{operator}' no puede aplicarse a tipos '{left_type}' y '{right_type}'",
                    line=bin_op_node.line,
                    column=bin_op_node.column
                )
                self.error_collection.add_error(error)
                bin_op_node.type = None
                return False
        
        # Operadores lógicos
        elif operator in ('&&', '||'):
            if left_type == 'bool' and right_type == 'bool':
                bin_op_node.type = 'bool'
            else:
                error = TypeError(
                    expected="bool",
                    found=f"{left_type} y {right_type}",
                    message=f"Operador '{operator}' requiere operandos booleanos",
                    line=bin_op_node.line,
                    column=bin_op_node.column
                )
                self.error_collection.add_error(error)
                bin_op_node.type = None
                return False
        
        # El tipo fue asignado correctamente
        return True
    
    def handle_if_condition(self, if_node):
        """
        Maneja la regla de condicional.
        
        Args:
            if_node (IfNode): Nodo de condición if
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga condición
        if not hasattr(if_node, 'condition') or not hasattr(if_node.condition, 'type'):
            return False
        
        condition_type = if_node.condition.type
        
        # Verificar que la condición sea booleana
        if condition_type != 'bool' and condition_type is not None:
            error = TypeError(
                expected="bool",
                found=condition_type,
                message="La condición del 'si' debe ser booleana",
                line=if_node.condition.line,
                column=if_node.condition.column
            )
            self.error_collection.add_error(error)
            return False
        
        return True
    
    def handle_while_loop(self, while_node):
        """
        Maneja la regla de bucle while.
        
        Args:
            while_node (WhileNode): Nodo de bucle while
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga condición
        if not hasattr(while_node, 'condition') or not hasattr(while_node.condition, 'type'):
            return False
        
        condition_type = while_node.condition.type
        
        # Verificar que la condición sea booleana
        if condition_type != 'bool' and condition_type is not None:
            error = TypeError(
                expected="bool",
                found=condition_type,
                message="La condición del 'mientras' debe ser booleana",
                line=while_node.condition.line,
                column=while_node.condition.column
            )
            self.error_collection.add_error(error)
            return False
        
        return True
    
    def handle_repeat_loop(self, repeat_node):
        """
        Maneja la regla de bucle repeat.
        
        Args:
            repeat_node (RepeatNode): Nodo de bucle repeat
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga contador
        if not hasattr(repeat_node, 'count') or not hasattr(repeat_node.count, 'type'):
            return False
        
        count_type = repeat_node.count.type
        
        # Verificar que el contador sea entero
        if count_type != 'ent' and count_type is not None:
            error = TypeError(
                expected="ent",
                found=count_type,
                message="El número de repeticiones debe ser entero",
                line=repeat_node.count.line,
                column=repeat_node.count.column
            )
            self.error_collection.add_error(error)
            return False
        
        return True
    
    def handle_print(self, print_node):
        """
        Maneja la regla de impresión.
        
        Args:
            print_node (PrintNode): Nodo de impresión
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # No necesitamos validación de tipo - cualquier tipo puede imprimirse
        return True
    
    def handle_input(self, input_node):
        """
        Maneja la regla de entrada (scan).
        
        Args:
            input_node (InputNode): Nodo de entrada
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        # Verificar que el nodo tenga variable
        if not hasattr(input_node, 'variable') or not hasattr(input_node.variable, 'name'):
            return False
        
        var_name = input_node.variable.name
        symbol = self.symbol_table.lookup(var_name)
        
        if not symbol:
            error = UndeclaredError(var_name, input_node.variable.line, input_node.variable.column)
            self.error_collection.add_error(error)
            return False
        
        # Propagar el tipo
        input_node.variable.type = symbol.type
        return True
    
    def are_types_compatible(self, target_type, source_type):
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
        
        # Concatenación de cadenas (para casos especiales)
        if target_type == 'cadena' and source_type == 'cadena':
            return True
        
        return False