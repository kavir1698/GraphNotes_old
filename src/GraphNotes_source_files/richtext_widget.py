from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QThread
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QTextCursor, QTextListFormat, QImage
import sys
        
class Main(QMainWindow):
    def __init__(self, app, parent = None):

        QMainWindow.__init__(self,parent)
        widget = RichTextWidget(app)
        self.setCentralWidget(widget)
        self.resize(1000, 600)
        self.show()

class RichTextWidget(QTextEdit):

    def __init__(self, app=None, parent = None):

        QTextEdit.__init__(self,parent)
        qApp.installEventFilter(self)
        self.initUI()
        self.configureLayout()
        
        
    def initUI(self):
        
        self.toolbar = self.initToolbar()
        self.instruments = QToolButton()
        
        #self.instruments.clicked.connect(self.showMenu)
        #self.instruments.pressed.connect(self.showMenu)
        
        self.instruments.setMouseTracking(True)
        
        self.instruments.setStyleSheet("QToolButton{background-color: rgba(255, 255, 255, 0);}"
                                       "QToolButton:hover{background-color: rgba(225, 225, 225, 0);}"
                                       "QToolButton:pressed{background-color: rgba(225, 225, 225, 0);}"
                                       "QToolButton::menu-indicator{top: 20px;}")
         
        self.instruments.setToolButtonStyle(Qt.ToolButtonFollowStyle) 
        self.instruments.setMenu(self.toolbar)  
        self.instruments.setPopupMode(QToolButton.InstantPopup)
        
        #self.instruments.enterEvent = lambda obj: (self.showMenu(obj), [print(i) for i in range(100)])
        #self.instruments.leaveEvent = lambda obj: print("CLOSE")
        self.instruments.setIcon(QIcon("icons/more.png"))
        self.instruments.setIconSize(QSize(16, 16))
        
        
     
    def initToolbar(self):
        toolbar = QMenu()

        boldAction = QAction(QIcon("icons/bold.png"),"Bold", self)
        boldAction.triggered.connect(self.bold)
        
        italicAction = QAction(QIcon("icons/italic.png"),"Italic",self)
        italicAction.triggered.connect(self.italic)
        
        underlAction = QAction(QIcon("icons/underline.png"),"Underline",self)
        underlAction.triggered.connect(self.underline)
    
        strikeAction = QAction(QIcon("icons/strike.png"),"Strike-out",self)
        strikeAction.triggered.connect(self.strike)
        
        superAction = QAction(QIcon("icons/superscript.png"),"Superscript",self)
        superAction.triggered.connect(self.superScript)
    
        subAction = QAction(QIcon("icons/subscript.png"),"Subscript",self)
        subAction.triggered.connect(self.subScript)
    
        alignLeft = QAction(QIcon("icons/align-left.png"),"Align left",self)
        alignLeft.triggered.connect(self.alignLeft)
    
        alignCenter = QAction(QIcon("icons/align-center.png"),"Align center",self)
        alignCenter.triggered.connect(self.alignCenter)
    
        alignRight = QAction(QIcon("icons/align-right.png"),"Align right",self)
        alignRight.triggered.connect(self.alignRight)
    
        alignJustify = QAction(QIcon("icons/align-justify.png"),"Align justify",self)
        alignJustify.triggered.connect(self.alignJustify)
    
        indentAction = QAction(QIcon("icons/indent.png"),"Indent Area",self)
        indentAction.setShortcut("Ctrl+Tab")
        indentAction.triggered.connect(self.indent)
    
        dedentAction = QAction(QIcon("icons/dedent.png"),"Dedent Area",self)
        dedentAction.setShortcut("Shift+Tab")
        dedentAction.triggered.connect(self.dedent)
        
        imageAction = QAction(QIcon("icons/image.png"),"Insert image",self)
        imageAction.setStatusTip("Insert image")
        imageAction.setShortcut("Ctrl+Shift+I")
        imageAction.triggered.connect(self.insertImage)
    
        bulletAction = QAction(QIcon("icons/bullet.png"),"Insert bullet List",self)
        bulletAction.setStatusTip("Insert bullet list")
        bulletAction.setShortcut("Ctrl+Shift+B")
        bulletAction.triggered.connect(self.bulletList)
    
        numberedAction = QAction(QIcon("icons/number.png"),"Insert numbered List",self)
        numberedAction.setStatusTip("Insert numbered list")
        numberedAction.setShortcut("Ctrl+Shift+L")
        numberedAction.triggered.connect(self.numberList)
        
        toolbar.addAction(boldAction)
        toolbar.addAction(italicAction)
        toolbar.addAction(underlAction)
        toolbar.addAction(strikeAction)
        toolbar.addAction(superAction)
        toolbar.addAction(subAction)
    
        toolbar.addSeparator()
    
        toolbar.addAction(alignLeft)
        toolbar.addAction(alignCenter)
        toolbar.addAction(alignRight)
        toolbar.addAction(alignJustify)
    
        toolbar.addSeparator()
    
        toolbar.addAction(indentAction)
        toolbar.addAction(dedentAction)        
        
        toolbar.addSeparator()
        toolbar.addAction(imageAction)
        toolbar.addAction(bulletAction)
        toolbar.addAction(numberedAction)
        
        return toolbar
    
    def showMenu(self, event=None):
        pass
        """
        pos = self.instruments.rect().bottomRight()
        self.toolbar.setMouseTracking(True)
        self.toolbar.leaveEvent = lambda event: self.toolbar.hide()
        thread = QThread()
        thread.run = lambda: self.toolbar.exec_(self.instruments.mapToGlobal(pos)) 
        thread.start()
        """
        
    def hideMenu(self, event=None):
        self.toolbar.close()
    
    def configureLayout(self):
        layout = QGridLayout()
        #layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 10, 10)
        layout.addWidget(self.instruments, 0, 0, Qt.AlignTop | Qt.AlignRight)
        
        self.setLayout(layout)
     
    """ Text action 
    """
    
    def bold(self):
        if self.fontWeight() == QFont.Bold:
            self.setFontWeight(QFont.Normal)
        else:
            self.setFontWeight(QFont.Bold)
            
    def italic(self):
        state = self.fontItalic()
        self.setFontItalic(not state)

    def underline(self):
        state = self.fontUnderline()
        self.setFontUnderline(not state)

    def strike(self):
        # Grab the text's format
        fmt = self.currentCharFormat()
        
        # Set the fontStrikeOut property to its opposite
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        
        # And set the next char format
        self.setCurrentCharFormat(fmt)    
        

    def superScript(self):

        # Grab the current format
        fmt = self.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QTextCharFormat.AlignSuperScript)

        else:

            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)

        # Set the new format
        self.setCurrentCharFormat(fmt)

    def subScript(self):

        # Grab the current format
        fmt = self.currentCharFormat()

        # And get the vertical alignment property
        align = fmt.verticalAlignment()

        # Toggle the state
        if align == QTextCharFormat.AlignNormal:

            fmt.setVerticalAlignment(QTextCharFormat.AlignSubScript)

        else:

            fmt.setVerticalAlignment(QTextCharFormat.AlignNormal)

        # Set the new format
        self.setCurrentCharFormat(fmt)

    def alignLeft(self):
        self.setAlignment(Qt.AlignLeft)

    def alignRight(self):
        self.setAlignment(Qt.AlignRight)

    def alignCenter(self):
        self.setAlignment(Qt.AlignCenter)

    def alignJustify(self):
        self.setAlignment(Qt.AlignJustify)

    def indent(self):
        # Grab the cursor
        cursor = self.textCursor()
        if cursor.hasSelection():

            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to the selection's end
            cursor.setPosition(cursor.anchor())

            # Calculate range of selection
            diff = cursor.blockNumber() - temp

            direction = QTextCursor.Up if diff > 0 else QTextCursor.Down

            # Iterate over lines (diff absolute value)
            for n in range(abs(diff) + 1):

                # Move to start of each line
                cursor.movePosition(QTextCursor.StartOfLine)

                # Insert tabbing
                cursor.insertText("\t")

                # And move back up
                cursor.movePosition(direction)

        # If there is no selection, just insert a tab
        else:

            cursor.insertText("\t")

    def handleDedent(self,cursor):

        cursor.movePosition(QTextCursor.StartOfLine)

        # Grab the current line
        line = cursor.block().text()

        # If the line starts with a tab character, delete it
        if line.startswith("\t"):

            # Delete next character
            cursor.deleteChar()

        # Otherwise, delete all spaces until a non-space character is met
        else:
            for char in line[:8]:

                if char != " ":
                    break

                cursor.deleteChar()

    def dedent(self):

        cursor = self.textCursor()

        if cursor.hasSelection():

            # Store the current line/block number
            temp = cursor.blockNumber()

            # Move to the selection's last line
            cursor.setPosition(cursor.anchor())

            # Calculate range of selection
            diff = cursor.blockNumber() - temp

            direction = QTextCursor.Up if diff > 0 else QTextCursor.Down

            # Iterate over lines
            for n in range(abs(diff) + 1):

                self.handleDedent(cursor)

                # Move up
                cursor.movePosition(direction)

        else:
            self.handleDedent(cursor)


    def bulletList(self):

        cursor = self.textCursor()

        # Insert bulleted list
        cursor.insertList(QTextListFormat.ListDisc)

    def numberList(self):

        cursor = self.textCursor()

        # Insert list with numbers
        cursor.insertList(QTextListFormat.ListDecimal) 
        
    def bulletList(self):

        cursor = self.textCursor()

        # Insert bulleted list
        cursor.insertList(QTextListFormat.ListDisc)

    def numberList(self):

        cursor = self.textCursor()

        # Insert list with numbers
        cursor.insertList(QTextListFormat.ListDecimal)   
        
    def insertImage(self):

        # Get image file name
        filename = QFileDialog.getOpenFileName(self, 'Insert image',".","Images (*.png *.xpm *.jpg *.bmp *.gif)")[0]
        
        if filename:

            # Create image object
            image = QImage(filename)

            # Error if unloadable
            if image.isNull():

                popup = QMessageBox(QMessageBox.Critical,
                                          "Image load error",
                                          "Could not load image file!",
                                          QMessageBox.Ok,
                                          self)
                popup.show()

            else:

                cursor = self.textCursor()

                cursor.insertImage(image,filename)

    

def main():

    app = QApplication(sys.argv)

    main = Main(app)
    main.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
    