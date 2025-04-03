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
        """
        Crear nodo de expresión relacional.
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
    
    @v_args(inline=True)
    def operador_suma(self, op):
        """
        Extraer operador de suma.
        """
        return op.value if hasattr(op, 'value') else str(op)
    
    @v_args(inline=True)
    def operador_mult(self, op):
        """
        Extraer operador de multiplicación.
        """
        return op.value if hasattr(op, 'value') else str(op)
    
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