from mainwindow import MainWindow
from frames import ParamSelectionFrame, ModelTrainingFrame

if __name__ == '__main__':
    # initialize main window
    mw = MainWindow([ParamSelectionFrame, ModelTrainingFrame])
    mw.show()