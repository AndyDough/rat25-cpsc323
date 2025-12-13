import sys
from lexer import Lexer


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.pos < len(
            self.tokens) else None
        self.output = []

        # Assignment 3: Symbol Table and Instruction Table
        self.symbol_table = {}  # {lexeme: {'address': addr, 'type': type}}
        # List of {'address': i, 'op': op, 'oprnd': oprnd}
        self.instr_table = []
        self.instr_address = 1
        self.memory_address = 10000
        self.jump_stack = []

    def log_production(self, rule):
        self.output.append("    " + rule)

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(
            self.tokens) else None

    def match(self, token_type, token_value=None):
        if self.current_token and self.current_token[0] == token_type:
            if token_value is None or self.current_token[1] == token_value:
                self.output.append(
                    f"Token: {self.current_token[0].capitalize()}, Lexeme: {self.current_token[1]}")
                self.advance()
                return True
        return False

    def error(self, message):
        if self.current_token:
            token_type, lexeme, line_number = self.current_token
            error_message = f"Parser error at line {line_number}: Unexpected token '{lexeme}' of type {token_type}. {message}"
        else:
            error_message = f"Parser error at end of file: {message}"
        raise Exception(error_message)

    # --- Assignment 3 Helper Methods ---

    def gen_instr(self, op, oprnd):
        self.instr_table.append(
            {'address': self.instr_address, 'op': op, 'oprnd': oprnd})
        self.instr_address += 1
        return self.instr_address - 1

    def back_patch(self, jump_addr):
        addr = self.jump_stack.pop()
        # Instr table is 0-indexed, addresses are 1-based
        # We need to find the instruction with address == addr
        # Since we append sequentially, index = addr - 1
        if 0 <= addr - 1 < len(self.instr_table):
            self.instr_table[addr-1]['oprnd'] = jump_addr
        else:
            raise Exception(f"Backpatch error: Invalid address {addr}")

    def insert_symbol(self, lexeme, type_):
        if lexeme in self.symbol_table:
            self.error(f"Identifier '{lexeme}' already declared.")
        self.symbol_table[lexeme] = {
            'address': self.memory_address, 'type': type_}
        self.memory_address += 1

    def get_address(self, lexeme):
        if lexeme not in self.symbol_table:
            self.error(f"Identifier '{lexeme}' not declared.")
        return self.symbol_table[lexeme]['address']

    def get_type(self, lexeme):
        if lexeme not in self.symbol_table:
            self.error(f"Identifier '{lexeme}' not declared.")
        return self.symbol_table[lexeme]['type']

    def print_symbol_table(self):
        print("\nSymbol Table")
        print(f"{'Identifier':<15} {'MemoryLocation':<20} {'Type':<10}")
        for lexeme, data in self.symbol_table.items():
            print(f"{lexeme:<15} {data['address']:<20} {data['type']:<10}")

    def print_assembly(self):
        print("\nAssembly Code Listing")
        for instr in self.instr_table:
            oprnd = instr['oprnd'] if instr['oprnd'] is not None else ""
            print(f"{instr['address']:<4} {instr['op']:<6} {oprnd}")

    def parse(self, output_filename="parser_output.txt"):
        try:
            self.rat25f()
            print("Syntax is correct.")
            
            with open(output_filename, "w") as f:
                # Write Assembly Code
                f.write("Assembly Code Listing\n")
                print("\nAssembly Code Listing")
                for instr in self.instr_table:
                    oprnd = instr['oprnd'] if instr['oprnd'] is not None else ""
                    line = f"{instr['address']:<4} {instr['op']:<6} {oprnd}"
                    f.write(line + "\n")
                    print(line)
                
                # Write Symbol Table
                f.write("\nSymbol Table\n")
                f.write(f"{'Identifier':<15} {'MemoryLocation':<20} {'Type':<10}\n")
                print("\nSymbol Table")
                print(f"{'Identifier':<15} {'MemoryLocation':<20} {'Type':<10}")
                for lexeme, data in self.symbol_table.items():
                    line = f"{lexeme:<15} {data['address']:<20} {data['type']:<10}"
                    f.write(line + "\n")
                    print(line)
                    
            return True
        except Exception as e:
            print(e, file=sys.stderr)
            with open(output_filename, "w") as f:
                f.write(str(e))
            return False

    # --- Grammar Rules ---

    def rat25f(self):
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
        # Simplified Rat25F: No function definitions expected
        if self.current_token and self.current_token[1] == 'function':
            self.log_production(
                "<Opt Function Definitions> ::= <Function Definitions>")
            self.function_definitions()
        else:
            self.log_production("<Opt Function Definitions> ::= <Empty>")

    def function_definitions(self):
        self.log_production(
            "<Function Definitions> ::= <Function> <Function Definitions'>")
        self.function()
        self.function_definitions_prime()

    def function_definitions_prime(self):
        if self.current_token and self.current_token[1] == 'function':
            self.log_production(
                "<Function Definitions'> ::= <Function> <Function Definitions'>")
            self.function()
            self.function_definitions_prime()
        else:
            self.log_production("<Function Definitions'> ::= <Empty>")

    def function(self):
        self.log_production(
            "<Function> ::= function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        if not self.match('KEYWORD', 'function'):
            self.error("Expected 'function'")
        if not self.match('IDENTIFIER'):
            self.error("Expected identifier")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '('")
        self.opt_parameter_list()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')'")
        self.opt_declaration_list()
        self.body()

    def opt_parameter_list(self):
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            self.log_production("<Opt Parameter List> ::= <Parameter List>")
            self.parameter_list()
        else:
            self.log_production("<Opt Parameter List> ::= <Empty>")

    def parameter_list(self):
        self.log_production(
            "<Parameter List> ::= <Parameter> <Parameter List'>")
        self.parameter()
        self.parameter_list_prime()

    def parameter_list_prime(self):
        if self.match('SEPARATOR', ','):
            self.log_production(
                "<Parameter List'> ::= , <Parameter> <Parameter List'>")
            self.parameter()
            self.parameter_list_prime()
        else:
            self.log_production("<Parameter List'> ::= <Empty>")

    def parameter(self):
        self.log_production("<Parameter> ::= <IDs> <Qualifier>")
        ids_list = self.ids_parse_only()
        type_ = self.qualifier()
        for lexeme in ids_list:
            self.insert_symbol(lexeme, type_)

    def qualifier(self):
        self.log_production("<Qualifier> ::= integer | boolean | real")
        if self.match('KEYWORD', 'integer'):
            return 'integer'
        if self.match('KEYWORD', 'boolean'):
            return 'boolean'
        if self.match('KEYWORD', 'real'):
            self.error("Type 'real' is not allowed in Simplified Rat25F")
        self.error("Expected a qualifier")

    def body(self):
        self.log_production("<Body> ::= { <Statement List> }")
        if not self.match('SEPARATOR', '{'):
            self.error("Expected '{'")
        self.statement_list()
        if not self.match('SEPARATOR', '}'):
            self.error("Expected '}'")

    def opt_declaration_list(self):
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ['integer', 'boolean', 'real']:
            self.log_production(
                "<Opt Declaration List> ::= <Declaration List>")
            self.declaration_list()
        else:
            self.log_production("<Opt Declaration List> ::= <Empty>")

    def declaration_list(self):
        self.log_production(
            "<Declaration List> ::= <Declaration> ; <Declaration List'>")
        self.declaration()
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';'")
        self.declaration_list_prime()

    def declaration_list_prime(self):
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] in ['integer', 'boolean', 'real']:
            self.log_production(
                "<Declaration List'> ::= <Declaration> ; <Declaration List'>")
            self.declaration()
            if not self.match('SEPARATOR', ';'):
                self.error("Expected ';'")
            self.declaration_list_prime()
        else:
            self.log_production("<Declaration List'> ::= <Empty>")

    def declaration(self):
        self.log_production("<Declaration> ::= <Qualifier> <IDs>")
        type_ = self.qualifier()
        self.ids_decl(type_)

    def ids_decl(self, type_):
        self.log_production("<IDs> ::= <Identifier> <IDs'>")
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            lexeme = self.current_token[1]
            self.match('IDENTIFIER')
            self.insert_symbol(lexeme, type_)
            self.ids_prime_decl(type_)
        else:
            self.error("Expected identifier")

    def ids_prime_decl(self, type_):
        if self.match('SEPARATOR', ','):
            self.log_production("<IDs'> ::= , <Identifier> <IDs'>")
            if self.current_token and self.current_token[0] == 'IDENTIFIER':
                lexeme = self.current_token[1]
                self.match('IDENTIFIER')
                self.insert_symbol(lexeme, type_)
                self.ids_prime_decl(type_)
            else:
                self.error("Expected identifier")
        else:
            self.log_production("<IDs'> ::= <Empty>")

    def ids_parse_only(self):
        self.log_production("<IDs> ::= <Identifier> <IDs'>")
        lexemes = []
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            lexemes.append(self.current_token[1])
            self.match('IDENTIFIER')
            lexemes.extend(self.ids_prime_parse_only())
        else:
            self.error("Expected identifier")
        return lexemes

    def ids_prime_parse_only(self):
        lexemes = []
        if self.match('SEPARATOR', ','):
            self.log_production("<IDs'> ::= , <Identifier> <IDs'>")
            if self.current_token and self.current_token[0] == 'IDENTIFIER':
                lexemes.append(self.current_token[1])
                self.match('IDENTIFIER')
                lexemes.extend(self.ids_prime_parse_only())
            else:
                self.error("Expected identifier")
        else:
            self.log_production("<IDs'> ::= <Empty>")
        return lexemes

    def ids_scan(self):
        self.log_production("<IDs> ::= <Identifier> <IDs'>")
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            lexeme = self.current_token[1]
            addr = self.get_address(lexeme)
            self.match('IDENTIFIER')
            self.gen_instr('STDIN', None)
            self.gen_instr('POPM', addr)
            self.ids_prime_scan()
        else:
            self.error("Expected identifier")

    def ids_prime_scan(self):
        if self.match('SEPARATOR', ','):
            self.log_production("<IDs'> ::= , <Identifier> <IDs'>")
            if self.current_token and self.current_token[0] == 'IDENTIFIER':
                lexeme = self.current_token[1]
                addr = self.get_address(lexeme)
                self.match('IDENTIFIER')
                self.gen_instr('STDIN', None)
                self.gen_instr('POPM', addr)
                self.ids_prime_scan()
            else:
                self.error("Expected identifier")
        else:
            self.log_production("<IDs'> ::= <Empty>")

    def statement_list(self):
        self.log_production(
            "<Statement List> ::= <Statement> <Statement List'>")
        self.statement()
        self.statement_list_prime()

    def statement_list_prime(self):
        if self.current_token and (self.current_token[1] == '{' or self.current_token[0] == 'IDENTIFIER' or self.current_token[1] in ['if', 'return', 'put', 'get', 'while']):
            self.log_production(
                "<Statement List'> ::= <Statement> <Statement List'>")
            self.statement()
            self.statement_list_prime()
        else:
            self.log_production("<Statement List'> ::= <Empty>")

    def statement(self):
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
            self.error("Unexpected end of input")

    def compound(self):
        self.log_production("<Compound> ::= { <Statement List> }")
        if not self.match('SEPARATOR', '{'):
            self.error("Expected '{'")
        self.statement_list()
        if not self.match('SEPARATOR', '}'):
            self.error("Expected '}'")

    def assign(self):
        self.log_production("<Assign> ::= <Identifier> = <Expression> ;")
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            lexeme = self.current_token[1]
            addr = self.get_address(lexeme)
            self.match('IDENTIFIER')
            if not self.match('OPERATOR', '='):
                self.error("Expected '='")
            self.expression()
            self.gen_instr('POPM', addr)
            if not self.match('SEPARATOR', ';'):
                self.error("Expected ';'")
        else:
            self.error("Expected identifier")

    def _if(self):
        self.log_production(
            "<If> ::= if ( <Condition> ) <Statement> <If_Tail>")
        if not self.match('KEYWORD', 'if'):
            self.error("Expected 'if'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '('")
        self.condition()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')'")

        # Jump over 'then' block if condition is false
        self.gen_instr('JUMPZ', None)  # Placeholder
        jumpz_addr = self.instr_address - 1
        self.jump_stack.append(jumpz_addr)

        self.statement()
        self.if_tail()

    def if_tail(self):
        if self.match('KEYWORD', 'else'):
            self.log_production("<If_Tail> ::= else <Statement> fi")

            # Jump over 'else' block from 'then' block
            self.gen_instr('JUMP', None)  # Placeholder
            jump_addr = self.instr_address - 1

            # Patch the JUMPZ to here (start of else)
            self.back_patch(self.instr_address)

            # Push the JUMP addr to stack to patch later
            self.jump_stack.append(jump_addr)

            self.statement()
            if not self.match('KEYWORD', 'fi'):
                self.error("Expected 'fi'")

            # Patch the JUMP to here (end of if)
            self.back_patch(self.instr_address)

        elif self.match('KEYWORD', 'fi'):
            self.log_production("<If_Tail> ::= fi")
            # Patch the JUMPZ to here (end of if)
            self.back_patch(self.instr_address)
        else:
            self.error("Expected 'fi' or 'else'")

    def _return(self):
        self.log_production("<Return> ::= return <Return_Tail>")
        if not self.match('KEYWORD', 'return'):
            self.error("Expected 'return'")
        self.return_tail()

    def return_tail(self):
        if self.current_token and self.current_token[1] == ';':
            self.log_production("<Return_Tail> ::= ;")
            self.match('SEPARATOR', ';')
        else:
            self.log_production("<Return_Tail> ::= <Expression> ;")
            self.expression()
            if not self.match('SEPARATOR', ';'):
                self.error("Expected ';'")

    def print_statement(self):
        self.log_production("<Print> ::= put ( <Expression> );")
        if not self.match('KEYWORD', 'put'):
            self.error("Expected 'put'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '('")
        self.expression()
        self.gen_instr('STDOUT', None)
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')'")
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';'")

    def scan(self):
        self.log_production("<Scan> ::= get ( <IDs> );")
        if not self.match('KEYWORD', 'get'):
            self.error("Expected 'get'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '('")
        self.ids_scan()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')'")
        if not self.match('SEPARATOR', ';'):
            self.error("Expected ';'")

    def _while(self):
        self.log_production("<While> ::= while ( <Condition> ) <Statement>")

        addr_start = self.instr_address
        self.gen_instr('LABEL', None)  # Mark start of loop

        if not self.match('KEYWORD', 'while'):
            self.error("Expected 'while'")
        if not self.match('SEPARATOR', '('):
            self.error("Expected '('")
        self.condition()
        if not self.match('SEPARATOR', ')'):
            self.error("Expected ')'")

        # Exit jump
        self.gen_instr('JUMPZ', None)
        jumpz_addr = self.instr_address - 1
        self.jump_stack.append(jumpz_addr)

        self.statement()

        # Loop back
        self.gen_instr('JUMP', addr_start)

        # Patch exit jump
        self.back_patch(self.instr_address)

    def condition(self):
        self.log_production(
            "<Condition> ::= <Expression> <Relop> <Expression>")
        self.expression()
        op = self.relop()
        self.expression()

        if op == '==':
            self.gen_instr('EQU', None)
        elif op == '!=':
            self.gen_instr('NEQ', None)
        elif op == '>':
            self.gen_instr('GRT', None)
        elif op == '<':
            self.gen_instr('LES', None)
        elif op == '<=':
            self.gen_instr('LEQ', None)
        elif op == '=>':
            self.gen_instr('GEQ', None)

    def relop(self):
        self.log_production("<Relop> ::= == | != | > | < | <= | =>")
        if self.current_token and self.current_token[0] == 'OPERATOR':
            op = self.current_token[1]
            if op in ['==', '!=', '>', '<', '<=', '=>']:
                self.match('OPERATOR', op)
                return op
        self.error("Expected relational operator")

    def expression(self):
        self.log_production("<Expression> ::= <Term> <Expression'>")
        self.term()
        self.expression_prime()

    def expression_prime(self):
        if self.current_token and self.current_token[0] == 'OPERATOR' and self.current_token[1] in ['+', '-']:
            op = self.current_token[1]
            self.match('OPERATOR', op)
            self.log_production(f"<Expression'> ::= {op} <Term> <Expression'>")
            self.term()
            if op == '+':
                self.gen_instr('ADD', None)
            else:
                self.gen_instr('SUB', None)
            self.expression_prime()
        else:
            self.log_production("<Expression'> ::= <Empty>")

    def term(self):
        self.log_production("<Term> ::= <Factor> <Term'>")
        self.factor()
        self.term_prime()

    def term_prime(self):
        if self.current_token and self.current_token[0] == 'OPERATOR' and self.current_token[1] in ['*', '/']:
            op = self.current_token[1]
            self.match('OPERATOR', op)
            self.log_production(f"<Term'> ::= {op} <Factor> <Term'>")
            self.factor()
            if op == '*':
                self.gen_instr('MUL', None)
            else:
                self.gen_instr('DIV', None)
            self.term_prime()
        else:
            self.log_production("<Term'> ::= <Empty>")

    def factor(self):
        if self.current_token and self.current_token[0] == 'OPERATOR' and self.current_token[1] == '-':
            self.match('OPERATOR', '-')
            self.log_production("<Factor> ::= - <Primary>")
            self.gen_instr('PUSHI', 0)
            self.primary()
            self.gen_instr('SUB', None)
        else:
            self.log_production("<Factor> ::= <Primary>")
            self.primary()

    def primary(self):
        if self.current_token and self.current_token[0] == 'IDENTIFIER':
            self.log_production("<Primary> ::= <Identifier> <Primary_Tail>")
            lexeme = self.current_token[1]
            addr = self.get_address(lexeme)
            self.match('IDENTIFIER')
            self.gen_instr('PUSHM', addr)
            self.primary_tail()
        elif self.current_token and self.current_token[0] == 'INTEGER':
            val = self.current_token[1]
            self.log_production("<Primary> ::= <Integer>")
            self.match('INTEGER')
            self.gen_instr('PUSHI', val)
        elif self.current_token and self.current_token[0] == 'REAL':
            self.error("Reals not supported")
        elif self.current_token and self.current_token[1] == 'true':
            self.log_production("<Primary> ::= true")
            self.match('KEYWORD', 'true')
            self.gen_instr('PUSHI', 1)
        elif self.current_token and self.current_token[1] == 'false':
            self.log_production("<Primary> ::= false")
            self.match('KEYWORD', 'false')
            self.gen_instr('PUSHI', 0)
        elif self.current_token and self.current_token[1] == '(':
            self.log_production("<Primary> ::= ( <Expression> )")
            self.match('SEPARATOR', '(')
            self.expression()
            if not self.match('SEPARATOR', ')'):
                self.error("Expected ')'")
        else:
            self.error("Invalid primary")

    def primary_tail(self):
        if self.current_token and self.current_token[1] == '(':
            self.error("Function calls not supported")
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
