import sys
import os
import random
import json
from PySide6.QtWidgets import QApplication, QFrame,QGridLayout,QVBoxLayout,QWidget,QSizePolicy,QComboBox,QPushButton,QLabel,QSizePolicy
from PySide6.QtCore import *
from PySide6.QtGui import *
PARKING_SIZE = 6 #GRID SIZE IS PARKING_SIZE*PARKING_SIZE
EMPTY = 0 #DENOTES EMPTY SPACE
VERTICAL = 1
HORIZONTAL = 0

#COLORS FOR IDS IN GRID
COLORS = [
    (100,100,100),
    (255,0,0),
    (100,230,50),
    (160,70,230),
    (70,230,255),
    (255,200,50),
    (255,140,50),
    (0,255,170),
    (255,90,220),
    (50,75,90)
]


"""
Car widget contains current info about car
"""
class Car(QWidget):
    def __init__(self,parent,id,length,position,orientation,colors):
        super().__init__(parent)
        assert orientation in [VERTICAL,HORIZONTAL], f"invalid orientation for car:{orientation}"
        assert len(colors) == 3, f"wrong format for colors:{colors}"
        assert len(position) == 2, f"wrong format for position:{position}"
        self.board = parent
        self.id= id
        self.x = position[1]
        self.y = position[0]
        self.orientation = orientation
        self.length = length
        self.colors = colors
    
    def getColors(self):
        return self.colors
    
    def mousePressEvent(self,event):
        print("hi")
        self.board.selectedCar = self.id


