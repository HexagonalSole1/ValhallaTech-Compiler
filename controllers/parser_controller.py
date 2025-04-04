from lark import Lark, Transformer, v_args
import os
from models.ast_nodes import *
from models.error import SyntaxError, ErrorCollection

class ASTBuilder(Transformer):
    """
    Transformador de Lark para construir el AST a partir del árbol de análisis.
    """
    
    @v_args(inline=True)
    def start(self, programa):
        """
        Método para manejar el nodo raíz de la gramática.
        """
        # Solo debería recibir un nodo programa
        return programa
    
    @v_args(inline=True)
    def programa(self, *statements):
        """
        Procesar los elementos del programa.
        """
        programa_node = ProgramNode()
        
        # Agregar cada declaración o sentencia como hijo del programa
        for statement in statements:
            if statement:  # Ignorar None
                programa_node.add_child(statement)
        
        return programa_node
    
    @v_args(inline=True)
    def declaracion(self, tipo, identificador_lista):
        """
        Crear nodo de declaración con tipo y lista de identificadores.
        """
        node = DeclarationNode(tipo)
        node.add_child(identificador_lista)
        return node
    
    @v_args(inline=True)
    def tipo_entero(self):
        return "ent"
    
    @v_args(inline=True)
    def tipo_decimal(self):
        return "dec"
    
    @v_args(inline=True)
    def tipo_cadena(self):
        return "cadena"
    
    @v_args(inline=True)
    def identificador_lista(self, *identificadores):
        """
        Crear lista de identificadores.
        """
        node = IdentifierListNode()
        node.identifiers = []
        
        for identificador in identificadores:
            if isinstance(identificador, IdentifierNode):
                node.identifiers.append(identificador.name)
                node.add_child(identificador)
        
        return node

    @v_args(inline=True)
    def expr_suma(self, left, right):
        print(f"DEBUG - Creando SUMA explícita: {left} + {right}")
        return BinaryOpNode("+", left, right)

    @v_args(inline=True)
    def expr_resta(self, left, right):
        print(f"DEBUG - Creando RESTA explícita: {left} - {right}")
        return BinaryOpNode("-", left, right)    
        
    @v_args(inline=True)
    def expr_mult(self, left, right):
        print(f"DEBUG - Creando multi explícita: {left} + {right}")
        return BinaryOpNode("*", left, right)

    @v_args(inline=True)
    def expr_division(self, left, right):
        print(f"DEBUG - Creando division explícita: {left} - {right}")
        return BinaryOpNode("/", left, right)   
    
    @v_args(inline=True)
    def identificador(self, id_token):
        """
        Crear nodo de identificador.
        """
        return IdentifierNode(id_token.value, id_token.line, id_token.column)
    
    @v_args(inline=True)
    def asignacion(self, variable, expresion):
        """
        Crear nodo de asignación.
        """
        return AssignmentNode(variable, expresion)
    
    @v_args(inline=True)
    def condicional(self, condicion, bloque_if, bloque_else=None):
        """
        Crear nodo de condicional.
        """
        return IfNode(condicion, bloque_if, bloque_else)
    
    @v_args(inline=True)
    def bucle_mientras(self, condicion, bloque):
        """
        Crear nodo de bucle mientras.
        """
        return WhileNode(condicion, bloque)
    
    @v_args(inline=True)
    def bucle_repetir(self, count, bloque):
        """
        Crear nodo de bucle repetir.
        """
        return RepeatNode(count, bloque)
    
    @v_args(inline=True)
    def impresion(self, expr):
        """
        Crear nodo de impresión.
        """
        return PrintNode(expr)
    
    @v_args(inline=True)
    def entrada(self, variable):
        """
        Crear nodo de entrada.
        """
        return InputNode(variable)
    
    @v_args(inline=True)
    def bloque(self, *statements):
        """
        Crear nodo de bloque.
        """
        node = BlockNode()
        for statement in statements:
            if statement:  # Ignorar None
                node.add_statement(statement)
        return node
    
    @v_args(inline=True)
    def expr_logica(self, expr, *args):
        """
        Crear nodo de expresión lógica.
        """
        if not args:
            return expr
        
        result = expr
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                operator = args[i].value if hasattr(args[i], 'value') else args[i]
                right_expr = args[i+1]
                result = BinaryOpNode(operator, result, right_expr)
        
        return result
    
    @v_args(inline=True)
    def expr_relacional(self, expr, *args):
        print(f"DEBUG expr_relacional: expr={expr}, args={args}")
        
        if not args:
            return expr
        
        # Caso especial para cuando tenemos dos operandos sin operador explícito
        if len(args) == 1 and hasattr(args[0], 'name'):
            # Estamos ante un caso como 'x > y' donde falta el operador
            print(f"Caso especial: creando BinaryOpNode para comparación de {expr.name if hasattr(expr, 'name') else expr} > {args[0].name if hasattr(args[0], 'name') else args[0]}")
            # Asumimos '>' como operador por defecto (ajusta según sea necesario)
            result = BinaryOpNode('>', expr, args[0])
            # Establecer el tipo explícitamente como bool
            result.type = 'bool'
            return result
        
        # Código original para el caso normal
        result = expr
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                operator = args[i]
                if hasattr(operator, 'value'):
                    operator = operator.value
                right_expr = args[i+1]
                print(f"Creando BinaryOpNode: {result} {operator} {right_expr}")
                result = BinaryOpNode(operator, result, right_expr)
                # Establecer tipo bool para operadores relacionales
                if operator in ('==', '!=', '>', '<', '>=', '<='):
                    result.type = 'bool'
        
        return result
    
    @v_args(inline=True)
    def expr_aritmetica(self, term, *args):
        """
        Crear nodo de expresión aritmética.
        """
        if not args:
            return term
        
        result = term
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                operator = args[i].value if hasattr(args[i], 'value') else args[i]
                right_term = args[i+1]
                result = BinaryOpNode(operator, result, right_term)
        
        return result
    
    @v_args(inline=True)
    def termino(self, factor, *args):
        """
        Crear nodo de término.
        """
        if not args:
            return factor
        
        result = factor
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                operator = args[i].value if hasattr(args[i], 'value') else args[i]
                right_factor = args[i+1]
                result = BinaryOpNode(operator, result, right_factor)
        
        return result

    @v_args(inline=True)
    def op_igual(self, left, right):
        node = BinaryOpNode("==", left, right)
        node.type = "bool"
        return node

    @v_args(inline=True)
    def op_distinto(self, left, right):
        node = BinaryOpNode("!=", left, right)
        node.type = "bool"
        return node

    @v_args(inline=True)
    def op_mayor(self, left, right):
        node = BinaryOpNode(">", left, right)
        node.type = "bool"
        return node

    @v_args(inline=True)
    def op_menor(self, left, right):
        node = BinaryOpNode("<", left, right)
        node.type = "bool"
        return node

    @v_args(inline=True)
    def op_mayor_igual(self, left, right):
        node = BinaryOpNode(">=", left, right)
        node.type = "bool"
        return node

    @v_args(inline=True)
    def op_menor_igual(self, left, right):
        node = BinaryOpNode("<=", left, right)
        node.type = "bool"
        return node
    @v_args(inline=True)
    def factor(self, value):
        """
        Manejar factor (paréntesis, número, variable, etc.)
        """
        return value
    
    @v_args(inline=True)
    def operador_logico(self, op):
        """
        Extraer operador lógico.
        """
        return op.value if hasattr(op, 'value') else str(op)
    
    @v_args(inline=True)
    def operador_relacional(self, op):
        """
        Extraer operador relacional.
        """
        return op.value if hasattr(op, 'value') else str(op)
    
