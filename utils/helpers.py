"""
Funciones auxiliares para el analizador.
"""

import os
import re

def load_grammar_file():
    """
    Carga el archivo de gramática.
    
    Returns:
        str: Contenido del archivo de gramática
    """
    grammar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'grammar', 'language_grammar.lark')
    
    with open(grammar_path, 'r') as f:
        return f.read()

def highlight_line(text, line_number, line_color='#ffff00'):
    """
    Resalta una línea específica en el texto.
    
    Args:
        text (str): Texto a procesar
        line_number (int): Número de línea a resaltar
        line_color (str, optional): Color de resaltado en formato hex
        
    Returns:
        str: Texto HTML con la línea resaltada
    """
    lines = text.split('\n')
    if line_number <= 0 or line_number > len(lines):
        return text
    
    result = []
    for i, line in enumerate(lines):
        if i + 1 == line_number:
            result.append(f'<span style="background-color: {line_color};">{line}</span>')
        else:
            result.append(line)
    
    return '\n'.join(result)

def type_check(left_type, right_type, operator):
    """
    Verifica la compatibilidad de tipos para operaciones.
    
    Args:
        left_type (str): Tipo del operando izquierdo
        right_type (str): Tipo del operando derecho
        operator (str): Operador a verificar
        
    Returns:
        str: Tipo resultante si es compatible, None en caso contrario
    """
    # Operaciones aritméticas
    if operator in ('+', '-', '*', '/'):
        if left_type == 'ent' and right_type == 'ent':
            return 'ent'
        elif left_type in ('ent', 'dec') and right_type in ('ent', 'dec'):
            return 'dec'
        elif operator == '+' and left_type == 'cadena' and right_type == 'cadena':
            return 'cadena'  # Concatenación de cadenas
        return None
    
    # Operaciones relacionales
    elif operator in ('==', '!=', '>', '<', '>=', '<='):
        if (left_type in ('ent', 'dec') and right_type in ('ent', 'dec')) or \
           (left_type == 'cadena' and right_type == 'cadena'):
            return 'bool'
        return None
    
    # Operaciones lógicas
    elif operator in ('&&', '||'):
        if left_type == 'bool' and right_type == 'bool':
            return 'bool'
        return None
    
    return None

def is_valid_identifier(name):
    """
    Verifica si un nombre es un identificador válido.
    
    Args:
        name (str): Nombre a verificar
        
    Returns:
        bool: True si es válido, False en caso contrario
    """
    # Debe comenzar con una letra o guion bajo y contener solo letras, dígitos o guiones bajos
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    
    # Verificar que no sea una palabra reservada
    reserved_words = [
        'ent', 'dec', 'cadena', 'si', 'oNo', 'mientras', 'repetir', 'sout', 'scan'
    ]
    
    return bool(re.match(pattern, name)) and name not in reserved_words

def format_ast_as_dot(ast):
    """
    Convierte el AST a formato DOT para visualización con Graphviz.
    
    Args:
        ast (ASTNode): Raíz del AST
        
    Returns:
        str: Representación DOT del AST
    """
    if not ast:
        return "digraph AST { node [shape=box]; label=\"Empty AST\"; }"
    
    dot = ["digraph AST {", "  node [shape=box];"]
    node_id = 0
    node_ids = {}
    
    def add_node(node, label):
        nonlocal node_id
        current_id = node_id
        node_ids[node] = current_id
        dot.append(f'  node{current_id} [label="{label}"];')
        node_id += 1
        return current_id
    
    def add_edge(from_id, to_id, label=""):
        if label:
            dot.append(f'  node{from_id} -> node{to_id} [label="{label}"];')
        else:
            dot.append(f'  node{from_id} -> node{to_id};')
    
    def visit_node(node, parent_id=None, edge_label=""):
        if not node:
            return
        
        # Crear etiqueta del nodo
        node_type = type(node).__name__
        label = node_type
        
        # Añadir atributos específicos según el tipo de nodo
        attrs = []
        if hasattr(node, 'name') and node.name is not None:
            attrs.append(f"name: {node.name}")
        if hasattr(node, 'value') and node.value is not None:
            attrs.append(f"value: {node.value}")
        if hasattr(node, 'operator') and node.operator is not None:
            attrs.append(f"op: {node.operator}")
        if hasattr(node, 'var_type') and node.var_type is not None:
            attrs.append(f"type: {node.var_type}")
        if hasattr(node, 'type') and node.type is not None:
            attrs.append(f"type: {node.type}")
        
        if attrs:
            label += "\\n" + "\\n".join(attrs)
        
        # Crear nodo
        current_id = add_node(node, label)
        
        # Añadir conexión con el padre
        if parent_id is not None:
            add_edge(parent_id, current_id, edge_label)
        
        # Visitar hijos
        if hasattr(node, 'children') and node.children:
            for i, child in enumerate(node.children):
                visit_node(child, current_id, f"child {i+1}")
        
        # Visitar hijos específicos según el tipo de nodo
        if hasattr(node, 'left') and node.left:
            visit_node(node.left, current_id, "left")
        
        if hasattr(node, 'right') and node.right:
            visit_node(node.right, current_id, "right")
        
        if hasattr(node, 'condition') and node.condition:
            visit_node(node.condition, current_id, "condition")
        
        if hasattr(node, 'if_body') and node.if_body:
            visit_node(node.if_body, current_id, "if_body")
        
        if hasattr(node, 'else_body') and node.else_body:
            visit_node(node.else_body, current_id, "else_body")
        
        if hasattr(node, 'body') and node.body:
            visit_node(node.body, current_id, "body")
        
        if hasattr(node, 'expression') and node.expression:
            visit_node(node.expression, current_id, "expression")
        
        if hasattr(node, 'statements') and node.statements:
            for i, stmt in enumerate(node.statements):
                visit_node(stmt, current_id, f"stmt {i+1}")
    
    # Iniciar recorrido
    visit_node(ast)
    
    dot.append("}")
    return "\n".join(dot)