#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analizador Léxico, Sintáctico y Semántico
Universidad Politécnica de Chiapas
Materia: Compiladores e Intérpretes
Abril 2025

Autores:
- Gerson Daniel García Domínguez (223181)
- Julián de Jesús Gutiérrez López (223195)

Este programa implementa un analizador léxico, sintáctico y semántico
para un lenguaje de programación básico que soporta:
- Declaraciones de variables
- Operaciones aritméticas
- Ciclos (while, repeat)
- Condicionales (if-else)
- Instrucciones de lectura (scan) y escritura (sout)
- Asignaciones
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Importar módulos del proyecto
from models.error import ErrorCollection
from controllers.lexer_controller import LexerController
from controllers.parser_controller import ParserController
from controllers.semantic_controller import SemanticController
from views.main_window import MainWindow

def main():
    """
    Función principal del programa.
    """
    # Asegurar que los recursos se carguen correctamente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    # Crear la aplicación PyQt
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle('Fusion')
    
    # Crear colección de errores compartida
    error_collection = ErrorCollection()
    
    # Crear controladores
    lexer_controller = LexerController(error_collection)
    parser_controller = ParserController(error_collection)
    semantic_controller = SemanticController(error_collection)
    
    # Crear la ventana principal
    window = MainWindow(lexer_controller, parser_controller, semantic_controller)
    window.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()