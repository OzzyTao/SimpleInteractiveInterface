from PyQt4.QtGui import QGraphicsScene, QColor, QGraphicsLineItem
from PyQt4.QtCore import pyqtSignal, Qt, QLineF

class DragEnabledScene(QGraphicsScene):
	"""docstring for DragEnabledScene"""
	modelchanged = pyqtSignal()
	filterSet = pyqtSignal(list)

	def __init__(self,rect=None,parent=None):
		super(DragEnabledScene,self).__init__(rect,parent)
		self.movingState = 0
		self.mode = 0
		self.filterHandles = []
		self.pointerLine = None

	def mousePressEvent(self,event):
		if self.mode:
			self.clearFilterHandle()
			if self.pointerLine:
				self.removeItem(self.pointerLine)
			self.pointerLine = QGraphicsLineItem(QLineF(event.scenePos(),event.scenePos()))
			self.addItem(self.pointerLine)

		self.movingState = 1
		return super(DragEnabledScene,self).mousePressEvent(event)

	def mouseMoveEvent(self,event):
		if self.movingState:
			self.movingState = 2
			if self.mode and self.pointerLine:
				templine = self.pointerLine.line()
				templine.setP2(event.scenePos())
				self.pointerLine.setLine(templine)
		return super(DragEnabledScene,self).mouseMoveEvent(event)

	def mouseReleaseEvent(self,event):
		if self.mode:
			if self.movingState == 1 and self.pointerLine:
				self.removeItem(self.pointerLine)
				self.pointerLine = None
			elif self.movingState == 2:
				self.removeItem(self.pointerLine)
				item1 = self.itemAt(self.pointerLine.line().p1())
				item2 = self.itemAt(self.pointerLine.line().p2())
				if item1 and item2:
					self.filterHandles = [item1,item2]
					item1.changeFilterState(1)
					item2.changeFilterState(2)
					self.filterSet.emit(item1.model.leafIDs()+[0]+item2.model.leafIDs())
					self.addItem(self.pointerLine)
				else:
					self.pointerLine = None
		else:
			if self.movingState == 2:
				self.modelchanged.emit()
		self.movingState = 0
		return super(DragEnabledScene,self).mouseReleaseEvent(event)

	def setFilterMode(self,mode=1):
		if mode != self.mode:
			if mode:
				self.setBackgroundBrush(Qt.gray)
				for child in self.items():
					child.setEnabled(False)
			else:
				self.clearFilterHandle()
				self.filterSet.emit([0])
				self.setBackgroundBrush(Qt.white)
				for child in self.items():
					child.setEnabled(True)
			self.mode = mode
			

	def mouseDoubleClickEvent(self,event):
		self.clearFilterHandle()
		if self.mode:
			itemClicked = self.itemAt(event.scenePos())
			if itemClicked:
				self.filterHandles.append(itemClicked)
				itemClicked.changeFilterState(2)
				self.filterSet.emit(itemClicked.model.leafIDs()+[0]+itemClicked.model.leafIDs())
		return super(DragEnabledScene,self).mouseDoubleClickEvent(event)

	def clearFilterHandle(self):
		if self.filterHandles:
			for item in self.filterHandles:
				item.changeFilterState(0)
			self.filterHandles = []

