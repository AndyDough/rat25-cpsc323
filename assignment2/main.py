import os
import sys
from lexer import Lexer
from parser import Parser

def run_test_on_file(file_path):
    """
    Runs the parser on a single file.
    """
    output_filename = os.path.splitext(file_path)[0] + ".out"
    
    print(f"--- Running test on {file_path} ---")
    
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        return

    lexer = Lexer(source_code)
    tokens = lexer.lex()
    
    parser = Parser(tokens)
    success = parser.parse(output_filename)
    
    if success:
        print(f"Result: {os.path.basename(file_path)} - PASSED")
    else:
        print(f"Result: {os.path.basename(file_path)} - FAILED", file=sys.stderr)
    
    print("-" * (len(file_path) + 24))
    print()

if __name__ == '__main__':
    while True:
        try:
            filename = input("Enter the path to a .rat25 file to test (or 'exit' to quit): ")
            if filename.lower() == 'exit':
                break
            if not filename.endswith('.rat25'):
                print("Please provide a file with a .rat25 extension.", file=sys.stderr)
                continue
            
            run_test_on_file(filename)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