# Este fragmento es para el ASTBuilder en parser_controller.py

    @v_args(inline=True)
    def operador_suma(self, op):
        """
        Extraer operador de suma o resta.
        """
        if op is None:
            return "+"  # Valor por defecto
        
        # Obtener el valor real del operador
        if hasattr(op, 'value'):
            result = op.value
        else:
            result = str(op)
        
        print(f"DEBUG - Operador extraído: '{result}' - Tipo: {type(op)}")
        return result
    
    
    @v_args(inline=True)
    def operador_mult(self, op=None):
        """
        Extraer operador de multiplicación o división.
        """
        print(f"DEBUG - Procesando operador_mult: {op}")
        
        # Si no se proporciona operador, usar * por defecto
        if op is None:
            print(f"DEBUG - No se proporcionó operador, usando '*' por defecto")
            return "*"
        
        # Si el operador es un Tree, intentar extraer su valor
        import lark
        if isinstance(op, lark.Tree):
            # Comprobar si hay un Token en el Tree que podamos usar
            if op.children and hasattr(op.children[0], 'value'):
                operator_value = op.children[0].value
                print(f"DEBUG - Extrayendo valor del hijo del Tree: {operator_value}")
                return operator_value
            else:
                # Si no encontramos valor, usamos el data del Tree para determinar el operador
                print(f"DEBUG - Usando data del Tree: {op.data}")
                if op.data == 'operador_mult':
                    return "*" 
                elif op.data == 'expr_division' or op.data == 'operador_div' or "div" in op.data:
                    return "/"
        
        # Si es un Token o tiene un atributo value
        if hasattr(op, 'value'):
            # Verificar explícitamente si es un operador de división
            value = op.value
            if value == '/':
                print(f"DEBUG - Encontrado operador de división explícito: {value}")
                return "/"
            return value
        
        # Si es una cadena directamente
        if isinstance(op, str):
            # Verificar explícitamente si es un operador de división
            if op == '/':
                print(f"DEBUG - Encontrado operador de división como cadena: {op}")
                return "/"
            return op
        
        # Si todo falla, asumimos "*" por defecto
        print(f"DEBUG - No se pudo extraer operador, usando '*' por defecto")
        return "*"
    @v_args(inline=True)
    def expr_aritmetica(self, term, *args):
        """
        Crear nodo de expresión aritmética.
        """
        if not args:
            return term
        
        result = term
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                # Obtener el operador real (+ o -)
                if hasattr(args[i], 'value'):
                    operator = args[i].value
                else:
                    operator = str(args[i])
                
                right_term = args[i+1]
                
                # Verificación detallada para operadores
                print(f"DEBUG - Operador en expr_aritmetica: '{operator}' - Tipo: {type(operator)}")
                
                # Crear el nodo binario con el operador correcto
                binary_node = BinaryOpNode(operator, result, right_term)
                
                # Verificación extra
                if operator == '-':
                    print(f"DEBUG - Creando operación de RESTA: {result} - {right_term}")
                elif operator == '+':
                    print(f"DEBUG - Creando operación de SUMA: {result} + {right_term}")
                
                result = binary_node
        
        return result
    
    # Implementación completa para term y operador_mult también
    @v_args(inline=True)
    def termino(self, factor, *args):
        """
        Crear nodo de término.
        """
        if not args:
            return factor
        
        result = factor
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                # Obtener el operador real (* o /)
                if hasattr(args[i], 'value'):
                    operator = args[i].value
                else:
                    operator = str(args[i])
                
                right_factor = args[i+1]
                
                # Verificación detallada
                print(f"DEBUG - Operador en termino: '{operator}' - Tipo: {type(operator)}")
                
                # Crear nodo con el operador correcto
                binary_node = BinaryOpNode(operator, result, right_factor)
                
                # Verificación extra
                if operator == '*':
                    print(f"DEBUG - Creando operación de MULTIPLICACIÓN: {result} * {right_factor}")
                elif operator == '/':
                    print(f"DEBUG - Creando operación de DIVISIÓN: {result} / {right_factor}")
                
                result = binary_node
        
        return result

    
    @v_args(inline=True)
    def variable(self, var_token):
        """
        Crear nodo de variable.
        """
        return VariableNode(var_token.value, var_token.line, var_token.column)
    
    @v_args(inline=True)
    def entero(self, num_token):
        """
        Crear nodo de número entero.
        """
        return NumberNode(int(num_token.value), num_token.line, num_token.column)
    
    @v_args(inline=True)
    def decimal(self, num_token):
        """
        Crear nodo de número decimal.
        """
        return NumberNode(float(num_token.value), num_token.line, num_token.column)
    
    @v_args(inline=True)
    def string(self, str_token):
        """
        Crear nodo de cadena.
        """
        # Eliminar comillas
        value = str_token.value[1:-1]
        return StringNode(value, str_token.line, str_token.column)
    
    @v_args(inline=True)
    def expresion(self, expr):
        """
        Manejar nodo de expresión (asegura la conversión adecuada de Tree a nodos AST personalizados)
        """
        return expr


