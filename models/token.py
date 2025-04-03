class Token:
    """
    Clase que representa un token en el análisis léxico.
    """
    def __init__(self, type, value, line, column):
        """
        Inicializa un nuevo token.
        
        Args:
            type (str): El tipo de token (por ejemplo, 'KEYWORD', 'IDENTIFIER', etc.)
            value (str): El valor léxico del token
            line (int): Número de línea donde se encontró el token
            column (int): Posición de columna donde se encontró el token
        """
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        """
        Representación en cadena del token.
        """
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"
    
    def __repr__(self):
        """
        Representación oficial del token.
        """
        return self.__str__()