import sys
from lexer import Lexer


class Parser:
    """
    A recursive descent parser for the Rat25F language.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.pos < len(
            self.tokens) else None
        self.output = []

    def log_production(self, rule):
        self.output.append("    " + rule)

    def advance(self):
        """Consumes the current token and moves to the next one."""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(
            self.tokens) else None

    def match(self, token_type, token_value=None):
        """
        Checks if the current token matches the expected type and value.
        If it matches, it consumes the token and returns True. Otherwise, returns False.
        """
        if self.current_token and self.current_token[0] == token_type:
            if token_value is None or self.current_token[1] == token_value:
                self.output.append(
                    f"Token: {self.current_token[0].capitalize()}, Lexeme: {self.current_token[1]}")
                self.advance()
                return True
        return False

    def error(self, message):
        """Raises a syntax error with a descriptive message."""
        if self.current_token:
            token_type, lexeme, line_number = self.current_token
            error_message = f"Parser error at line {line_number}: Unexpected token '{lexeme}' of type {token_type}. {message}"
        else:
            error_message = f"Parser error at end of file: {message}"
        raise Exception(error_message)

    def parse(self, output_filename="parser_output.txt"):
        """
        Starts the parsing process and handles the output.
        """
        try:
            self.rat25f()
            print("Syntax is correct.")
            with open(output_filename, "w") as f:
                for line in self.output:
                    f.write(line + "\n")
            print(f"Parser output written to {output_filename}")
            return True
        except Exception as e:
            print(e, file=sys.stderr)
            with open(output_filename, "w") as f:
                f.write(str(e))
            return False

    # Grammar rule implementations

    def rat25f(self):
        """R1. <Rat25F> ::= <Opt Function Definitions> # <Opt Declaration List> <Statement List> #"""
        self.log_production(
            "<Rat25F> ::= <Opt Function Definitions> # <Opt Declaration List> <Statement List> #")
        self.opt_function_definitions()
        if not self.match('SEPARATOR', '#'):
            self.error("Expected '#' after function definitions")
        self.opt_declaration_list()
        self.statement_list()
        if not self.match('SEPARATOR', '#'):
            self.error("Expected '#' at the end of the program")

    def opt_function_definitions(self):
        """R2. <Opt Function Definitions> ::= <Function Definitions> | <Empty>"""
        if self.current_token and self.current_token[1] == 'function':
            self.log_production(
                "<Opt Function Definitions> ::= <Function Definitions>")
            self.function_definitions()
        else:
            self.log_production("<Opt Function Definitions> ::= <Empty>")

    def function_definitions(self):
        """R3. <Function Definitions> ::= <Function> <Function Definitions'>"""
        self.log_production(
            "<Function Definitions> ::= <Function> <Function Definitions'>")
        self.function()
        self.function_definitions_prime()

    def function_definitions_prime(self):
        """R3'. <Function Definitions'> ::= <Function> <Function Definitions'> | <Empty>"""
        if self.current_token and self.current_token[1] == 'function':
            self.log_production(
                "<Function Definitions'> ::= <Function> <Function Definitions'>")
            self.function()
            self.function_definitions_prime()
        else:
            self.log_production("<Function Definitions'> ::= <Empty>")

    def function(self):
        """R4. <Function> ::= function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>"""
        self.log_production(
            "<Function> ::= function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        if not self.match('KEYWORD', 'function'):
            self.error("Expected 'function'")
        if not self.match('IDENTIFIER'):
            self.error("Expected identifier after 'function'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '(' after function identifier")
        self.opt_parameter_list()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')' after parameter list")
        self.opt_declaration_list()
        self.body()

    def opt_parameter_list(self):
        """R5. <Opt Parameter List> ::= <Parameter List> | <Empty>"""
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            self.log_production("<Opt Parameter List> ::= <Parameter List>")
            self.parameter_list()
        else:
            self.log_production("<Opt Parameter List> ::= <Empty>")

    def parameter_list(self):
        """R6. <Parameter List> ::= <Parameter> <Parameter List'>"""
        self.log_production(
            "<Parameter List> ::= <Parameter> <Parameter List'>")
        self.parameter()
        self.parameter_list_prime()

    def parameter_list_prime(self):
        """R6'. <Parameter List'> ::= , <Parameter> <Parameter List'> | <Empty>"""
        if self.match('SEPARATOR', ','):
            self.log_production(
                "<Parameter List'> ::= , <Parameter> <Parameter List'>")
            self.parameter()
            self.parameter_list_prime()
        else:
            self.log_production("<Parameter List'> ::= <Empty>")

    def parameter(self):
        """R7. <Parameter> ::= <IDs> <Qualifier>"""
        self.log_production("<Parameter> ::= <IDs> <Qualifier>")
        self.ids()
        self.qualifier()

    def qualifier(self):
        """R8. <Qualifier> ::= integer | boolean | real"""
        self.log_production("<Qualifier> ::= integer | boolean | real")
        if not (self.match('KEYWORD', 'integer') or
                self.match('KEYWORD', 'boolean') or
                self.match('KEYWORD', 'real')):
            self.error("Expected a qualifier (integer, boolean, real)")

    def body(self):
        """R9. <Body> ::= { <Statement List> }"""
        self.log_production("<Body> ::= { <Statement List> }")
        if not self.match('SEPARATOR', '{'):
            self.error("Expected '{' for body")
        self.statement_list()
        if not self.match('SEPARATOR', '}'):
            self.error("Expected '}' for body")

    def opt_declaration_list(self):
        """R10. <Opt Declaration List> ::= <Declaration List> | <Empty>"""
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ['integer', 'boolean', 'real']:
            self.log_production(
                "<Opt Declaration List> ::= <Declaration List>")
            self.declaration_list()
        else:
            self.log_production("<Opt Declaration List> ::= <Empty>")

    def declaration_list(self):
        """R11. <Declaration List> ::= <Declaration> ; <Declaration List'>"""
        self.log_production(
            "<Declaration List> ::= <Declaration> ; <Declaration List'>")
        self.declaration()
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';' after declaration")
        self.declaration_list_prime()

    def declaration_list_prime(self):
        """R11'. <Declaration List'> ::= <Declaration> ; <Declaration List'> | <Empty>"""
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ['integer', 'boolean', 'real']:
            self.log_production(
                "<Declaration List'> ::= <Declaration> ; <Declaration List'>")
            self.declaration()
            if not self.match('SEPARATOR', ';'):
                self.error("Expected ';' after declaration")
            self.declaration_list_prime()
        else:
            self.log_production("<Declaration List'> ::= <Empty>")

    def declaration(self):
        """R12. <Declaration> ::= <Qualifier> <IDs>"""
        self.log_production("<Declaration> ::= <Qualifier> <IDs>")
        self.qualifier()
        self.ids()

    def ids(self):
        """R13. <IDs> ::= <Identifier> <IDs'>"""
        self.log_production("<IDs> ::= <Identifier> <IDs'>")
        if not self.match('IDENTIFIER'):
            self.error("Expected an identifier")
        self.ids_prime()

    def ids_prime(self):
        """R13'. <IDs'> ::= , <Identifier> <IDs'> | <Empty>"""
        if self.match('SEPARATOR', ','):
            self.log_production("<IDs'> ::= , <Identifier> <IDs'>")
            if not self.match('IDENTIFIER'):
                self.error("Expected an identifier after ','")
            self.ids_prime()
        else:
            self.log_production("<IDs'> ::= <Empty>")

    def statement_list(self):
        """R14. <Statement List> ::= <Statement> <Statement List'>"""
        self.log_production(
            "<Statement List> ::= <Statement> <Statement List'>")
        self.statement()
        self.statement_list_prime()

    def statement_list_prime(self):
        """R14'. <Statement List'> ::= <Statement> <Statement List'> | <Empty>"""
        if self.current_token and (self.current_token[1] == '{' or
           self.current_token[0] == 'IDENTIFIER' or
           self.current_token[1] in ['if', 'return', 'put', 'get', 'while']):
            self.log_production(
                "<Statement List'> ::= <Statement> <Statement List'>")
            self.statement()
            self.statement_list_prime()
        else:
            self.log_production("<Statement List'> ::= <Empty>")

    def statement(self):
        """R15. <Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>"""
        if self.current_token:
            if self.current_token[1] == '{':
                self.log_production("<Statement> ::= <Compound>")
                self.compound()
            elif self.current_token[0] == 'IDENTIFIER':
                self.log_production("<Statement> ::= <Assign>")
                self.assign()
            elif self.current_token[1] == 'if':
                self.log_production("<Statement> ::= <If>")
                self._if()
            elif self.current_token[1] == 'return':
                self.log_production("<Statement> ::= <Return>")
                self._return()
            elif self.current_token[1] == 'put':
                self.log_production("<Statement> ::= <Print>")
                self.print_statement()
            elif self.current_token[1] == 'get':
                self.log_production("<Statement> ::= <Scan>")
                self.scan()
            elif self.current_token[1] == 'while':
                self.log_production("<Statement> ::= <While>")
                self._while()
            else:
                self.error("Invalid statement")
        else:
            self.error("Unexpected end of input, expected a statement")

    def compound(self):
        """R16. <Compound> ::= { <Statement List> }"""
        self.log_production("<Compound> ::= { <Statement List> }")
        if not self.match('SEPARATOR', '{'):
            self.error("Expected '{' for compound statement")
        self.statement_list()
        if not self.match('SEPARATOR', '}'):
            self.error("Expected '}' for compound statement")

    def assign(self):
        """R17. <Assign> ::= <Identifier> = <Expression> ;"""
        self.log_production("<Assign> ::= <Identifier> = <Expression> ;")
        if not self.match('IDENTIFIER'):
            self.error("Expected identifier for assignment")
        if not self.match('OPERATOR', '='):
            self.error("Expected '=' for assignment")
        self.expression()
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';' after assignment expression")

    def _if(self):
        """R18. <If> ::= if ( <Condition> ) <Statement> <If_Tail>"""
        self.log_production(
            "<If> ::= if ( <Condition> ) <Statement> <If_Tail>")
        if not self.match('KEYWORD', 'if'):
            self.error("Expected 'if'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '(' after 'if'")
        self.condition()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')' after condition")
        self.statement()
        self.if_tail()

    def if_tail(self):
        """R18_Tail. <If_Tail> ::= fi | else <Statement> fi"""
        if self.match('KEYWORD', 'else'):
            self.log_production("<If_Tail> ::= else <Statement> fi")
            self.statement()
            if not self.match('KEYWORD', 'fi'):
                self.error("Expected 'fi' after 'else' statement")
        elif self.match('KEYWORD', 'fi'):
            self.log_production("<If_Tail> ::= fi")
        else:
            self.error("Expected 'fi' or 'else'")

    def _return(self):
        """R19. <Return> ::= return <Return_Tail>"""
        self.log_production("<Return> ::= return <Return_Tail>")
        if not self.match('KEYWORD', 'return'):
            self.error("Expected 'return'")
        self.return_tail()

    def return_tail(self):
        """R19_Tail. <Return_Tail> ::= ; | <Expression> ;"""
        if self.current_token and self.current_token[1] == ';':
            self.log_production("<Return_Tail> ::= ;")
            self.match('SEPARATOR', ';')
        else:
            self.log_production("<Return_Tail> ::= <Expression> ;")
            self.expression()
            if not self.match('SEPARATOR', ';'):
                self.error("Expected ';' after return expression")

    def print_statement(self):
        """R20. <Print> ::= put ( <Expression> );"""
        self.log_production("<Print> ::= put ( <Expression> );")
        if not self.match('KEYWORD', 'put'):
            self.error("Expected 'put'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '(' after 'put'")
        self.expression()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')' after expression in 'put'")
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';' after 'put' statement")

    def scan(self):
        """R21. <Scan> ::= get ( <IDs> );"""
        self.log_production("<Scan> ::= get ( <IDs> );")
        if not self.match('KEYWORD', 'get'):
            self.error("Expected 'get'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '(' after 'get'")
        self.ids()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')' after IDs in 'get'")
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';' after 'get' statement")

    def _while(self):
        """R22. <While> ::= while ( <Condition> ) <Statement>"""
        self.log_production("<While> ::= while ( <Condition> ) <Statement>")
        if not self.match('KEYWORD', 'while'):
            self.error("Expected 'while'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '(' after 'while'")
        self.condition()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')' after condition in 'while'")
        self.statement()

    def condition(self):
        """R23. <Condition> ::= <Expression> <Relop> <Expression>"""
        self.log_production(
            "<Condition> ::= <Expression> <Relop> <Expression>")
        self.expression()
        self.relop()
        self.expression()

    def relop(self):
        """R24. <Relop> ::= == | != | > | < | <= | =>"""
        self.log_production("<Relop> ::= == | != | > | < | <= | =>")
        if not (self.match('OPERATOR', '==') or
                self.match('OPERATOR', '!=') or
                self.match('OPERATOR', '>') or
                self.match('OPERATOR', '<') or
                self.match('OPERATOR', '<=') or
                self.match('OPERATOR', '=>')):
            self.error("Expected a relational operator")

    def expression(self):
        """R25. <Expression> ::= <Term> <Expression'>"""
        self.log_production("<Expression> ::= <Term> <Expression'>")
        self.term()
        self.expression_prime()

    def expression_prime(self):
        """R25'. <Expression'> ::= + <Term> <Expression'> | - <Term> <Expression'> | <Empty>"""
        if self.current_token and self.current_token[0] == 'OPERATOR' and self.current_token[1] in ['+', '-']:
            op = self.current_token[1]
            self.match('OPERATOR', op)
            self.log_production(f"<Expression'> ::= {op} <Term> <Expression'>")
            self.term()
            self.expression_prime()
        else:
            self.log_production("<Expression'> ::= <Empty>")

    def term(self):
        """R26. <Term> ::= <Factor> <Term'>"""
        self.log_production("<Term> ::= <Factor> <Term'>")
        self.factor()
        self.term_prime()

    def term_prime(self):
        """R26'. <Term'> ::= * <Factor> <Term'> | / <Factor> <Term'> | <Empty>"""
        if self.current_token and self.current_token[0] == 'OPERATOR' and self.current_token[1] in ['*', '/']:
            op = self.current_token[1]
            self.match('OPERATOR', op)
            self.log_production(f"<Term'> ::= {op} <Factor> <Term'>")
            self.factor()
            self.term_prime()
        else:
            self.log_production("<Term'> ::= <Empty>")

    def factor(self):
        """R27. <Factor> ::= - <Primary> | <Primary>"""
        if self.current_token and self.current_token[0] == 'OPERATOR' and self.current_token[1] == '-':
            self.match('OPERATOR', '-')
            self.log_production("<Factor> ::= - <Primary>")
            self.primary()
        else:
            self.log_production("<Factor> ::= <Primary>")
            self.primary()

    def primary(self):
        """R28. <Primary> ::= <Identifier> <Primary_Tail> | <Integer> | ( <Expression> ) | <Real> | true | false"""
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            self.log_production("<Primary> ::= <Identifier> <Primary_Tail>")
            self.match('IDENTIFIER')
            self.primary_tail()
        elif self.match('INTEGER'):
            self.log_production("<Primary> ::= <Integer>")
        elif self.match('REAL'):
            self.log_production("<Primary> ::= <Real>")
        elif self.match('KEYWORD', 'true'):
            self.log_production("<Primary> ::= true")
        elif self.match('KEYWORD', 'false'):
            self.log_production("<Primary> ::= false")
        elif self.match('SEPARATOR', '('):
            self.log_production("<Primary> ::= ( <Expression> )")
            self.expression()
            if not self.match('SEPARATOR', ')'):
                self.error("Expected ')' after expression")
        else:
            self.error("Invalid primary expression")

    def primary_tail(self):
        """R28_Tail. <Primary_Tail> ::= ( <IDs> ) | <Empty>"""
        if self.current_token and self.current_token[1] == '(':
            self.log_production("<Primary_Tail> ::= ( <IDs> )")
            self.match('SEPARATOR', '(')
            self.ids()
            if not self.match('SEPARATOR', ')'):
                self.error("Expected ')' after IDs in function call")
        else:
            self.log_production("<Primary_Tail> ::= <Empty>")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 parser.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    lexer = Lexer(source_code)
    tokens = lexer.lex()

    parser = Parser(tokens)
    parser.parse()
