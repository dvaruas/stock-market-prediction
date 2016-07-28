# This is the main file to run the project

from mainProgram import Main

mainObject = Main()

while True:
    mainObject.main()
    
    wantToContinue = raw_input('\nWant to continue? (y/n) : ')
    
    if wantToContinue == 'n':
        break
    else:
        pass
