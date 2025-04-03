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
        Maneja la regla: D ::= T L { L.tipo = T.tipo; D.tipo = L.tipo; }
        
        Args:
            decl_node: Nodo de declaración que contiene T (tipo) y L (lista de identificadores)
        """
        # Extraer el tipo (atributo sintético de T)
        var_type = decl_node.var_type  # T.tipo
        
        # Propagar el tipo a los identificadores (atributo heredado para L)
        for child in decl_node.children:
            child.type = var_type  # L.tipo = T.tipo
        
        # El tipo de la declaración es el mismo (atributo sintético de D)
        decl_node.type = var_type  # D.tipo = L.tipo
        
        return var_type
    
    def handle_identifier_list(self, list_node):
        """
        Maneja la regla: L ::= Ld , i { Ld.tipo = L.tipo; i.tipo = L.tipo; insertar(TablaSimbolos, i, L.tipo); }
                           L ::= i { i.tipo = L.tipo; insertar(TablaSimbolos, i, L.tipo); }
        
        Args:
            list_node: Nodo de lista de identificadores
        """
        # Propagar el tipo heredado a todos los identificadores
        inherited_type = list_node.type
        
        for child in list_node.children:
            # Propagar tipo a cada identificador (i.tipo = L.tipo)
            child.type = inherited_type
            
            # Insertar en la tabla de símbolos
            name = child.name
            if self.symbol_table.lookup(name):
                # Error: variable ya declarada
                error = RedeclarationError(name, child.line, child.column)
                self.error_collection.add_error(error)
            else:
                # insertar(TablaSimbolos, i, L.tipo)
                self.symbol_table.insert(
                    name=name,
                    type=inherited_type,
                    line=child.line,
                    column=child.column
                )
        
        return True
    
    def handle_assignment(self, assign_node):
        """
        Maneja la regla: A ::= i = E { si i ∈ TablaSimbolos ∧ i.tipo == E.tipo entonces A.tipo = E.tipo; }
        
        Args:
            assign_node: Nodo de asignación
        """
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
        assign_node.type = expression.type
        
        # Actualizar el valor en la tabla de símbolos si es un valor literal
        if hasattr(expression, 'value') and expression.value is not None:
            self.symbol_table.update(identifier.name, value=expression.value)
        
        return True
    
    def handle_binary_op(self, bin_op_node):
        """
        Maneja las reglas de operaciones aritméticas, relacionales y lógicas
        
        Args:
            bin_op_node: Nodo de operación binaria
        """
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
        Maneja la regla de condicional:
        Condicional ::= si ( E ) { S1 } oNo { S2 } { 
            si E.tipo == bool entonces ejecutar_condicional(E.valor, S1, S2);
            si no, error("La condición del 'si' debe ser booleana."); 
        }
        
        Args:
            if_node: Nodo de condición if
        """
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
        Maneja la regla de bucle while:
        Mientras ::= mientras ( E ) { S } {
            si E.tipo == bool entonces ejecutar_mientras(E, S);
            si no, error("La condición del 'mientras' debe ser booleana.");
        }
        
        Args:
            while_node: Nodo de bucle while
        """
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
        Maneja la regla de bucle repeat:
        Repetir ::= repetir ( num ) { S } {
            si obtener_tipo(num) == entero entonces ejecutar_repetir(num.lexval, S);
            si no, error("El número de repeticiones debe ser entero.");
        }
        
        Args:
            repeat_node: Nodo de bucle repeat
        """
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
        Maneja la regla de impresión:
        Salida ::= sout ( i ) ; {
            si i ∈ TablaSimbolos entonces imprimir(buscar_valor(i));
            si no, error("Variable no declarada.");
        }
        
        Args:
            print_node: Nodo de impresión
        """
        # No necesitamos validación de tipo - cualquier tipo puede imprimirse
        return True
    
    def handle_input(self, input_node):
        """
        Maneja la regla de entrada (scan).
        
        Args:
            input_node: Nodo de entrada
        """
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
        Implementación de la función 'verificar_tipos' mencionada en la gramática atributada.
        
        Args:
            target_type: Tipo de destino
            source_type: Tipo de origen
            
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