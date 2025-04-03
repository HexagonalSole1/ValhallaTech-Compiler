from lark import Lark, Token as LarkToken
import os
from models.token import Token
from models.error import LexicalError, ErrorCollection

class LexerController:
    """
    Controlador para el análisis léxico.
    """
    def __init__(self, error_collection=None):
        """
        Inicializa el controlador del analizador léxico.
        
        Args:
            error_collection (ErrorCollection, optional): Colección para almacenar errores
        """
        self.error_collection = error_collection or ErrorCollection()
        self.tokens = []
        
        # Construir el analizador léxico usando Lark
        grammar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'grammar', 'language_grammar.lark')
        
        with open(grammar_path, 'r') as f:
            grammar = f.read()
        
        # Crear el lexer en modo lexer-only
        self.lexer = Lark(grammar, parser='lalr', lexer='basic')
    
    def tokenize(self, code):
        """
        Realiza el análisis léxico del código fuente.
        
        Args:
            code (str): Código fuente a analizar
            
        Returns:
            list: Lista de tokens encontrados
        """
        self.tokens = []
        
        try:
            # Usar Lark para tokenizar
            lark_tokens = self.lexer.lex(code)
            
            # Convertir tokens de Lark a nuestro formato
            for lark_token in lark_tokens:
                if isinstance(lark_token, LarkToken):
                    # Crear un token con nuestro formato
                    token = Token(
                        type=lark_token.type,
                        value=lark_token.value,
                        line=lark_token.line,
                        column=lark_token.column
                    )
                    self.tokens.append(token)
        
        except Exception as e:
            # Capturar errores léxicos
            error = LexicalError(str(e))
            self.error_collection.add_error(error)
        
        return self.tokens
    
    def get_tokens(self):
        """
        Obtiene los tokens generados.
        
        Returns:
            list: Lista de tokens
        """
        return self.tokens
    
    def has_errors(self):
        """
        Comprueba si se produjeron errores durante el análisis léxico.
        
        Returns:
            bool: True si hay errores, False en caso contrario
        """
        return any(isinstance(e, LexicalError) for e in self.error_collection.get_all_errors())