from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import pyqtSignal

class DragEnabledScene(QGraphicsScene):
	"""docstring for DragEnabledScene"""
	modelchanged = pyqtSignal()
	def __init__(self,rect=None,parent=None):
		super(DragEnabledScene,self).__init__(rect,parent)
		self.movingState = 0

	def mousePressEvent(self,event):
		self.movingState = 1
		return super(DragEnabledScene,self).mousePressEvent(event)

	def mouseMoveEvent(self,event):
		if self.movingState:
			self.movingState = 2
		return super(DragEnabledScene,self).mouseMoveEvent(event)

	def mouseReleaseEvent(self,event):
		if self.movingState == 2:
			self.movingState=0
			self.modelchanged.emit()
		return super(DragEnabledScene,self).mouseReleaseEvent(event)

	
