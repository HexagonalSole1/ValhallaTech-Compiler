from lark import Lark, Transformer, v_args
import os
from models.ast_nodes import *
from models.error import SyntaxError, ErrorCollection

class ASTBuilder(Transformer):
    """
    Transformador de Lark para construir el AST a partir del árbol de análisis.
    """
    
    @v_args(inline=True)
    def programa(self, *statements):
        node = ProgramNode()
        for statement in statements:
            if statement:  # Ignorar None
                node.add_child(statement)
        return node
    
    @v_args(inline=True)
    def declaracion(self, tipo, identificador_lista):
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
        node = IdentifierListNode()
        for identificador in identificadores:
            if isinstance(identificador, IdentifierNode):
                node.identifiers.append(identificador.name)
                node.add_child(identificador)
        return node
    
    @v_args(inline=True)
    def identificador(self, id_token):
        return IdentifierNode(id_token.value, id_token.line, id_token.column)
    
    @v_args(inline=True)
    def asignacion(self, variable, expresion):
        return AssignmentNode(variable, expresion)
    
    @v_args(inline=True)
    def condicional(self, condicion, bloque_if, bloque_else=None):
        return IfNode(condicion, bloque_if, bloque_else)
    
    @v_args(inline=True)
    def bucle_mientras(self, condicion, bloque):
        return WhileNode(condicion, bloque)
    
    @v_args(inline=True)
    def bucle_repetir(self, count, bloque):
        return RepeatNode(count, bloque)
    
    @v_args(inline=True)
    def impresion(self, expr):
        return PrintNode(expr)
    
    @v_args(inline=True)
    def entrada(self, variable):
        return InputNode(variable)
    
    @v_args(inline=True)
    def bloque(self, *statements):
        node = BlockNode()
        for statement in statements:
            if statement:  # Ignorar None
                node.add_statement(statement)
        return node
    
    @v_args(inline=True)
    def expr_logica(self, *args):
        if len(args) == 1:
            return args[0]
        left = args[0]
        for i in range(1, len(args), 2):
            operator = args[i]
            right = args[i+1]
            left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def expr_relacional(self, *args):
        if len(args) == 1:
            return args[0]
        left = args[0]
        for i in range(1, len(args), 2):
            operator = args[i]
            right = args[i+1]
            left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def expr_aritmetica(self, *args):
        if len(args) == 1:
            return args[0]
        left = args[0]
        for i in range(1, len(args), 2):
            operator = args[i]
            right = args[i+1]
            left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def termino(self, *args):
        if len(args) == 1:
            return args[0]
        left = args[0]
        for i in range(1, len(args), 2):
            operator = args[i]
            right = args[i+1]
            left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def factor(self, value):
        return value
    
    @v_args(inline=True)
    def operador_logico(self, op):
        return op.value
    
    @v_args(inline=True)
    def operador_relacional(self, op):
        return op.value
    
    @v_args(inline=True)
    def operador_suma(self, op):
        return op.value
    
    @v_args(inline=True)
    def operador_mult(self, op):
        return op.value
    
    @v_args(inline=True)
    def variable(self, var_token):
        return VariableNode(var_token.value, var_token.line, var_token.column)
    
    @v_args(inline=True)
    def entero(self, num_token):
        return NumberNode(int(num_token.value), num_token.line, num_token.column)
    
    @v_args(inline=True)
    def decimal(self, num_token):
        return NumberNode(float(num_token.value), num_token.line, num_token.column)
    
    @v_args(inline=True)
    def string(self, str_token):
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
        
        # Crear el parser
        self.parser = Lark(grammar, parser='lalr')
        self.transformer = ASTBuilder()
    
    def parse(self, code):
        """
        Realiza el análisis sintáctico del código fuente.
        
        Args:
            code (str): Código fuente a analizar
            
        Returns:
            ASTNode: Nodo raíz del AST o None si hay errores
        """
        try:
            # Analizar el código y construir el árbol de análisis
            parse_tree = self.parser.parse(code)
            
            # Transformar el árbol de análisis en un AST
            self.ast = self.transformer.transform(parse_tree)
            
            return self.ast
            
        except Exception as e:
            # Capturar errores sintácticos
            error = SyntaxError(str(e))
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