class Application(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(50, 50, 500, 500)
        self.setBaseSize(100, 100)
        self.grid = [[EMPTY]*PARKING_SIZE for _ in range(PARKING_SIZE)] # 0 for empty space, num for car
        self.cars = dict() #dictionary mapping carID to car object
        self.layout = QVBoxLayout()
        levels = os.listdir("./levels")
        self.comboBox = QComboBox()
        self.comboBox.addItems(levels)
        button = QPushButton("Load Level")
        button.clicked.connect(lambda:self.loadScenario(self.comboBox.currentText()))
        self.wonLabel = QLabel("You won !") 
        self.wonLabel.setAlignment(Qt.AlignCenter)
        spRetain = QSizePolicy()
        spRetain.setRetainSizeWhenHidden(True)
        self.wonLabel.setSizePolicy(spRetain)
        self.layout.addWidget(self.wonLabel)
        self.layout.addWidget(self.comboBox)
        self.layout.addWidget(button)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.drawSquares()
        self.layout.addLayout(self.gridLayout)
        self.setLayout(self.layout)
        self.selectedCar = None
        self.won = False
        self.updateGrid()

"""
create empty grid
"""
    def drawSquares(self):
        for row in range(PARKING_SIZE):
            for col in range(PARKING_SIZE):
                square = QWidget(self)
                square.setStyleSheet(f"background-color: rgb(100,100 ,100 )")
                square.setObjectName(str(row)+str(col))
                self.gridLayout.addWidget(square, row, col)


"""
update grid view based on car positions 
"""
    def updateGrid(self):
        if self.won:
            self.wonLabel.setHidden(False)
        else:
            self.wonLabel.setHidden(True)
        for row in range(PARKING_SIZE):
            for col in range(PARKING_SIZE):
                id = self.grid[row][col]
                if id !=0:
                    colors = self.cars[id].getColors()
                    self.gridLayout.itemAt(row*PARKING_SIZE+col).widget().setStyleSheet(f"background-color: rgb({colors[0]},{colors[1]} ,{colors[2]})")
                else:
                    self.gridLayout.itemAt(row*PARKING_SIZE+col).widget().setStyleSheet(f"background-color: rgb(100,100 ,100 )")

"""
check if space given parameters is free (no cars)
"""
    def isFree(self,y,x,length,orientation):
        for i in range(length):
            if self.grid[y+int(orientation==VERTICAL)*i][x+int(orientation==HORIZONTAL)*i]!=0:
                return False
        return True



    def keyPressEvent(self,event):
        car = self.cars.get(self.selectedCar,None)
        if car is None or self.won: 
            return
        if event.key() == Qt.Key_Z:
            if car.orientation == VERTICAL:
                self.moveCar(car,-1)
        elif event.key() == Qt.Key_S:
            if car.orientation == VERTICAL:
                self.moveCar(car,1)
        elif event.key() == Qt.Key_D:
            if car.orientation == HORIZONTAL:
                self.moveCar(car,1)
        elif event.key() == Qt.Key_Q:
            if car.orientation == HORIZONTAL:
                self.moveCar(car,-1)
        self.updateGrid()


"""
move car and check validity of move
Checks for win
@move: -1 or 1 (left or right, up or down)
"""
    def moveCar(self,car,move):
        if car.orientation == VERTICAL:  #vertical movement
            if move == 1: #down
                if (car.y+car.length) < PARKING_SIZE and self.grid[car.y+car.length][car.x] == 0:
                    self.grid[car.y+car.length][car.x] = self.grid[car.y][car.x]
                    self.grid[car.y][car.x] = 0
                    car.y+=1
            else: #up
                if (car.y-1) >= 0 and self.grid[car.y-1][car.x] == 0:
                    self.grid[car.y-1][car.x] = self.grid[car.y][car.x]
                    self.grid[car.y+car.length-1][car.x] = 0
                    car.y-=1
        else: #horizontal movement
            if move == 1: #right
                if  car.id == 1 and car.x >= (PARKING_SIZE-car.length):
                    self.won = True
                elif (car.x+car.length) < PARKING_SIZE and self.grid[car.y][car.x+car.length] == 0:
                    self.grid[car.y][car.x+car.length] = self.grid[car.y][car.x]
                    self.grid[car.y][car.x] = 0
                    car.x+=1
            else: #left
                if (car.x-1) >= 0 and self.grid[car.y][car.x-1] == 0:
                    self.grid[car.y][car.x-1] = self.grid[car.y][car.x]
                    self.grid[car.y][car.x+car.length-1] = 0
                    car.x-=1
        if not self.won:
            self.gridLayout.addWidget(car,car.y,car.x,1+int(car.orientation==VERTICAL)*(car.length-1),1+int(car.orientation==HORIZONTAL)*(car.length-1))
        self.updateGrid()

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

"""
loads cars from json scenario given as parameter and resets game
"""
    def loadScenario(self,scenario):
        self.won = False
        self.clearLayout(self.gridLayout)
        self.drawSquares()
        self.grid = [[EMPTY]*PARKING_SIZE for _ in range(PARKING_SIZE)] # 0 for empty space, num for car
        self.cars = dict()
        with open("./levels/"+scenario) as f:
            data = json.load(f)        
            for car in data["cars"]:
                self.spawnCar(int(car["carID"]),int(car["length"]),json.loads(car["position"]),int(car["orientation"]))
        self.updateGrid()

"""
spawn car at given parameters
pos is starting point as [y,x] grid coordinates
"""
    def spawnCar(self,carID,length,pos,orientation):
        colors = COLORS[carID]
        if self.isFree(pos[0],pos[1],length,orientation):
            car = Car(self,carID,length,pos,orientation,colors)
            self.cars[carID] = car
            self.gridLayout.addWidget(car,car.y,car.x,1+int(orientation==VERTICAL)*(length-1),1+int(orientation==HORIZONTAL)*(length-1))
            for i in range(length):
                if car.orientation==VERTICAL:
                    self.grid[car.y+i][car.x] = carID
                    
                else:
                    self.grid[car.y][car.x+i] = carID
        
            

if __name__ == "__main__":
    app = QApplication([])
    window = Application()
    window.show()
    sys.exit(app.exec())