class CompilerError:
    """
    Clase base para representar errores durante el proceso de compilación.
    """
    def __init__(self, message, line=None, column=None):
        """
        Inicializa un nuevo error.
        
        Args:
            message (str): Mensaje de error
            line (int, optional): Línea donde ocurrió el error
            column (int, optional): Columna donde ocurrió el error
        """
        self.message = message
        self.line = line
        self.column = column
    
    def __str__(self):
        """
        Representación en cadena del error.
        """
        position = ""
        if self.line is not None:
            position += f" en línea {self.line}"
            if self.column is not None:
                position += f", columna {self.column}"
        return f"{self.__class__.__name__}: {self.message}{position}"


class LexicalError(CompilerError):
    """
    Error durante el análisis léxico.
    """
    pass


class SyntaxError(CompilerError):
    """
    Error durante el análisis sintáctico.
    """
    pass


class SemanticError(CompilerError):
    """
    Error durante el análisis semántico.
    """
    pass


class TypeError(SemanticError):
    """
    Error de tipo durante el análisis semántico.
    """
    def __init__(self, expected, found, message=None, line=None, column=None):
        """
        Inicializa un nuevo error de tipo.
        
        Args:
            expected (str): Tipo esperado
            found (str): Tipo encontrado
            message (str, optional): Mensaje adicional
            line (int, optional): Línea donde ocurrió el error
            column (int, optional): Columna donde ocurrió el error
        """
        self.expected = expected
        self.found = found
        if message is None:
            message = f"Se esperaba tipo '{expected}' pero se encontró '{found}'"
        super().__init__(message, line, column)


class UndeclaredError(SemanticError):
    """
    Error por uso de variable no declarada.
    """
    def __init__(self, name, line=None, column=None):
        """
        Inicializa un nuevo error de variable no declarada.
        
        Args:
            name (str): Nombre de la variable no declarada
            line (int, optional): Línea donde ocurrió el error
            column (int, optional): Columna donde ocurrió el error
        """
        super().__init__(f"Variable '{name}' no declarada", line, column)


class RedeclarationError(SemanticError):
    """
    Error por redeclaración de variable.
    """
    def __init__(self, name, line=None, column=None):
        """
        Inicializa un nuevo error de redeclaración.
        
        Args:
            name (str): Nombre de la variable redeclarada
            line (int, optional): Línea donde ocurrió el error
            column (int, optional): Columna donde ocurrió el error
        """
        super().__init__(f"Variable '{name}' ya declarada", line, column)


class ErrorCollection:
    """
    Colección para gestionar errores durante la compilación.
    """
    def __init__(self):
        """
        Inicializa una nueva colección de errores.
        """
        self.lexical_errors = []
        self.syntax_errors = []
        self.semantic_errors = []
    
    def add_error(self, error):
        """
        Añade un error a la colección apropiada según su tipo.
        
        Args:
            error (CompilerError): Error a añadir
        """
        if isinstance(error, LexicalError):
            self.lexical_errors.append(error)
        elif isinstance(error, SyntaxError):
            self.syntax_errors.append(error)
        elif isinstance(error, SemanticError):
            self.semantic_errors.append(error)
    
    def get_all_errors(self):
        """
        Obtiene todos los errores de la colección.
        
        Returns:
            list: Lista de todos los errores
        """
        return self.lexical_errors + self.syntax_errors + self.semantic_errors
    
    def has_errors(self):
        """
        Comprueba si hay errores en la colección.
        
        Returns:
            bool: True si hay errores, False en caso contrario
        """
        return bool(self.lexical_errors or self.syntax_errors or self.semantic_errors)
    
    def clear(self):
        """
        Limpia todos los errores de la colección.
        """
        self.lexical_errors.clear()
        self.syntax_errors.clear()
        self.semantic_errors.clear()
    
    def __str__(self):
        """
        Representación en cadena de todos los errores.
        """
        result = []
        if self.lexical_errors:
            result.append("Errores léxicos:")
            for error in self.lexical_errors:
                result.append(f"  {error}")
        
        if self.syntax_errors:
            result.append("Errores sintácticos:")
            for error in self.syntax_errors:
                result.append(f"  {error}")
        
        if self.semantic_errors:
            result.append("Errores semánticos:")
            for error in self.semantic_errors:
                result.append(f"  {error}")
        
        return "\n".join(result) if result else "No hay errores"