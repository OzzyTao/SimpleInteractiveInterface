from PyQt4.QtGui import QWidget, QFont, QFontMetricsF, QPainter, QPalette, QColor, QSizePolicy
from PyQt4.QtCore import QSize, Qt, QPointF, pyqtSignal, QLineF

class DoubleSlider(QWidget):
	"""docstring for DoubleSlider"""
	WSTRING = "1996"
	valueChanged = pyqtSignal(str,str)
	def __init__(self,valuerange,continuous = True,parent=None):
		super(DoubleSlider, self).__init__(parent)
		self.range = valuerange
		self._isContinuous = continuous
		self._start = 0
		self._end = 100
		self._selected = 0
		if self._isContinuous:
			self.labels = [(0,str(self.range[0])),(100,str(self.range[1]))]
		else:
			self.labels = []
			num = len(self.range)
			for i in range(num):
				self.labels.append((i*100.0/(num-1),str(self.range[i])))
		self.setFocusPolicy(Qt.WheelFocus)
		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed))

	def value(self):
		startvalue = (self.range[1]-self.range[0])/100*self._start+self.range[0]
		endvalue = (self.range[1]-self.range[0])/100*self._end+self.range[0]
		if not self._isContinuous:
			startvalue = [x[1] for x in self.labels if x[0]==startvalue][0]
			endvalue = [x[1] for x in self.labels if x[0]==endvalue][0]
		return  str(startvalue), str(endvalue)

	def setValue(self,startvalue,endvalue):
		if self.range[0]<=startvalue<=endvalue<=self.range[1]:
			self._start = (startvalue-self.range[0])/(self.range[1]-self.range[0])*100 
			self._end = (endvalue-self.range[0])/(self.range[1]-self.range[0])*100
			self.update()
			self.updateGeometry()
			return True
		else:
			return False


	def paintEvent(self,event=None):
		font = QFont(self.font())
		fm = QFontMetricsF(font)
		handleDiameter = fm.height()
		boundingRect = self.rect()
		margin = handleDiameter
		barHeight = handleDiameter -4
		barWidth = boundingRect.width()-2*margin
		startX = barWidth/100.0 * self._start
		startPoint = QPointF(startX+margin,margin/2+barHeight/2)
		endX = barWidth/100.0 * self._end
		endPoint = QPointF(endX+margin,margin/2+barHeight/2)

		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setRenderHint(QPainter.TextAntialiasing)
		painter.setPen(self.palette().color(QPalette.Mid))
		painter.setBrush(self.palette().brush(QPalette.AlternateBase))
		painter.drawRect(self.rect())

		barColor = Qt.lightGray
		outlineColor = Qt.gray
		activeBarColor = Qt.blue
		painter.setPen(outlineColor)
		painter.setBrush(barColor)
		painter.drawRect(margin,margin/2,barWidth,barHeight)
		painter.setBrush(activeBarColor)
		painter.drawRect(margin+startX,margin/2,endX-startX,barHeight)

		painter.setPen(Qt.black)
		for label in self.labels:
			x = label[0]/100.0*barWidth+margin-fm.width(label[1])/2.0
			y = boundingRect.bottom() - margin/2 
			painter.drawText(QPointF(x,y),label[1])
			painter.drawLine(label[0]/100.0*barWidth+margin,margin/2+barHeight,label[0]/100.0*barWidth+margin,y-fm.height()+1)

		handleColor = QColor(Qt.blue).dark()
		painter.setBrush(handleColor)
		painter.setPen(Qt.green)
		painter.drawEllipse(startPoint,handleDiameter/2,handleDiameter/2)
		painter.setPen(Qt.red)
		painter.drawEllipse(endPoint,handleDiameter/2,handleDiameter/2)


	def mousePressEvent(self,event):
		if event.button() == Qt.LeftButton:
			font = QFont(self.font())
			fm = QFontMetricsF(font)
			handleDiameter = fm.height()
			boundingRect = self.rect()
			margin = handleDiameter
			barHeight = handleDiameter -4
			barWidth = boundingRect.width()-2*margin
			startX = barWidth/100.0 * self._start
			startPoint = QPointF(startX+margin,margin/2+barHeight/2)
			endX = barWidth/100.0 * self._end
			endPoint = QPointF(endX+margin,margin/2+barHeight/2)
			if QLineF(startPoint,event.posF()).length()<handleDiameter/2:
				self._selected = 1
			elif QLineF(endPoint,event.posF()).length()<handleDiameter/2:
				self._selected = 2
		return super(DoubleSlider,self).mousePressEvent(event)

	def mouseMoveEvent(self,event):
		if self._selected:
			font = QFont(self.font())
			fm = QFontMetricsF(font)
			handleDiameter = fm.height()
			boundingRect = self.rect()
			margin = handleDiameter
			barHeight = handleDiameter -4
			barWidth = boundingRect.width()-2*margin
			startX = barWidth/100.0 * self._start
			startPoint = QPointF(startX+margin,margin/2+barHeight/2)
			endX = barWidth/100.0 * self._end
			endPoint = QPointF(endX+margin,margin/2+barHeight/2)
			if self._selected == 1:
				if event.x()< margin:
					self._start = self.labels[0][0]
				elif margin<=event.x()< margin+endX - handleDiameter:
					self._start = (event.x()-margin)/float(barWidth)*100
				else:
					self._start = (endX - handleDiameter)/float(barWidth)*100
			else:
				if event.x()>barWidth+margin:
					self._end = 100
				elif startX+margin+ handleDiameter < event.x()<= barWidth + margin :
					self._end = (event.x()-margin)/float(barWidth)*100
				else:
					self._end = (startX + handleDiameter)/float(barWidth)*100
			self.update()
			self.updateGeometry()
		return super(DoubleSlider,self).mouseMoveEvent(event)

	def _numToLevel(self, x, labels):
		num = len(labels)
		level = 0
		for i in range(num):
			if x>labels[i][0]:
				level = i
		if level < num-1:
			if labels[level+1][0]-x > x - labels[level][0]:
				return labels[level][0]
			else:
				return labels[level+1][0]
		else:
			return labels[level][0]


	def mouseReleaseEvent(self, event):
		if self._selected:
			if not self._isContinuous:
				font = QFont(self.font())
				fm = QFontMetricsF(font)
				handleDiameter = fm.height()
				boundingRect = self.rect()
				margin = handleDiameter
				barWidth = boundingRect.width()-2*margin
				if self._selected == 1:
					self._start = self._numToLevel((event.x()-margin)/float(barWidth)*100,[x for x in self.labels if x[0]<self._end])
				elif self._selected ==2:
					self._end = self._numToLevel((event.x()-margin)/float(barWidth)*100,[x for x in self.labels if x[0]>self._start])
				self.update()
				self.updateGeometry()
				value1 = [x[1] for x in self.labels if x[0]==self._start]
				value2 = [x[1] for x in self.labels if x[0]==self._end]
				self.valueChanged.emit(value1[0],value2[0])
			else:
				value1 = self.range[0]+(self.range[1]-self.range[0])*self._start/100.0
				value2 = self.range[0]+(self.range[1]-self.range[0])*self._end/100.0
				self.valueChanged.emit(str(value1),str(value2))
			self._selected = 0
		return super(DoubleSlider,self).mousePressEvent(event)


	def sizeHint(self):
		return self.minimumSizeHint()

	def minimumSizeHint(self):
		font = QFont(self.font())
		fm = QFontMetricsF(font)
		return QSize(fm.width(DoubleSlider.WSTRING)*6,fm.height()*3)


if __name__ == '__main__':
	from PyQt4.QtGui import QApplication
	import sys
	myapp = QApplication(sys.argv)
	mydouble = DoubleSlider([1996,2001,2008,2012],False)
	mydouble.show()
	myapp.exec_()

		