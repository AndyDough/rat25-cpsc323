# Token types
TOKEN_TYPES = {
    'KEYWORD': 'KEYWORD',
    'IDENTIFIER': 'IDENTIFIER',
    'INTEGER': 'INTEGER',
    'REAL': 'REAL',
    'OPERATOR': 'OPERATOR',
    'SEPARATOR': 'SEPARATOR',
    'COMMENT': 'COMMENT',
    'UNKNOWN': 'UNKNOWN',
}

# Keywords
KEYWORDS = {
    'function', 'if', 'fi', 'else', 'return', 'put', 'get', 'while',
    'integer', 'boolean', 'real', 'true', 'false'
}

# Operators
OPERATORS = {'==', '!=', '<=', '=>', '=', '>', '<', '+', '-', '*', '/'}
OPERATOR_STARTS = {'=', '!', '<', '>', '+', '-', '*', '/'}

# Separators
SEPARATORS = {'#', '(', ')', '{', '}', ',', ';'}

class Lexer:
    def __init__(self, sourceCode):
        self.sourceCode = sourceCode
        self.tokens = []
        self.currentPosition = 0

    def lex(self):
        # Main FSM driver
        # Continue until all characters in the source code have been processed
        while self.currentPosition < len(self.sourceCode):
            char = self.sourceCode[self.currentPosition]

            if char.isspace():
                self.currentPosition += 1
                continue

            if char == '"':
                self.handleComments()
                continue

            if char.isalpha():
                self.handleIdentifier()
                continue

            if char.isdigit() or char == '.':
                self.handleNumber()
                continue

            if char in OPERATOR_STARTS or char in SEPARATORS:
                self.handleOperatorOrSeparator()
                continue
            
            # If no token is recognized, we have an unknown token
            self.tokens.append((TOKEN_TYPES['UNKNOWN'], char))
            self.currentPosition += 1

        return self.tokens

    # FSM for handling comments
    def handleComments(self):
        startPosition = self.currentPosition
        self.currentPosition += 1
        # Continue until the end of the comment is reached or the end of the source code is reached
        while self.currentPosition < len(self.sourceCode) and self.sourceCode[self.currentPosition] != '"':
            self.currentPosition += 1
        if self.currentPosition < len(self.sourceCode) and self.sourceCode[self.currentPosition] == '"':
            self.currentPosition += 1
        # Comments are ignored, so we don't add a token


    # FSM for handling identifiers and keywords
    def handleIdentifier(self):
        startPosition = self.currentPosition
        # Continue until the end of the identifier is reached
        while self.currentPosition < len(self.sourceCode) and (self.sourceCode[self.currentPosition].isalnum() or self.sourceCode[self.currentPosition] == '_' or self.sourceCode[self.currentPosition] == '$'):
            self.currentPosition += 1
        lexeme = self.sourceCode[startPosition:self.currentPosition]
        if lexeme in KEYWORDS:
            self.tokens.append((TOKEN_TYPES['KEYWORD'], lexeme))
        else:
            self.tokens.append((TOKEN_TYPES['IDENTIFIER'], lexeme))

    # FSM for handling integers and real numbers
    def handleNumber(self):
        startPosition = self.currentPosition
        isReal = False
        
        # Handle numbers starting with a decimal point
        if self.sourceCode[self.currentPosition] == '.':
            isReal = True
            self.currentPosition += 1
            if self.currentPosition >= len(self.sourceCode) or not self.sourceCode[self.currentPosition].isdigit():
                self.tokens.append((TOKEN_TYPES['UNKNOWN'], '.'))
                return
        
        # Continue until the end of the number is reached
        while self.currentPosition < len(self.sourceCode) and self.sourceCode[self.currentPosition].isdigit():
            self.currentPosition += 1
            
        if self.currentPosition < len(self.sourceCode) and self.sourceCode[self.currentPosition] == '.':
            isReal = True
            self.currentPosition += 1
            # Check if there are digits after the decimal point
            if self.currentPosition >= len(self.sourceCode) or not self.sourceCode[self.currentPosition].isdigit():
                lexeme = self.sourceCode[startPosition:self.currentPosition]
                self.tokens.append((TOKEN_TYPES['UNKNOWN'], lexeme))
                return
            while self.currentPosition < len(self.sourceCode) and self.sourceCode[self.currentPosition].isdigit():
                self.currentPosition += 1

        lexeme = self.sourceCode[startPosition:self.currentPosition]
        if isReal:
            self.tokens.append((TOKEN_TYPES['REAL'], lexeme))
        else:
            self.tokens.append((TOKEN_TYPES['INTEGER'], lexeme))

    # FSM for handling operators and separators
    def handleOperatorOrSeparator(self):
        startPosition = self.currentPosition
        op = self.sourceCode[startPosition]
        
        # Check for two-character operators to differentiate for example = and ==
        if self.currentPosition + 1 < len(self.sourceCode):
            twoCharOp = op + self.sourceCode[self.currentPosition + 1]
            if twoCharOp in OPERATORS:
                self.tokens.append((TOKEN_TYPES['OPERATOR'], twoCharOp))
                self.currentPosition += 2
                return

        if op in OPERATORS:
            self.tokens.append((TOKEN_TYPES['OPERATOR'], op))
            self.currentPosition += 1
        elif op in SEPARATORS:
            self.tokens.append((TOKEN_TYPES['SEPARATOR'], op))
            self.currentPosition += 1
        else:
            self.tokens.append((TOKEN_TYPES['UNKNOWN'], op))
            self.currentPosition += 1


def lexer(sourceCode):
    lex = Lexer(sourceCode)
    return lex.lex()

# run test by running python3 lexer.py
if __name__ == '__main__':
    code = """
        "This should be ingored"
        function main() {
            integer x;
            x = 10;
            put(x);
        } # main #

        #
        function test(breh) {
            while e == x;
                e = e + e
        }
        #
    """
    tokens = lexer(code)
    for token in tokens:
        print(token)