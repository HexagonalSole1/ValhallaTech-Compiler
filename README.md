# Analizador Léxico, Sintáctico y Semántico

Un analizador de lenguaje de programación básico desarrollado para la materia de Compiladores e Intérpretes.

## Autores

- **Gerson Daniel García Domínguez** (223181)
- **Julián de Jesús Gutiérrez López** (223195)

## Descripción

Este proyecto implementa un analizador léxico, sintáctico y semántico para un lenguaje de programación básico con las siguientes características:

- Declaraciones de variables (`ent`, `dec`, `cadena`)
- Operaciones aritméticas (`+`, `-`, `*`, `/`)
- Operaciones lógicas y relacionales (`==`, `!=`, `>`, `<`, `>=`, `<=`)
- Estructuras de control:
  - Condicionales (`si` - `oNo`)
  - Bucles (`mientras`, `repetir`)
- Entrada/Salida (`scan`, `sout`)
- Asignaciones (`=`)

## Estructura del Proyecto

```
analizador_compiler/
│
├── models/                 # Estructuras de datos y lógica de negocio
│   ├── token.py            # Definición de tokens
│   ├── symbol_table.py     # Implementación de tabla de símbolos
│   ├── ast_nodes.py        # Nodos del Árbol de Sintaxis Abstracta
│   └── error.py            # Clases para manejo de errores
│
├── controllers/            # Lógica de control
│   ├── lexer_controller.py # Controla análisis léxico
│   ├── parser_controller.py # Controla análisis sintáctico
│   └── semantic_controller.py # Controla análisis semántico
│
├── views/                  # Interfaz de usuario
│   ├── main_window.py      # Ventana principal de la aplicación
│   ├── editor_view.py      # Editor de código
│   ├── output_view.py      # Área de visualización de resultados
│   └── symbol_table_view.py # Visualización de tabla de símbolos
│
├── grammar/                # Definiciones de gramática
│   └── language_grammar.lark  # Gramática del lenguaje en formato Lark
│
├── utils/                  # Funciones de utilidad
│   └── helpers.py          # Funciones auxiliares
│
└── main.py                 # Punto de entrada de la aplicación
```

## Requisitos

- Python 3.8 o superior
- PyQt5
- Lark-parser

## Instalación

1. Clonar este repositorio:
   ```
   git clone <url-repositorio>
   cd analizador_compiler
   ```

2. Crear y activar un entorno virtual (opcional pero recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

Ejecutar la aplicación:
```
python main.py
```

### Características de la Interfaz

- **Editor de Código**: Con resaltado de sintaxis y números de línea.
- **Análisis Léxico**: Muestra los tokens identificados en el código.
- **Análisis Sintáctico**: Construye y muestra el Árbol de Sintaxis Abstracta (AST).
- **Análisis Semántico**: Verifica tipos y variables, mostrando la tabla de símbolos.
- **Gestión de Errores**: Muestra errores léxicos, sintácticos y semánticos.

## Gramática del Lenguaje

La gramática está definida en formato Lark y soporta:

- Declaraciones: `ent x;`, `dec y;`, `cadena mensaje;`
- Expresiones aritméticas: `x = 10 + y * 2;`
- Condicionales: `si (x > y) { ... } oNo { ... }`
- Bucles: `mientras (x > 0) { ... }` y `repetir(5) { ... }`
- E/S: `sout("Hola");` y `scan(x);`

## Casos de Prueba

En el editor, puede probar el siguiente código de ejemplo:

```
// Declaraciones
ent x, y;
dec z;
cadena mensaje;

// Asignaciones
x = 10;
y = 5;
z = 3.14;
mensaje = "Hola, mundo!";

// Condicional
si (x > y) {
    sout("x es mayor que y");
} oNo {
    sout("x no es mayor que y");
}

// Bucle mientras
mientras (x > 0) {
    x = x - 1;
    sout(x);
}

// Bucle repetir
repetir(3) {
    sout("Iteración");
}
```

## Licencia

Este proyecto es de uso educativo y está disponible bajo la Licencia MIT.