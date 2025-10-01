from lexer import lexer
import os

def runTest(testFile):
    # Runs the lexer on a given test file and writes the output to a .out file.
    testFile = os.path.join("testFiles", testFile)
    try:
        with open(testFile, 'r') as f:
            code = f.read()
        
        tokens = lexer(code)
        
        outputFile = os.path.splitext(testFile)[0] + ".out"
        
        with open(outputFile, 'w') as f:
            f.write("Token Type | Lexeme\n")
            f.write("---------------------\n")
            for tokenType, lexeme in tokens:
                f.write(f"{tokenType}, {lexeme}\n")
                
        print(f"Successfully ran test '{testFile}'. Output written to '{outputFile}'.")

    except FileNotFoundError:
        print(f"Error: Test file '{testFile}' not found.")

def main():
    testFiles = ["test1.rat25", "test2.rat25", "test3.rat25"]
    
    while True:
        print("\nSelect a test case to run:")
        for i, testFile in enumerate(testFiles):
            print(f"{i+1}. {testFile}")
        
        choice = input("Enter the number or the name of the test file (or 'q' to quit): ")
        
        if choice.lower() == 'q':
            break
        
        try:
            choiceNum = int(choice)
            if 1 <= choiceNum <= len(testFiles):
                runTest(testFiles[choiceNum - 1])
            else:
                print("Invalid number. Please try again.")
                print("If you are trying to run your own test file be sure that it is .rat25")
        except ValueError:
            # If the input is not a number, treat it as a filename
            if not choice.endswith(".rat25"):
                choice += ".rat25"
            runTest(choice)

if __name__ == '__main__':
    main()
