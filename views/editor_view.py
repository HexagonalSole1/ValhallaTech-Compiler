from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt5.QtGui import QFont, QColor, QTextFormat, QTextCursor, QPainter, QTextCharFormat
from PyQt5.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    """
    Widget para mostrar números de línea en el editor.
    """
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class EditorView(QPlainTextEdit):
    """
    Vista del editor de código con resaltado de sintaxis y números de línea.
    """
    def __init__(self, parent=None):
        """
        Inicializa el editor de código.
        
        Args:
            parent (QWidget, optional): Widget padre
        """
        super().__init__(parent)
        
        # Configurar la fuente
        font = QFont("Menlo", 11)  # Menlo es una fuente monoespaciada disponible en macOS
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Configurar colores
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: none;
            }
        """)
        
        # Configurar área de números de línea
        self.line_number_area = LineNumberArea(self)
        
        # Conectar señales
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        # Inicializar ancho del área de números de línea
        self.update_line_number_area_width(0)
        
        # Configurar tabulador a 4 espacios
        self.setTabStopWidth(4 * self.fontMetrics().width(' '))
        
        # Habilitar resaltado de la línea actual
        self.setCurrentLineHighlight(True)
        
        # Texto de ejemplo
        self.setPlainText("""// Ejemplo de programa
ent x, y;
dec z;
cadena mensaje;

x = 10;
y = 5;
z = 3.14;
mensaje = "Hola, mundo!";

si (x > y) {
    sout("x es mayor que y");
} oNo {
    sout("x no es mayor que y");
}

mientras (x > 0) {
    x = x - 1;
    sout(x);
}

repetir(3) {
    sout("Iteración");
}
""")
    
    def line_number_area_width(self):
        """
        Calcula el ancho necesario para el área de números de línea.
        
        Returns:
            int: Ancho en píxeles
        """
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().width('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """
        Actualiza el margen izquierdo para acomodar los números de línea.
        
        Args:
            _ (int): Número de bloques (no utilizado)
        """
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """
        Actualiza el área de números de línea cuando se desplaza el editor.
        
        Args:
            rect (QRect): Rectángulo que se actualizó
            dy (int): Desplazamiento vertical
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """
        Maneja el evento de redimensionamiento para ajustar el área de números de línea.
        
        Args:
            event (QResizeEvent): Evento de redimensionamiento
        """
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), 
                                              self.line_number_area_width(), cr.height()))
    
    def line_number_area_paint_event(self, event):
            """
            Dibuja los números de línea en el área correspondiente.
            
            Args:
                event (QPaintEvent): Evento de pintado
            """
            painter = QPainter(self.line_number_area)
            painter.fillRect(event.rect(), QColor("#313335"))
            
            block = self.firstVisibleBlock()
            block_number = block.blockNumber()
            
            # Asegurarnos de que top sea un entero
            top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            bottom = top + round(self.blockBoundingRect(block).height())
            
            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = str(block_number + 1)
                    painter.setPen(QColor("#606366"))
                    
                    # Crear un QRect para el área de dibujo en lugar de usar coordenadas individuales
                    rect = QRect(0, top, self.line_number_area.width(), self.fontMetrics().height())
                    painter.drawText(rect, Qt.AlignRight, number)
                
                block = block.next()
                top = bottom
                bottom = top + round(self.blockBoundingRect(block).height())
                block_number += 1
    
    def setCurrentLineHighlight(self, enable):
        """
        Habilita o deshabilita el resaltado de la línea actual.
        
        Args:
            enable (bool): True para habilitar, False para deshabilitar
        """
        self.highlightCurrentLine = enable
        if enable:
            self.cursorPositionChanged.connect(self.highlightCurrentLine_)
        else:
            self.cursorPositionChanged.disconnect(self.highlightCurrentLine_)
    
    def highlightCurrentLine_(self):
        """
        Resalta la línea actual.
        """
        extraSelections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#323232")
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        
        self.setExtraSelections(extraSelections)