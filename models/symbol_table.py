class Symbol:
    """
    Clase que representa un símbolo en la tabla de símbolos.
    """
    def __init__(self, name, type=None, value=None, line=None, column=None):
        """
        Inicializa un nuevo símbolo.
        
        Args:
            name (str): Nombre del símbolo (identificador)
            type (str, optional): Tipo de dato del símbolo (ent, dec, cadena, etc.)
            value (any, optional): Valor asociado al símbolo
            line (int, optional): Línea donde se declaró el símbolo
            column (int, optional): Columna donde se declaró el símbolo
        """
        self.name = name
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        """
        Representación en cadena del símbolo.
        """
        return f"Symbol(name='{self.name}', type='{self.type}', value={self.value})"


class SymbolTable:
    """
    Tabla de símbolos para almacenar y gestionar variables declaradas.
    """
    def __init__(self):
        """
        Inicializa una nueva tabla de símbolos vacía.
        """
        self.symbols = {}
        self.scopes = [{}]  # Pila de ámbitos para manejar bloques anidados
        self.current_scope = 0
    
    def enter_scope(self):
        """
        Entra en un nuevo ámbito (por ejemplo, al entrar en un bloque).
        """
        self.scopes.append({})
        self.current_scope += 1
    
    def exit_scope(self):
        """
        Sale del ámbito actual (por ejemplo, al finalizar un bloque).
        """
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1
    
    def insert(self, name, type=None, value=None, line=None, column=None):
        """
        Inserta un nuevo símbolo en la tabla de símbolos.
        
        Args:
            name (str): Nombre del símbolo
            type (str, optional): Tipo de dato del símbolo
            value (any, optional): Valor asociado al símbolo
            line (int, optional): Línea donde se declaró el símbolo
            column (int, optional): Columna donde se declaró el símbolo
            
        Returns:
            bool: True si se insertó correctamente, False si ya existía en el ámbito actual
        """
        # Verificar si ya existe en el ámbito actual
        if name in self.scopes[self.current_scope]:
            return False
        
        # Crear nuevo símbolo y agregarlo al ámbito actual
        symbol = Symbol(name, type, value, line, column)
        self.scopes[self.current_scope][name] = symbol
        self.symbols[name] = symbol
        
        # Debug
        print(f"[SymbolTable] Insertado símbolo: {name}, tipo: {type}, valor: {value}")
        
        return True
    
    def lookup(self, name):
        """
        Busca un símbolo en la tabla de símbolos.
        
        Args:
            name (str): Nombre del símbolo a buscar
            
        Returns:
            Symbol: El símbolo encontrado o None si no existe
        """
        # Buscar desde el ámbito actual hacia atrás
        for i in range(self.current_scope, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def update(self, name, **kwargs):
        """
        Actualiza los atributos de un símbolo existente.
        
        Args:
            name (str): Nombre del símbolo a actualizar
            **kwargs: Atributos a actualizar (type, value, etc.)
            
        Returns:
            bool: True si se actualizó correctamente, False si no existe
        """
        symbol = self.lookup(name)
        if symbol:
            old_value = symbol.value
            
            for key, value in kwargs.items():
                if hasattr(symbol, key):
                    setattr(symbol, key, value)
            
            # Debug
            print(f"[SymbolTable] Actualizado símbolo: {name}, valor anterior: {old_value}, valor nuevo: {symbol.value}")
            
            # Actualizar también en la lista global
            if name in self.symbols:
                for key, value in kwargs.items():
                    if hasattr(self.symbols[name], key):
                        setattr(self.symbols[name], key, value)
            
            return True
        return False
    
    def get_all_symbols(self):
        """
        Obtiene todos los símbolos en la tabla.
        
        Returns:
            list: Lista de todos los símbolos
        """
        # Debug
        print(f"[SymbolTable] Obteniendo todos los símbolos: {len(self.symbols)}")
        for name, symbol in self.symbols.items():
            print(f"[SymbolTable] - {name}: tipo={symbol.type}, valor={symbol.value}")
        
        return list(self.symbols.values())
    """
    Tabla de símbolos para almacenar y gestionar variables declaradas.
    """
    def __init__(self):
        """
        Inicializa una nueva tabla de símbolos vacía.
        """
        self.symbols = {}
        self.scopes = [{}]  # Pila de ámbitos para manejar bloques anidados
        self.current_scope = 0
    
    def enter_scope(self):
        """
        Entra en un nuevo ámbito (por ejemplo, al entrar en un bloque).
        """
        self.scopes.append({})
        self.current_scope += 1
    
    def exit_scope(self):
        """
        Sale del ámbito actual (por ejemplo, al finalizar un bloque).
        """
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1
    
    def insert(self, name, type=None, value=None, line=None, column=None):
        """
        Inserta un nuevo símbolo en la tabla de símbolos.
        
        Args:
            name (str): Nombre del símbolo
            type (str, optional): Tipo de dato del símbolo
            value (any, optional): Valor asociado al símbolo
            line (int, optional): Línea donde se declaró el símbolo
            column (int, optional): Columna donde se declaró el símbolo
            
        Returns:
            bool: True si se insertó correctamente, False si ya existía en el ámbito actual
        """
        # Verificar si ya existe en el ámbito actual
        if name in self.scopes[self.current_scope]:
            return False
        
        # Crear nuevo símbolo y agregarlo al ámbito actual
        symbol = Symbol(name, type, value, line, column)
        self.scopes[self.current_scope][name] = symbol
        self.symbols[name] = symbol
        return True
    
    def lookup(self, name):
        """
        Busca un símbolo en la tabla de símbolos.
        
        Args:
            name (str): Nombre del símbolo a buscar
            
        Returns:
            Symbol: El símbolo encontrado o None si no existe
        """
        # Buscar desde el ámbito actual hacia atrás
        for i in range(self.current_scope, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def update(self, name, **kwargs):
        """
        Actualiza los atributos de un símbolo existente.
        
        Args:
            name (str): Nombre del símbolo a actualizar
            **kwargs: Atributos a actualizar (type, value, etc.)
            
        Returns:
            bool: True si se actualizó correctamente, False si no existe
        """
        symbol = self.lookup(name)
        if symbol:
            for key, value in kwargs.items():
                if hasattr(symbol, key):
                    setattr(symbol, key, value)
            return True
        return False
    
    def get_all_symbols(self):
        """
        Obtiene todos los símbolos en la tabla.
        
        Returns:
            list: Lista de todos los símbolos
        """
        return list(self.symbols.values())