class ParserController:
    """
    Controlador para el análisis sintáctico.
    """
    def __init__(self, error_collection=None):
        """
        Inicializa el controlador del analizador sintáctico.
        
        Args:
            error_collection (ErrorCollection, optional): Colección para almacenar errores
        """
        self.error_collection = error_collection or ErrorCollection()
        self.ast = None
        
        # Construir el analizador sintáctico usando Lark
        grammar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'grammar', 'language_grammar.lark')
        
        with open(grammar_path, 'r') as f:
            grammar = f.read()
        
        # Instanciar el transformador
        self.transformer = ASTBuilder()
        
        # Crear el parser con la gramática
        self.parser = Lark(grammar, parser='lalr', lexer='basic', 
                           transformer=self.transformer)
    
    # Modificación para el método parse en ParserController

    def parse(self, code, tokens=None):
        """
        Realiza el análisis sintáctico del código fuente.
        
        Args:
            code (str): Código fuente a analizar
            tokens (list, optional): Lista de tokens generados por el lexer
            
        Returns:
            ASTNode: Nodo raíz del AST o None si hay errores
        """
        # Limpiar errores previos y AST
        self.ast = None
        self.error_collection.syntax_errors.clear()
        
        try:
            # Usar tokens del lexer si están disponibles
            if tokens:
                self.ast = self.parser.parse(code, tokens=tokens)
            else:
                self.ast = self.parser.parse(code)
            
            # Verificar que tenemos un AST válido
            if not isinstance(self.ast, ASTNode):
                error_msg = f"Error al construir el AST: tipo inesperado {type(self.ast).__name__}"
                error = SyntaxError(error_msg)
                self.error_collection.add_error(error)
                return None
            
            return self.ast
            
        except Exception as e:
            # Capturar errores sintácticos
            error_msg = f"Error de sintaxis: {str(e)}"
            error = SyntaxError(error_msg)
            self.error_collection.add_error(error)
            return None

    def get_ast(self):
        """
        Obtiene el AST generado.
        
        Returns:
            ASTNode: Nodo raíz del AST
        """
        return self.ast
    
    def has_errors(self):
        """
        Comprueba si se produjeron errores durante el análisis sintáctico.
        
        Returns:
            bool: True si hay errores, False en caso contrario
        """
        return any(isinstance(e, SyntaxError) for e in self.error_collection.get_all_errors())