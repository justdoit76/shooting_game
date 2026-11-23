from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
from PySide6.QtGui import QPainter
import sys
from game import Game

class Window(QWidget):

    def __init__(self):
        super().__init__()        
        self.setFixedSize(800,400)
        self.setWindowTitle('Ocean Coding School')
        self.game = Game(self)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.game.draw(qp)
        qp.end()

    def keyPressEvent(self, e):
        self.game.keyPress(e.key(), True)
        return super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.game.keyPress(e.key(), False)
        return super().keyReleaseEvent(e)

    def closeEvent(self, e):
        self.game.closeGame()
        return super().closeEvent(e)

    def gameOver(self):
        yesno = QMessageBox.information(self, 'Game Over', 'Retry(Y), Exit(N)',
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if yesno==QMessageBox.StandardButton.Yes:
            self.game = Game(self)
        else:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())