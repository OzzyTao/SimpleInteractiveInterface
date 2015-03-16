from PyQt4.QtGui import QGraphicsItem, QGraphicsObject
from PyQt4.QtCore import QRectF, Qt, QPointF, pyqtSignal, QObject

class Position():
	TOPLEFT = 1
	TOPRIGHT = 2
	BOTTOMLEFT = 3
	BOTTOMRIGHT = 4

class ResizeHandle(QGraphicsObject):
	"""docstring for ResizeHandle"""
	def __init__(self, position ,parent):
		super(ResizeHandle, self).__init__(parent)
		self._parent = parent
		self._position = position
		self._resizeState = False
		# ser rect
		if position == Position.TOPLEFT:
			self._rect = QRectF(0,0,5,5)
		elif position == Position.TOPRIGHT:
			self._rect = QRectF(-5,0,5,5)
		elif position == Position.BOTTOMLEFT:
			self._rect = QRectF(0,-5,5,5)
		else:
			self._rect = QRectF(-5,-5,5,5)
		# set cursor
		if position == Position.TOPLEFT or position==Position.BOTTOMRIGHT:
			self.setCursor(Qt.SizeFDiagCursor)
		else:
			self.setCursor(Qt.SizeBDiagCursor)
		self.setPosition()

	def setPosition(self):
		if self._position == Position.TOPLEFT:
			self.setPos(self._parent.boundingRect().topLeft())
		elif self._position == Position.TOPRIGHT:
			self.setPos(self._parent.boundingRect().topRight())
		elif self._position == Position.BOTTOMLEFT:
			self.setPos(self._parent.boundingRect().bottomLeft())
		else:
			self.setPos(self._parent.boundingRect().bottomRight())

	def boundingRect(self):
		return self._rect

	def paint(self,painter,option,widget):
		painter.save()
		painter.setPen(Qt.SolidLine)
		painter.setBrush(Qt.black) 
		painter.drawRect(self._rect)
		painter.restore()

	def mousePressEvent(self,event):
		self._resizeState = True
		self._location = self.pos()
		event.accept()

	def mouseReleaseEvent(self,event):
		self._resizeState = False
		event.accept()

	def mouseMoveEvent(self,event):
		if self._resizeState:
			change = event.pos()-event.lastPos()
			if self._parent.resizeRect(self._position,self._location+change):
				self._location+=change
				self.prepareGeometryChange()
				self.setPos(self._location)
		event.accept()




if __name__=='__main__':
	from PyQt4.QtGui import QApplication, QGraphicsView, QGraphicsScene
	import sys
	app = QApplication(sys.argv)
	myview = QGraphicsView()
	myscene = QGraphicsScene(QRectF(-400,-300,800,600))
	myscene.addItem(ResizeHandle())
	myview.setScene(myscene)
	myview.show()

	app.exec_()
