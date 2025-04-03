import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QSplitter, QAction, 
                            QFileDialog, QMessageBox, QTabWidget, QVBoxLayout, 
                            QWidget, QHBoxLayout, QPushButton, QLabel)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from views.editor_view import EditorView
from views.output_view import OutputView
from views.symbol_table_view import SymbolTableView

class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.
    """
    def __init__(self, lexer_controller=None, parser_controller=None, semantic_controller=None):
        """
        Inicializa la ventana principal.
        
        Args:
            lexer_controller: Controlador del analizador léxico
            parser_controller: Controlador del analizador sintáctico
            semantic_controller: Controlador del analizador semántico
        """
        super().__init__()
        
        self.lexer_controller = lexer_controller
        self.parser_controller = parser_controller
        self.semantic_controller = semantic_controller
        
        self.setWindowTitle("Analizador Léxico, Sintáctico y Semántico")
        self.setGeometry(100, 100, 1200, 800)
        
        self._create_menu()
        self._create_layout()
        self._create_connections()
    
    def _create_menu(self):
        """
        Crea la barra de menú de la aplicación.
        """
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('Archivo')
        
        new_action = QAction('Nuevo', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self._on_new)
        file_menu.addAction(new_action)
        
        open_action = QAction('Abrir', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self._on_open)
        file_menu.addAction(open_action)
        
        save_action = QAction('Guardar', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Guardar como...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self._on_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Salir', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Editar
        edit_menu = menubar.addMenu('Editar')
        
        cut_action = QAction('Cortar', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(lambda: self.editor_view.cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('Copiar', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(lambda: self.editor_view.copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('Pegar', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(lambda: self.editor_view.paste())
        edit_menu.addAction(paste_action)
        
        # Menú Análisis
        analysis_menu = menubar.addMenu('Análisis')
        
        lexical_action = QAction('Análisis Léxico', self)
        lexical_action.setShortcut('F5')
        lexical_action.triggered.connect(self._on_lexical_analysis)
        analysis_menu.addAction(lexical_action)
        
        syntax_action = QAction('Análisis Sintáctico', self)
        syntax_action.setShortcut('F6')
        syntax_action.triggered.connect(self._on_syntax_analysis)
        analysis_menu.addAction(syntax_action)
        
        semantic_action = QAction('Análisis Semántico', self)
        semantic_action.setShortcut('F7')
        semantic_action.triggered.connect(self._on_semantic_analysis)
        analysis_menu.addAction(semantic_action)
        
        analysis_menu.addSeparator()
        
        full_analysis_action = QAction('Análisis Completo', self)
        full_analysis_action.setShortcut('F8')
        full_analysis_action.triggered.connect(self._on_full_analysis)
        analysis_menu.addAction(full_analysis_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('Ayuda')
        
        about_action = QAction('Acerca de', self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _create_layout(self):
        """
        Crea el diseño de la ventana principal.
        """
        # Área central con splitter
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # Panel izquierdo: Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Título del editor
        editor_title = QLabel("Editor de Código")
        editor_title.setAlignment(Qt.AlignCenter)
        editor_title.setFont(QFont("Arial", 12, QFont.Bold))
        editor_layout.addWidget(editor_title)
        
        # Vista del editor
        self.editor_view = EditorView()
        editor_layout.addWidget(self.editor_view)
        
        # Botones de análisis
        button_layout = QHBoxLayout()
        
        self.lexical_button = QPushButton("Análisis Léxico")
        self.lexical_button.clicked.connect(self._on_lexical_analysis)
        button_layout.addWidget(self.lexical_button)
        
        self.syntax_button = QPushButton("Análisis Sintáctico")
        self.syntax_button.clicked.connect(self._on_syntax_analysis)
        button_layout.addWidget(self.syntax_button)
        
        self.semantic_button = QPushButton("Análisis Semántico")
        self.semantic_button.clicked.connect(self._on_semantic_analysis)
        button_layout.addWidget(self.semantic_button)
        
        self.full_button = QPushButton("Análisis Completo")
        self.full_button.clicked.connect(self._on_full_analysis)
        button_layout.addWidget(self.full_button)
        
        editor_layout.addLayout(button_layout)
        
        # Panel derecho: Resultados en pestañas
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Título de resultados
        results_title = QLabel("Resultados del Análisis")
        results_title.setAlignment(Qt.AlignCenter)
        results_title.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(results_title)
        
        # Pestañas de resultados
        self.results_tabs = QTabWidget()
        
        # Pestaña de salida
        self.output_view = OutputView()
        self.results_tabs.addTab(self.output_view, "Salida")
        
        # Pestaña de tabla de símbolos
        self.symbol_table_view = SymbolTableView()
        self.results_tabs.addTab(self.symbol_table_view, "Tabla de Símbolos")
        
        results_layout.addWidget(self.results_tabs)
        
        # Agregar los widgets al splitter
        main_splitter.addWidget(editor_widget)
        main_splitter.addWidget(results_widget)
        
        # Establecer proporciones iniciales
        main_splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])
    
    def _create_connections(self):
        """
        Establece las conexiones entre señales y slots.
        """
        pass  # Las conexiones se establecen en _create_layout
    
    def _on_new(self):
        """
        Maneja la acción de crear un nuevo archivo.
        """
        if self.editor_view.document().isModified():
            reply = QMessageBox.question(self, 'Guardar cambios',
                                        '¿Desea guardar los cambios antes de crear un nuevo archivo?',
                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            
            if reply == QMessageBox.Save:
                self._on_save()
            elif reply == QMessageBox.Cancel:
                return
        
        self.editor_view.clear()
        self.editor_view.document().setModified(False)
        self.setWindowTitle("Analizador Léxico, Sintáctico y Semántico")
    
    def _on_open(self):
        """
        Maneja la acción de abrir un archivo.
        """
        if self.editor_view.document().isModified():
            reply = QMessageBox.question(self, 'Guardar cambios',
                                        '¿Desea guardar los cambios antes de abrir un archivo?',
                                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            
            if reply == QMessageBox.Save:
                self._on_save()
            elif reply == QMessageBox.Cancel:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(self, 'Abrir archivo', '', 
                                                'Archivos de texto (*.txt);;Todos los archivos (*)')
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.editor_view.setPlainText(file.read())
                
                self.editor_view.document().setModified(False)
                self.setWindowTitle(f"Analizador - {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error al abrir el archivo: {str(e)}')
    
    def _on_save(self):
        """
        Maneja la acción de guardar el archivo actual.
        """
        if not hasattr(self, 'current_file') or not self.current_file:
            return self._on_save_as()
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.editor_view.toPlainText())
            
            self.editor_view.document().setModified(False)
            return True
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error al guardar el archivo: {str(e)}')
            return False
    
    def _on_save_as(self):
        """
        Maneja la acción de guardar como un archivo nuevo.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, 'Guardar archivo', '', 
                                                'Archivos de texto (*.txt);;Todos los archivos (*)')
        
        if file_path:
            self.current_file = file_path
            self.setWindowTitle(f"Analizador - {os.path.basename(file_path)}")
            return self._on_save()
        
        return False
    
    def _on_lexical_analysis(self):
        """
        Maneja la acción de realizar el análisis léxico.
        """
        if not self.lexer_controller:
            QMessageBox.warning(self, 'Advertencia', 'Controlador de análisis léxico no disponible')
            return
        
        code = self.editor_view.toPlainText()
        if not code.strip():
            QMessageBox.information(self, 'Información', 'El editor está vacío')
            return
        
        # Realizar análisis léxico
        tokens = self.lexer_controller.tokenize(code)
        
        # Mostrar resultados
        if self.lexer_controller.has_errors():
            self.output_view.show_errors("Análisis Léxico", 
                                        self.lexer_controller.error_collection.lexical_errors)
        else:
            # Mostrar tokens en la vista de salida
            self.output_view.show_tokens(tokens)
            
            # Mostrar mensaje de éxito
            self.output_view.append_message("\nAnálisis léxico completado con éxito.")
    
    def _on_syntax_analysis(self):
        """
        Maneja la acción de realizar el análisis sintáctico.
        """
        if not self.lexer_controller or not self.parser_controller:
            QMessageBox.warning(self, 'Advertencia', 'Controladores de análisis no disponibles')
            return
        
        code = self.editor_view.toPlainText()
        if not code.strip():
            QMessageBox.information(self, 'Información', 'El editor está vacío')
            return
        
        # Realizar análisis léxico primero
        self.lexer_controller.tokenize(code)
        if self.lexer_controller.has_errors():
            self.output_view.show_errors("Análisis Léxico", 
                                        self.lexer_controller.error_collection.lexical_errors)
            return
        
        # Realizar análisis sintáctico
        ast = self.parser_controller.parse(code)
        
        # Mostrar resultados
        if self.parser_controller.has_errors():
            self.output_view.show_errors("Análisis Sintáctico", 
                                        self.parser_controller.error_collection.syntax_errors)
        else:
            # Mostrar AST en la vista de salida
            self.output_view.show_ast(ast)
            
            # Mostrar mensaje de éxito
            self.output_view.append_message("\nAnálisis sintáctico completado con éxito.")
    
    def _on_semantic_analysis(self):
        """
        Maneja la acción de realizar el análisis semántico.
        """
        if not self.lexer_controller or not self.parser_controller or not self.semantic_controller:
            QMessageBox.warning(self, 'Advertencia', 'Controladores de análisis no disponibles')
            return
        
        code = self.editor_view.toPlainText()
        if not code.strip():
            QMessageBox.information(self, 'Información', 'El editor está vacío')
            return
        
        # Realizar análisis léxico primero
        self.lexer_controller.tokenize(code)
        if self.lexer_controller.has_errors():
            self.output_view.show_errors("Análisis Léxico", 
                                        self.lexer_controller.error_collection.lexical_errors)
            return
        
        # Realizar análisis sintáctico
        ast = self.parser_controller.parse(code)
        if self.parser_controller.has_errors() or ast is None:
            self.output_view.show_errors("Análisis Sintáctico", 
                                        self.parser_controller.error_collection.syntax_errors)
            return
        
        # Realizar análisis semántico
        success = self.semantic_controller.analyze(ast)
        
        # Mostrar resultados
        if not success:
            self.output_view.show_errors("Análisis Semántico", 
                                        self.semantic_controller.error_collection.semantic_errors)
        else:
            # Mostrar tabla de símbolos
            self.symbol_table_view.show_symbol_table(self.semantic_controller.get_symbol_table())
            
            # Cambiar a la pestaña de tabla de símbolos
            self.results_tabs.setCurrentWidget(self.symbol_table_view)
            
            # Mostrar mensaje de éxito en la vista de salida
            self.output_view.append_message("\nAnálisis semántico completado con éxito.")
    
    def _on_full_analysis(self):
        """
        Maneja la acción de realizar el análisis completo (léxico, sintáctico y semántico).
        """
        if not self.lexer_controller or not self.parser_controller or not self.semantic_controller:
            QMessageBox.warning(self, 'Advertencia', 'Controladores de análisis no disponibles')
            return
        
        code = self.editor_view.toPlainText()
        if not code.strip():
            QMessageBox.information(self, 'Información', 'El editor está vacío')
            return
        
        # Limpiar vista de salida
        self.output_view.clear()
        self.output_view.append_message("Iniciando análisis completo...\n")
        
        # 1. Análisis léxico
        self.output_view.append_message("=== Análisis Léxico ===")
        tokens = self.lexer_controller.tokenize(code)
        
        if self.lexer_controller.has_errors():
            self.output_view.show_errors("Errores Léxicos", 
                                        self.lexer_controller.error_collection.lexical_errors)
            return
        
        self.output_view.show_tokens(tokens)
        self.output_view.append_message("Análisis léxico completado con éxito.\n")
        
        # 2. Análisis sintáctico
        self.output_view.append_message("=== Análisis Sintáctico ===")
        ast = self.parser_controller.parse(code)
        
        if self.parser_controller.has_errors() or ast is None:
            self.output_view.show_errors("Errores Sintácticos", 
                                        self.parser_controller.error_collection.syntax_errors)
            return
        
        self.output_view.append_message("Análisis sintáctico completado con éxito.\n")
        
        # 3. Análisis semántico
        self.output_view.append_message("=== Análisis Semántico ===")
        success = self.semantic_controller.analyze(ast)
        
        if not success:
            self.output_view.show_errors("Errores Semánticos", 
                                        self.semantic_controller.error_collection.semantic_errors)
            return
        
        # Mostrar tabla de símbolos
        self.symbol_table_view.show_symbol_table(self.semantic_controller.get_symbol_table())
        
        # Mostrar mensaje de éxito
        self.output_view.append_message("Análisis semántico completado con éxito.\n")
        self.output_view.append_message("=== Análisis Completo Exitoso ===")
        
        # Mostrar un mensaje emergente
        QMessageBox.information(self, 'Éxito', 'El análisis completo se ha realizado con éxito!')
    
    def _on_about(self):
        """
        Muestra información sobre la aplicación.
        """
        QMessageBox.about(self, 'Acerca de',
                        'Analizador Léxico, Sintáctico y Semántico\n\n'
                        'Desarrollado por:\n'
                        '- Gerson Daniel García Domínguez (223181)\n'
                        '- Julián de Jesús Gutiérrez López (223195)\n\n'
                        'Materia: Compiladores e Intérpretes\n'
                        'Universidad Politécnica de Chiapas\n'
                        '8° Semestre - Ingeniería en Desarrollo de Software\n'
                        'Abril 2025')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())