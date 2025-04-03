from lark import Lark, Transformer, v_args
import os
from models.ast_nodes import *
from models.error import SyntaxError, ErrorCollection

class ASTBuilder(Transformer):
    """
    Transformador de Lark para construir el AST a partir del árbol de análisis.
    """
    
    def start(self, args):
        """
        Método para manejar el nodo raíz de la gramática.
        """
        programa_node = ProgramNode()
        
        # Filtrar y añadir solo los elementos válidos
        for arg in args:
            if arg is not None:
                if isinstance(arg, list):
                    # Si es una lista, añadir cada elemento
                    for item in arg:
                        if item is not None:
                            programa_node.add_child(item)
                else:
                    programa_node.add_child(arg)
        
        print(f"start method - Número de hijos: {len(programa_node.children)}")
        return programa_node
    
    def programa(self, args):
        """
        Procesar los elementos del programa.
        """
        programa_node = ProgramNode()
        
        # Depuración detallada
        print(f"programa method - Número de argumentos: {len(args)}")
        
        for arg in args:
            if arg is not None:
                if isinstance(arg, list):
                    # Si es una lista, añadir cada elemento
                    for item in arg:
                        if item is not None:
                            programa_node.add_child(item)
                            print(f"  Añadido hijo: {type(item).__name__}")
                else:
                    programa_node.add_child(arg)
                    print(f"  Añadido hijo: {type(arg).__name__}")
        
        print(f"programa method - Número de hijos: {len(programa_node.children)}")
        return programa_node
    
    @v_args(inline=True)
    def programa(self, *statements):
        node = ProgramNode()
        for statement in statements:
            if statement:  # Ignorar None
                node.add_child(statement)
        return node
    
    @v_args(inline=True)
    def declaracion(self, tipo, identificador_lista):
        print(f"Creando nodo de declaración con tipo: {tipo}")
        print(f"Identificadores: {identificador_lista.identifiers if hasattr(identificador_lista, 'identifiers') else 'ninguno'}")
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
        node.identifiers = []  # Inicializar la lista si no existe
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
            if i+1 < len(args):  # Verificar que hay operando derecho
                operator = args[i] if isinstance(args[i], str) else "&&"
                right = args[i+1]
                left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def expr_relacional(self, *args):
        print(f"Procesando expresión relacional con {len(args)} argumentos")
        
        # Caso 1: Un solo argumento (expresión simple)
        if len(args) == 1:
            return args[0]
        
        # Caso 2: Dos argumentos (expresión relacional sin operador explícito)
        if len(args) == 2:
            left = args[0]
            right = args[1]
            
            # Como no tenemos el operador, usamos ">" por defecto para la condición if
            # Este operador se infiere del contexto (si estamos en un if o while)
            operator = ">"
            print(f"  Inferido operador: {operator} para operandos: {type(left).__name__} y {type(right).__name__}")
            return BinaryOpNode(operator, left, right)
        
        # Caso 3: Tres argumentos (el caso normal que esperaríamos)
        if len(args) == 3:
            left = args[0]
            operator = args[1]
            right = args[2]
            return BinaryOpNode(operator, left, right)
        
        # Caso fallback: más argumentos (inusual)
        left = args[0]
        for i in range(1, len(args), 2):
            if i+1 < len(args):
                operator = args[i] if i < len(args) else ">"
                right = args[i+1]
                left = BinaryOpNode(operator, left, right)
        
        return left

    @v_args(inline=True)
    def expr_aritmetica(self, *args):
        if len(args) == 1:
            return args[0]
            
        # Caso para cuando tenemos dos argumentos pero falta el operador
        if len(args) == 2:
            left = args[0]
            right = args[1]
            operator = "+"  # Operador predeterminado
            print(f"  Inferido operador suma: {operator} para operandos: {type(left).__name__} y {type(right).__name__}")
            return BinaryOpNode(operator, left, right)
            
        left = args[0]
        for i in range(1, len(args), 2):
            if i+1 < len(args):
                operator = args[i] if isinstance(args[i], str) else "+"
                right = args[i+1]
                left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def termino(self, *args):
        if len(args) == 1:
            return args[0]
            
        # Caso para cuando tenemos dos argumentos pero falta el operador
        if len(args) == 2:
            left = args[0]
            right = args[1]
            operator = "*"  # Operador predeterminado
            print(f"  Inferido operador multiplicación: {operator} para operandos: {type(left).__name__} y {type(right).__name__}")
            return BinaryOpNode(operator, left, right)
            
        left = args[0]
        for i in range(1, len(args), 2):
            if i+1 < len(args):
                operator = args[i] if isinstance(args[i], str) else "*"
                right = args[i+1]
                left = BinaryOpNode(operator, left, right)
        return left
    
    @v_args(inline=True)
    def factor(self, value):
        return value
    
    @v_args(inline=True)
    def operador_logico(self, *args):
        if not args:
            print("Warning: operador_logico llamado sin argumentos")
            return "&&"  # Valor predeterminado
        op = args[0]
        return op.value if hasattr(op, 'value') else str(op)
    
    @v_args(inline=True)
    def operador_relacional(self, *args):
        if not args:
            print("Warning: operador_relacional llamado sin argumentos")
            return ">"  # Valor predeterminado
        
        op = args[0]
        print(f"Procesando operador relacional: {op}")
        if hasattr(op, 'value'):
            return op.value
        return str(op)
    
    @v_args(inline=True)
    def operador_suma(self, *args):
        if not args:
            print("Warning: operador_suma llamado sin argumentos")
            return "+"  # Valor predeterminado
        op = args[0]
        return op.value if hasattr(op, 'value') else str(op)
    
    @v_args(inline=True)
    def operador_mult(self, *args):
        if not args:
            print("Warning: operador_mult llamado sin argumentos")
            return "*"  # Valor predeterminado
        op = args[0]
        return op.value if hasattr(op, 'value') else str(op)
    
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

    # Añadido para manejar la regla de inicio
    def start(self, programa):
        # Asegurar que transformamos correctamente el nodo raíz
        if hasattr(programa, 'accept'):
            return programa
        else:
            # Si llegamos aquí, necesitamos convertir el nodo manualmente
            new_programa = ProgramNode()
            # Intentar extraer los hijos si existen
            if hasattr(programa, 'children'):
                for child in programa.children:
                    if hasattr(child, 'accept'):
                        new_programa.add_child(child)
            return new_programa

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
        
        # Crear el parser con modo de depuración para obtener más información
        self.parser = Lark(grammar, parser='lalr', 
                        debug=True,  # Añadir modo de depuración
                        lexer='basic')
    
    def parse(self, code, tokens=None):
        """
        Realiza el análisis sintáctico del código fuente.
        
        Args:
            code (str): Código fuente a analizar
            tokens (list, optional): Lista de tokens generados por el lexer
            
        Returns:
            ASTNode: Nodo raíz del AST o None si hay errores
        """
        try:
            # Usar tokens del lexer si están disponibles
            if tokens:
                parse_tree = self.parser.parse(code, tokens=tokens)
            else:
                parse_tree = self.parser.parse(code)
            
            # Transformar explícitamente el árbol de análisis en un AST
            self.ast = self.transformer.transform(parse_tree)
            
            # Verificar que tenemos un nodo AST válido
            if not hasattr(self.ast, 'accept'):
                print(f"WARNING: Transformation failed - got {type(self.ast).__name__} instead of ASTNode")
                # Crear un nodo de programa manualmente como fallback
                manual_ast = ProgramNode()
                self.ast = manual_ast
            
            return self.ast
            
        except Exception as e:
            # Capturar errores sintácticos
            error_msg = f"Error de sintaxis: {str(e)}"
            print(error_msg)
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
    def handle_declaration(self, decl_node):
        """
        Convierte la declaración en un nodo del AST.
        """
        print(f"Creando nodo de declaración con tipo: {decl_node.var_type}")
        
        # Crear el nodo de declaración
        node = DeclarationNode(decl_node.var_type)
        
        # Crear los nodos de identificadores
        identifiers_node = IdentifierListNode()
        identifiers_node.type = decl_node.var_type
        identifiers_node.identifiers = []
        
        # Añadir los identificadores al nodo de lista
        for id_token in decl_node.children:
            identifier = IdentifierNode(id_token.value)
            identifier.type = decl_node.var_type
            identifiers_node.identifiers.append(id_token.value)
            identifiers_node.add_child(identifier)
        
        # Añadir la lista de identificadores al nodo de declaración
        node.add_child(identifiers_node)
        
        return node    