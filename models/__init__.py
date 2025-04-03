# Exportar clases principales
from models.token import Token
from models.symbol_table import Symbol, SymbolTable
from models.ast_nodes import (
    ASTNode, ProgramNode, DeclarationNode, IdentifierListNode, IdentifierNode,
    AssignmentNode, BinaryOpNode, UnaryOpNode, NumberNode, StringNode, VariableNode,
    IfNode, WhileNode, RepeatNode, PrintNode, InputNode, BlockNode
)
from models.error import (
    CompilerError, LexicalError, SyntaxError, SemanticError,
    TypeError, UndeclaredError, RedeclarationError, ErrorCollection
)