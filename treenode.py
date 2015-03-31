from PyQt4.QtGui import QColor
from PyQt4.QtCore import QRectF, QPointF, QLineF, Qt

class TreeNode(object):
	"""store data for a class and manage hierarchy"""
	def __init__(self, classid,name,rect=None,color=None,pos=None,accu = 1.0,parent=None):
		super(TreeNode, self).__init__()
		self.classid = classid
		self.name = name
		self.parent = parent
		self.accu = accu
		self.rect = QRectF(*rect) if rect else rect
		self.color = QColor(color) if color else color
		self.pos = QPointF(*pos) if pos else pos 
		self.children = []
		if parent:
			parent.children.append(self)

	# def __init__(self,jsonobj):
	# 	self.__init__(jsonobj['id'],jsonobj['name'],jsonobj['rect'],jsonobj['color'],jsonobj['pos'])
	# 	for child in jsonobj['children']:
	# 		childItem = TreeNode(child)
	# 		self.children.append(childItem)
	# 		childItem.parent = self

	def leafIDs(self):
		if self.isLeaf():
			return [self.classid]
		else:
			idgroup = []
			for child in self.children:
				idgroup += child.leafIDs()
			return idgroup

	def isLeaf(self):
		if self.children:
			return False
		else:
			return True

	def isRoot(self):
		if self.parent:
			return False
		else:
			return True

	def toJSON(self):
		jsonObj = {}
		jsonObj['id']= self.classid
		jsonObj['name'] = self.name
		jsonObj['rect'] = [self.rect.left(),self.rect.top(),self.rect.width(),self.rect.height()] if self.rect else self.rect
		jsonObj['color'] = str(self.color.name()) if self.color else self.color
		jsonObj['pos'] = [self.pos.x(),self.pos.y()] if isinstance(self.pos,QPointF) else self.pos
		jsonObj['accu'] = self.accu
		jsonObj['children'] = []
		for child in self.children:
			jsonObj['children'].append(child.toJSON())
		return jsonObj

	def __str__(self):
		tempstr = "%s   %s\n" % (self.classid,self.name)
		for child in self.children:
			tempstr+= '   '+str(child)
		return tempstr 

	def findNode(self,id):
		if self.classid == id:
			return self
		for child in self.children:
			result = child.findNode(id)
			if result:
				return result
		return None

	def toplogicalDistance(self,id1,id2):
		if id1==id2:
			return 0
		else:
			node1 = self.findNode(id1)
			node2 = self.findNode(id2)
			if node1 and node2:
				if node1.parent == node2.parent:
					return 1
				else:
					return 2
		return 0

	def matrixDistance(self,id1,id2):
		if id1==id2:
			return 0
		else:
			node1 = self.findNode(id1)
			node2 = self.findNode(id2)
			if node1 and node2:
					pos1 = node1.pos + node1.parent.pos
					pos2 = node2.pos + node2.parent.pos
					return QLineF(pos1,pos2).length()
		return 2000.0

	def transactionPossibility(self,id1,id2):
		node1 = self.findNode(id1)
		node2 = self.findNode(id2)
		if node1 and node2:
			return node1.accu * node2.accu
		else:
			return 1.0

	def renderInformation(self,fromclass,toclass):
		fromnode = self.findNode(fromclass)
		tonode = self.findNode(toclass)
		if fromnode and tonode:
			tDistance = 0 if fromnode==tonode else 1 if fromnode.parent == tonode.parent else 2
			mDistance = 0 if fromnode==tonode else QLineF(fromnode.pos+fromnode.parent.pos,tonode.pos+tonode.parent.pos).length()
			possibility = fromnode.accu*tonode.accu
			color = QColor(tonode.color)
			color.setAlphaF(tonode.accu)
		else:
			tDistance =2
			mDistance = 1000.0
			possibility = 1.0
			color = Qt.white
		return (tDistance,mDistance,possibility,color)


