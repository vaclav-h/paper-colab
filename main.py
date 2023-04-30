import os
import sys, math
import pickle
import numpy as np
import networkx as nx
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PySide6.QtGui import QBrush, QPen, QTransform, QPainter, QFont, QColor
from fr import FruchtermanReingold
from utils import map2color



class VisGraphicsScene(QGraphicsScene):
    def __init__(self):
        super(VisGraphicsScene, self).__init__()
        self.selection = None
        self.wasDragg = False
        self.pen = QPen(Qt.black)
        self.selected = QPen(Qt.red, 6)
        self.txt = None

    def mouseReleaseEvent(self, event): 
        if(self.wasDragg):
            return

        # Deselect node
        if(self.selection):
            self.selection.setPen(self.pen)
            if self.txt:
                self.removeItem(self.txt)
                self.txt = None
        item = self.itemAt(event.scenePos(), QTransform())
        if(item):
            # Select node, show outline and authors name
            if isinstance(item, QGraphicsEllipseItem):
                self.txt = self.addText(item.author_name, QFont("Helvetica", 100, QFont.Bold))
                ellipse_size = item.rect().width()
                self.txt.setPos(item.rect().left() + ellipse_size, item.rect().top())
                item.setPen(self.selected)
                self.selection = item

class VisGraphicsView(QGraphicsView):
    def __init__(self, scene, parent):
        super(VisGraphicsView, self).__init__(scene, parent)
        self.startX = 0.0
        self.startY = 0.0
        self.distance = 0.0
        self.myScene = scene
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        zoom = 1 + event.angleDelta().y()*0.001;
        self.scale(zoom, zoom)
        
    def mousePressEvent(self, event):
        self.startX = event.position().x()
        self.startY = event.position().y()
        self.myScene.wasDragg = False
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        endX = event.position().x()
        endY = event.position().y()
        deltaX = endX - self.startX
        deltaY = endY - self.startY
        distance = math.sqrt(deltaX*deltaX + deltaY*deltaY)
        if(distance > 5):
            self.myScene.wasDragg = True
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Visualization of collaboration on scientific papers')
        self.createGraphicView()
        self.setMinimumSize(800, 600)

    def createGraphicView(self):
        self.scene = VisGraphicsScene()
        self.view = VisGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setGeometry(0, 0, 800, 600)

    def draw_graph(self, G, pos, names):
        base_size = 15
        x = []
        y = []
        sizes = []
        for i in range(G.shape[0]):
            x.append(pos[i][0])
            y.append(pos[i][1])

            # Node sizes based on it's degree
            sizes.append(base_size * math.log(3 + np.count_nonzero(G[i])))

            # Draw edges first
            for j in range(i+1):
                if G[i][j] == 1:
                    self.scene.addLine(x[i]+sizes[i]/2,
                                       y[i]+sizes[i]/2,
                                       x[j]+sizes[j]/2,
                                       y[j]+sizes[j]/2,
                                       self.scene.pen)

        # Get mapping from nodes to colors based on the size of the component
        colors = map2color(G)

        # Draw the nodes
        for i in range(len(x)):
            ellipse = self.scene.addEllipse(x[i], y[i],
                                            sizes[i],
                                            sizes[i],
                                            self.scene.pen,
                                            QBrush(QColor.fromString(colors[i])))
            ellipse.author_name = names[i]

        self.view.fitInView(0,0, 350, 350, Qt.KeepAspectRatio)


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()

    # Load the network
    Gnx = nx.read_gml("netscience.gml")
    names = list(Gnx.nodes)
    G = nx.adjacency_matrix(Gnx).toarray()

    # Check if there is cached layout
    # Compute layout if there is none
    cached = os.path.isfile("layout.pkl")
    if cached:
        with open('layout.pkl', 'rb') as f:
            pos = pickle.load(f)
    else:
        fr = FruchtermanReingold(area=22,
                                 gravity=0.8,
                                 speed=0.01)
        print("Computing layout...")
        pos = fr.layout(G, iterations=2000, pos=None)
        with open('layout.pkl', 'wb') as f:
            pickle.dump(pos, f)

    # Draw the network
    ex.draw_graph(G, pos, names)
    ex.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
