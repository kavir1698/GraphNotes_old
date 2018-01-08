Instructions how to build the program from source.

Windows:
1. Check the version of Python. This should be 3.5. Other versions have not been tested. For checking this, type in cmd: python --version. If you see this error: " 'python' is not recognized as an internal or external command, operable program or batch file.", install Python3.5 or type in cmd full path to python.exe (For example "C:\Python35\python.exe")
2. Go to folder with project in cmd using command cd path\to\your\project (For example cd C:\Users\YevheniiHyzyla\Desktop\Freelance\
3. Create virtual environment using this command: python -m venv env 
The last argument is a name of the folder that will be created. 
4. Activate your environment using this command: env\Scripts\activate.bat
After that line will have (env) prefix at the start
5. Upgrade pip: pip install --upgrade pip
6. Install modules: pip install bibtexparser pyinstaller pyqt5 sqlalchemy
7. Run application using this command: python application.py. If you don't have any problems, all is OK with modules.
8. Then create executable file using following command: pyinstaller --onefile --clean --windowed --paths env\Lib\site-packages\PyQt5\Qt\bin application.py 
The argument " --paths env\Lib\site-packages\PyQt5\Qt\bin " only need for Windows because pyinstaller doesn't see PyQt without this.
9. In "dist" folder you can see your "application.exe". Don't forget to add "Help" folder with "index.html" and "logo.png" into folder with "application.exe"

Linux (Ubuntu):
1. python3.5 --version
2. Go to folder with project in cmd using command cd
3. python3.5 -m venv env
4. source env/bin/activate
5. pip install --upgrade pip
6. pip install bibtexparser pyinstaller pyqt5 sqlalchemy
7. python application.py
8. pyinstaller --onefile --clean --windowed application.py 
9. Copy "Help" folder and "logo.png" to "dist" folder

Mac:
1. Check the version of Python (should be Python3.5)
2. Go to the project folder in terminal/shell
3. Create virtual environment using: python -m venv name_of_folder
4. Activate virtual environment and go into project folder if it necessary.
5. Upgrade pip: pip install --upgrade pip
6. Install all requirements: pip install bibtexparser pyinstaller pyqt5 sqlalchemy
7. Run and check application.py: python application.py
8. Build project
9. Copy Help and logo.png to executable file.