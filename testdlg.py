from PyQt4.QtGui import QDialog, QVBoxLayout, QGraphicsScene, QGraphicsView, QHBoxLayout, QPushButton, QFileDialog, QStatusBar, QAction, QMenuBar, QKeySequence
from PyQt4.QtCore import QRectF, pyqtSignal
from data import data
from treenode import TreeNode
from nodegraphicsitem import NodeGraphicsItem
import json
from dragenabledscene import DragEnabledScene

class TestDlg(QDialog):
	"""docstring for TestDlg"""
	classDefChanged = pyqtSignal()
	def __init__(self, parent=None):
		super(TestDlg, self).__init__(parent)
		self.mymodel = None
		self.proxyModel = []
		self.myscene = DragEnabledScene(QRectF(-400,-300,800,600))
		self.myview = QGraphicsView()
		self.myview.setScene(self.myscene)
		self.myfile = None
		layout = QVBoxLayout()
		layout.addWidget(self.myview)
		# buttonLayout = QHBoxLayout()
		# self.savebutton = QPushButton('Save')
		# self.loadbutton = QPushButton('Load')
		# self.renderbutton = QPushButton('Accept')
		# buttonLayout.addWidget(self.savebutton)
		# buttonLayout.addWidget(self.loadbutton)
		# buttonLayout.addWidget(self.renderbutton)
		# layout.addLayout(buttonLayout)
		self.statusbar =  QStatusBar()
		layout.addWidget(self.statusbar)
		self.statusbar.showMessage("Ready.",2000)
		self.setLayout(layout)

		self.menuBar = QMenuBar(self)
		self.set_menubar()

		# self.savebutton.pressed.connect(self.saveMatrix)
		# self.loadbutton.pressed.connect(self.loadMatrix)
		self.myscene.selectionChanged.connect(self.updateStatus)
		self.myscene.modelchanged.connect(self.changeModel)

		# self.renderbutton.pressed.connect(self.testDistance)
		self.setWindowTitle("Class Relation Metaphor")
		self.loadfromInitData()

	def set_menubar(self):
		fileSaveAction = self.createAction("&Save as...",self.saveMatrix,QKeySequence.Save)
		fileLoadAction = self.createAction("&Open...",self.loadMatrix,QKeySequence.Open)
		fileMenu = self.menuBar.addMenu("&File")
		fileMenu.addAction(fileSaveAction)
		fileMenu.addAction(fileLoadAction)

	def updateProxyModel(self):
		self.proxyModel = {}
		for fromcalss in self._classIDs:
			row = {}
			for toclass in self._classIDs:
				tD, mD, P, C = self.mymodel.renderInformation(fromcalss,toclass)
				# combine transparency 
				C.setAlphaF(P)
				
				width = 0.7 if tD==2 else 1.4 if tD==1 else 2.0
				distance = mD/100.0+2
				possibility = P*100.0
				row[toclass] = (width,distance,possibility,C)
			self.proxyModel[fromcalss]=row


	# def testDistance(self):
	# 	print "Toplogical Distance:",self.mymodel.toplogicalDistance(1,10)
	# 	print "Matrix Distance:",self.mymodel.matrixDistance(1,10)
	# 	print "Posibility:", self.mymodel.transactionPossibility(1,10)
	def fetchRenderInfo(self,fromclass,toclass,type):
		try:
			fromclass = int(fromclass)
			toclass = int(toclass)
		except:
			return None
		return self.proxyModel[fromclass][toclass][type]
		# if isinstance(fromclass,int) and isinstance(toclass,int):
		# 	return self.proxyModel[fromclass][toclass][type]
		# return None

	def changeModel(self):
		self.updateProxyModel()
		self.classDefChanged.emit()

	def updateStatus(self):
		items = self.myscene.selectedItems()
		message = " "
		if items and isinstance(items[0],NodeGraphicsItem):
			message = items[0].model.name
		self.statusbar.showMessage(message)

	def loadfromInitData(self): 
		self._classIDs = []
		rootNode = TreeNode(0,'root')
		tempid = 100
		for key in data:
			parentNode = TreeNode(tempid,key,parent=rootNode)
			for leaf in data[key]:
				self._classIDs.append(leaf[0])
				leafNode = TreeNode(leaf[0],leaf[1],color=leaf[2],accu=leaf[3],parent=parentNode)
			tempid += 1
		self.mymodel = rootNode

		# self._classIDDict = {}
		# for i in range(len(self._classIDs)):
		# 	self._classIDDict[self._classIDs[i]]=i
		for node in self.mymodel.children:
			self.myscene.addItem(NodeGraphicsItem(node))

		self.changeModel()

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
				rootNode = TreeNode(rawobj['id'],rawobj['name'],rawobj['rect'],rawobj['color'],rawobj['pos'],rawobj['accu'])
				for child in rawobj['children']:
					parentNode = TreeNode(child['id'],child['name'],child['rect'],child['color'],child['pos'],child['accu'],rootNode)
					for leaf in child['children']:
						leafNode = TreeNode(leaf['id'],leaf['name'],leaf['rect'],leaf['color'],leaf['pos'],leaf['accu'],parentNode)
				self.mymodel = rootNode

				self.myscene.clear()
				for node in self.mymodel.children:
					self.myscene.addItem(NodeGraphicsItem(node))
		self.changeModel()

	def createAction(self,text,slot=None,shortcut=None,icon=None,tip=None,checkable=False):
		action = QAction(text,self)
		if icon:
			action.setIcon(icon)
		if shortcut:
			action.setShortcut(shortcut)
		if tip:
			action.setToolTip(tip)
			action.setStatusTip(tip)
		if slot:
			action.triggered.connect(slot)
		if checkable:
			action.setCheckable(True)
		return action




if __name__ == '__main__':
	from PyQt4.QtGui import QApplication
	import sys
	app = QApplication(sys.argv)
	mydlg = TestDlg()
	mydlg.show()
	app.exec_()	