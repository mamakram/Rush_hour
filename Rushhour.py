import sys
import os
import random
import json
from PySide6.QtWidgets import QApplication, QFrame,QGridLayout,QVBoxLayout,QHBoxLayout,QWidget,QSizePolicy,QComboBox,QPushButton,QLabel,QSizePolicy,QGraphicsOpacityEffect
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
        self.qcolor = QColor(colors[0],colors[1],colors[2])
        self.child = QWidget(self)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.animation_group = QSequentialAnimationGroup(self)
        animation1 = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation1.setDuration(500)
        animation1.setStartValue(1)
        animation1.setEndValue(0.7)
        self.animation_group.addAnimation(animation1)
        # Second animation: pulse from 1 to 0.5
        animation2 = QPropertyAnimation(self.opacity_effect, b"opacity")
        animation2.setDuration(500)
        animation2.setStartValue(0.7)
        animation2.setEndValue(1)
        self.animation_group.addAnimation(animation2)

        # Set animation group to loop indefinitely
        self.animation_group.setLoopCount(-1)
        self.opacity_effect.setOpacity(1)


    def getColors(self):
        return self.colors
    
    def mousePressEvent(self,event):
        if self.board.selectedCar is not None:
            self.board.cars[self.board.selectedCar].deselect()
        self.board.selectedCar = self.id
        self.select()
    

    def select(self):
        self.animation_group.start()
        #self.anim_2 = QPropertyAnimation(self.effect, b"opacity")
        #self.anim_2.setStartValue(1)
        #self.anim_2.setEndValue(0)
        #self.anim_2.setDuration(10000)
        #self.anim_2.start()

    def deselect(self):
        self.animation_group.stop()
        self.opacity_effect.setOpacity(1)

    def paintEvent(self,event):
        p = QPainter(self)
        p.fillRect(event.rect(),self.qcolor)


class Application(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(50, 50, 600, 500)
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
        self.gridLayout.setSpacing(1)
        instructionsLayout = QVBoxLayout()
        label1 = QLabel("Select Car with Mouse") 
        label2 = QLabel("use Z Q S D to \n move the Car") 
        label1.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
        label2.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding)
        instructionsLayout.addWidget(label1)
        instructionsLayout.addWidget(label2)
        wrapper = QHBoxLayout() 
        wrapper.addLayout(self.gridLayout)
        wrapper.addLayout(instructionsLayout)
        self.drawSquares()
        self.layout.addLayout(wrapper)
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
                square.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
                square.setStyleSheet(f"background-color: rgb(100,100 ,100 );border: 1px solid; border-color: white;")
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
                    #self.gridLayout.itemAt(row*PARKING_SIZE+col).widget().setStyleSheet(f"background-color: rgb({colors[0]},{colors[1]} ,{colors[2]})")
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
        else:
            player = self.cars[1]
            for i in range(player.length):
                self.grid[player.y + int(player.orientation==VERTICAL)*(i)][player.x + int(player.orientation==HORIZONTAL)*(i)] = 0
            #self.gridLayout.removeWidget(player)
            player.deleteLater()
        
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
        self.selectedCar = None
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