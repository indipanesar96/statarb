# statarb
Imperial College Business School SIF - Statistical Arbitrage


'''
This project now runs in a virtual environment (3.7), for module/python version controlling (better for when we handover to next year's team).
Go to settings (ctrl + alt + s or cmd + ,) and ensure youre using the virtual env (under Project Interpreter)

The most basic of PyCharm shortcuts you may/may not already know that'll make your lives easier when navigating:
    - cmd + B (b for browse) or cmd+click on an object to take you to its definition (ctrl + B/click for windows)
    - cmd + [ = last cursor position (ctrl + alt + left arrow)
    - cmd + ] = next cursor position (ctrl + alt + right arrow)
    - cmd + k (k for Kommit, ie Commit) to commit (ctrl + k  for windows)
    - cmd + shift + k to push a commit up to the sky (ctrl + shift + k for windows)
    - cmd + t (t for updaTe) to pull down the latest commits from the sky (ctrl + t for windows)
    - shift + F6 (with fn key for mac) to do a project-level refactor
    - alt + enter is your friend - pulls up a useful cursor-context menu
    - cmd + alt + L = autoformat (ctrl + alt + L for windows) [DO THIS BEFORE EVERY COMMIT PLS]
    - cmd + alt + O = optimise imports (ctrl + alt + O for windows) [DO THIS BEFORE EVERY COMMIT PLS]

./depricated needs to go; I'll remove it in a week or so (and delete this line after). Take out any code you may and 
implement it in asap please.
chr
Bits of python you may not have seen before:
    - method name preceeded with __ is so a subclass doesn't override a private method of a superclass
        don't have to actually worry about this as I don't think we have any inheritance yet, it's just good practice 
         e.g. https://stackoverflow.com/questions/70528/why-are-pythons-private-methods-not-actually-private
    - DataLocations is an example of an Enum class. More info: https://www.tutorialspoint.com/enum-in-python 
    - The strong typing (anywhere you see variable_name: variable_type, eg 'List', 'Tuple', 'Optional' etc from the typing module)
        aren't actually required, they're just useful within PyCharm to make sure you don't shove a string into an int (or worse) 
         and throw an AttributeError or TypeError at runtime. 
        
If there's any code you can't figure out after some googling remember PyCharm's annotate feature. Right click on the line number
(in fact, any line of any checked in file) you're struggling with and click 'Annotate'. It'll tell you who checked it into the repo. Ask them directly. 
Failing that, contact me.

Of course if there's any code I (I make a lot of mistakes) or anyone else has written that you think is incorrect/could be made better, 
do contact them/change it yourself - this is a learning experience for us all. If it turns out it was correct all along you can use some git magic 
to get it back. Once it's commited it's never lost.
'''
