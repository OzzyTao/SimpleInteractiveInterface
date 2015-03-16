from PyQt4.QtGui import QGraphicsItem, QColor, QBrush, QTextOption, QPainter, QPen 
from PyQt4.QtCore import QRect, qrand, Qt, QRectF, QPointF
from resizehandle import ResizeHandle, Position

class NodeGraphicsItem(QGraphicsItem):
	"""Graphics Item of a node, supporting resizing"""
	LEAFSIZE = (30,20)
	PARENTSIZE = (150,100)
	def __init__(self, model,parent=None):
		super(NodeGraphicsItem, self).__init__(parent)
		self.loadModel(model)
		self.setCursor(Qt.PointingHandCursor)
		self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemClipsChildrenToShape | QGraphicsItem.ItemSendsGeometryChanges)

	def loadModel(self,model):
		self.model = model
		# set size and position based on the position of the node in the tree, also load data comes with model
		if not model.rect:
			if model.isLeaf():
				self.model.rect = QRectF(-NodeGraphicsItem.LEAFSIZE[0]/2,-NodeGraphicsItem.LEAFSIZE[1]/2,*NodeGraphicsItem.LEAFSIZE)
			else:
				self.model.rect = QRectF(-NodeGraphicsItem.PARENTSIZE[0]/2,-NodeGraphicsItem.PARENTSIZE[1]/2,*NodeGraphicsItem.PARENTSIZE)
		if model.isLeaf():
			self._resizable = False
		else:
			self._resizable = True
			self.setResizeHandle()

		# if model.isLeaf():
		# 	self._rect = QRectF(-NodeGraphicsItem.LEAFSIZE[0]/2,-NodeGraphicsItem.LEAFSIZE[1]/2,*NodeGraphicsItem.LEAFSIZE)
		# 	self._resizable = False
		# elif model.rect:
		# 	self._rect = model.rect
		# 	self._resizable =True
		# 	self.setResizeHandle()
		# else:
		# 	self._rect = QRectF(-NodeGraphicsItem.PARENTSIZE[0]/2,-NodeGraphicsItem.PARENTSIZE[1]/2,*NodeGraphicsItem.PARENTSIZE)
		# 	self._resizable = True
		# 	self.setResizeHandle()

		if model.pos:
			self.setPos(model.pos)

		if not model.color:
			self.model.color = QColor(qrand()%256,qrand()%256,qrand()%256) if model.isLeaf() else QColor(Qt.lightGray)
		# if model.color:
		# 	self._color = model.color
		# else:
		# 	self._color = QColor(qrand()%256,qrand()%256,qrand()%256) if model.isLeaf() else Qt.lightGray
		# recurcively load a model
		if not model.isLeaf():
			for child in model.children:
				childitem = NodeGraphicsItem(child,self)

	def boundingRect(self):
		return self.model.rect

	def paint(self,painter,option,widget):
		drawingRect = self.model.rect.adjusted(2,2,-2,-2)
		
		painter.save()
		painter.setRenderHint(QPainter.Antialiasing,True)
		if self.isSelected():
			pen = QPen(Qt.DashLine)
			pen.setWidth(2)
			pen.setColor(Qt.blue)
		else:
			pen = QPen(Qt.SolidLine)
			pen.setWidth(1)
			pen.setColor(Qt.gray)
		painter.setPen(pen)
		painter.setBrush(QBrush(self.model.color))
		painter.drawRoundedRect(drawingRect,5,5)
		painter.setPen(Qt.SolidLine)
		painter.drawText(drawingRect,str(self.model.classid),QTextOption(Qt.AlignCenter))
		painter.restore()

	def setResizeHandle(self):
		self._topleftHandle = ResizeHandle(Position.TOPLEFT,self)
		self._toprightHandle = ResizeHandle(Position.TOPRIGHT,self)
		self._bottomleftHandle = ResizeHandle(Position.BOTTOMLEFT,self)
		self._bottomrightHandle = ResizeHandle(Position.BOTTOMRIGHT,self)
		self.enableHandle(False)

	def updateHandle(self):
		self._topleftHandle.setPosition()
		self._toprightHandle.setPosition()
		self._bottomleftHandle.setPosition()
		self._bottomrightHandle.setPosition()
	
	def enableHandle(self,state):
		for handle in [self._topleftHandle,self._toprightHandle,self._bottomleftHandle,self._bottomrightHandle]:
			handle.setEnabled(state)
			handle.setVisible(state)

	def childClassesRect(self):
		childClasses = [x for x in self.childItems() if isinstance(x,NodeGraphicsItem)]
		baseRect = None
		if childClasses:
			for childitem in childClasses:
				baseRect = baseRect | childitem.mapRectToParent(childitem.boundingRect()) if baseRect else childitem.mapRectToParent(childitem.boundingRect())
		return baseRect

	def resizeRect(self,handle,newpos):
		newRect = self.model.rect.adjusted(0,0,0,0)
		if handle == Position.TOPLEFT:
			newRect.setTopLeft(newpos)
		elif handle == Position.TOPRIGHT:
			newRect.setTopRight(newpos)
		elif handle == Position.BOTTOMLEFT:
			newRect.setBottomLeft(newpos)
		else:
			newRect.setBottomRight(newpos)
		childItemRect = self.childClassesRect()
		if childItemRect and not newRect.contains(childItemRect):
			return False
		else:
			self.prepareGeometryChange()
			self.model.rect = newRect
			self.updateHandle()
			return True

	def itemChange(self,change,value):
		if change == QGraphicsItem.ItemSelectedHasChanged and self._resizable:
			self.enableHandle(value.toBool())
		elif change == QGraphicsItem.ItemPositionChange:
			previousPos = self.pos()
			value = value.toPointF()
			# check possible collision with parent and siblings
			if self.parentItem():
				#leaf classes
				parentItem = self.parentItem()
				onSceneParentRect = parentItem.boundingRect()
				mappedParentRect = parentItem.mapRectToItem(parentItem,onSceneParentRect)
				x = value.x()
				if x < mappedParentRect.left()+NodeGraphicsItem.LEAFSIZE[0]/2:
					x = mappedParentRect.left()+NodeGraphicsItem.LEAFSIZE[0]/2
				elif x>mappedParentRect.right()-NodeGraphicsItem.LEAFSIZE[0]/2:
					x = mappedParentRect.right()-NodeGraphicsItem.LEAFSIZE[0]/2
				y= value.y()
				if y < mappedParentRect.top()+NodeGraphicsItem.LEAFSIZE[1]/2:
					y = mappedParentRect.top()+NodeGraphicsItem.LEAFSIZE[1]/2
				elif y > mappedParentRect.bottom()-NodeGraphicsItem.LEAFSIZE[1]/2:
					y = mappedParentRect.bottom()-NodeGraphicsItem.LEAFSIZE[1]/2
				value  = QPointF(x,y)

			# collidingItems = self.collidingItems()
			# for item in collidingItems:
			# 	if item.parentItem()!=self and self.parentItem()!=item:
			# 		value = previousPos
		elif change == QGraphicsItem.ItemPositionHasChanged:
			self.model.pos = value.toPointF()

		return super(NodeGraphicsItem,self).itemChange(change,value)

	# def updateModel(self):
	# 	self.model.rect = self.boundingRect()
	# 	self.model.pos = self.pos()
	# 	self.model.color = self._color




if __name__ == '__main__':
	from PyQt4.QtGui import QApplication, QGraphicsView, QGraphicsScene
	from treenode import TreeNode
	import sys
	app = QApplication(sys.argv)
	myview = QGraphicsView()
	myscene = QGraphicsScene(QRectF(-400,-300,800,600))
	myview.setScene(myscene)
	rootnode = TreeNode(0,'root')
	parentnode = TreeNode(1,'grass land',parent=rootnode)
	leafnode = TreeNode(2,'grass 1',parent=parentnode)
	# leafnode2 = TreeNode(3,'earth',parent=parentnode)
	myscene.addItem(NodeGraphicsItem(parentnode))
	myview.show()
	app.exec_()



