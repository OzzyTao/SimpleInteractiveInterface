from PyQt4.QtGui import QDialog, QVBoxLayout, QGraphicsScene, QGraphicsView, QHBoxLayout, QPushButton, QFileDialog, QStatusBar
from PyQt4.QtCore import QRectF
from data import data
from treenode import TreeNode
from nodegraphicsitem import NodeGraphicsItem
import json

class TestDlg(QDialog):
	"""docstring for TestDlg"""
	def __init__(self, parent=None):
		super(TestDlg, self).__init__(parent)
		self.mymodel = None
		self.myscene = QGraphicsScene(QRectF(-400,-300,800,600))
		self.myview = QGraphicsView()
		self.myview.setScene(self.myscene)
		self.myfile = None
		layout = QVBoxLayout()
		layout.addWidget(self.myview)
		buttonLayout = QHBoxLayout()
		self.savebutton = QPushButton('Save')
		self.loadbutton = QPushButton('Load')
		self.renderbutton = QPushButton('Accept')
		buttonLayout.addWidget(self.savebutton)
		buttonLayout.addWidget(self.loadbutton)
		buttonLayout.addWidget(self.renderbutton)
		layout.addLayout(buttonLayout)
		self.statusbar =  QStatusBar()
		layout.addWidget(self.statusbar)
		self.statusbar.showMessage("Ready.",2000)
		self.setLayout(layout)

		self.loadfromInitData()

		self.savebutton.pressed.connect(self.saveMatrix)
		self.loadbutton.pressed.connect(self.loadMatrix)
		self.myscene.selectionChanged.connect(self.updateStatus)
		self.renderbutton.pressed.connect(self.testDistance)

	def testDistance(self):
		print "Toplogical Distance:",self.mymodel.toplogicalDistance(1,10)
		print "Matrix Distance:",self.mymodel.matrixDistance(1,10)

	def updateStatus(self):
		items = self.myscene.selectedItems()
		message = " "
		if items and isinstance(items[0],NodeGraphicsItem):
			message = items[0].model.name
		self.statusbar.showMessage(message)

	def loadfromInitData(self): 
		rootNode = TreeNode(0,'root')
		tempid = 100
		for key in data:
			parentNode = TreeNode(tempid,key,parent=rootNode)
			for leaf in data[key]:
				leafNode = TreeNode(leaf[0],leaf[1],parent=parentNode)
			tempid += 1
		self.mymodel = rootNode

		for node in self.mymodel.children:
			self.myscene.addItem(NodeGraphicsItem(node))

	def saveMatrix(self):
		path = '.'
		fname = QFileDialog.getSaveFileName(self,"Save class relation",path,'class relation file (*.crf)')
		if fname:
			if not "." in fname:
				fname+='.crf'
			self.myfile = fname
			with open(fname,'w') as savefile:
				savefile.write(json.dumps(self.mymodel.toJSON()))

	def loadMatrix(self):
		path = '.'
		fname = QFileDialog.getOpenFileName(self,"Load class relation",path,'class relation file (*.crf)')
		if fname:
			if not "." in fname:
				fname += '.crf'
			self.myfile = fname
			with open(fname,'r') as loadfile:
				rawobj = json.loads(loadfile.read())
				rootNode = TreeNode(rawobj['id'],rawobj['name'],rawobj['rect'],rawobj['color'],rawobj['pos'])
				for child in rawobj['children']:
					parentNode = TreeNode(child['id'],child['name'],child['rect'],child['color'],child['pos'],rootNode)
					for leaf in child['children']:
						leafNode = TreeNode(leaf['id'],leaf['name'],leaf['rect'],leaf['color'],leaf['pos'],parentNode)
				self.mymodel = rootNode

				self.myscene.clear()
				for node in self.mymodel.children:
					self.myscene.addItem(NodeGraphicsItem(node))



if __name__ == '__main__':
	from PyQt4.QtGui import QApplication
	import sys
	app = QApplication(sys.argv)
	mydlg = TestDlg()
	mydlg.show()
	app.exec_()	