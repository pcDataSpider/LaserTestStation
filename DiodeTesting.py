
import time
import wx
#import os
#import pickle
import newDevice
import PowerCurve
import tests

import logger
import graph
from scipy import stats


title = "Diode Testing"
description = "Wizard to create a new device"




def run_tool(window_parent, device):
	wnd = DiodeTestingGUI(window_parent, device)
	wnd.Show()




# class to hold the widgets for each procedure
class StepControls():
	def __init__(self, name, startBtn, check, idx):
		self.name = name
		self.startBtn = startBtn
		self.check = check
		self.idx = idx

# GUI 'home screen' for all diode test procedures
class DiodeTestingGUI ( wx.Frame ):
	

	def __init__( self, parent, device ):
		parent = None
		self.diode = None
		self.parent = parent
		self.device = device



		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Diode Testing", pos = wx.DefaultPosition, size = wx.Size( 466,329 ) )
		self.tests = [ tests.InitialTest(), tests.CoupleProcedure() ]

		self.steps  =[ ("Initial Diode Test",self.onP1), ("Diode Coupling",self.onP2), ("Test Module",self.onP3), ("Burn In",self.onP4), ("Final Test",self.onP5), ("Test With BHead",self.onP6) ]
		self.stepControls = []

		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		panelSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		leftSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		leftSizer.AddSpacer( ( 0, 10), 0, wx.EXPAND, 5 )
		
		self.topLine = wx.StaticLine( self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		leftSizer.Add( self.topLine, 0, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		
		infoSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		infoNameSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.modelTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Model:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.modelTxt.Wrap( -1 )
		self.modelTxt.Enable( False )
		
		infoNameSizer.Add( self.modelTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
		
		self.serNumTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Serial Number:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.serNumTxt.Wrap( -1 )
		self.serNumTxt.Enable( False )
		
		infoNameSizer.Add( self.serNumTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
		
		self.waveLenTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Wave Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.waveLenTxt.Wrap( -1 )
		self.waveLenTxt.Enable( False )
		
		infoNameSizer.Add( self.waveLenTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
		
		self.initCurTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Initial Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.initCurTxt.Wrap( -1 )
		self.initCurTxt.Enable( False )
		
		infoNameSizer.Add( self.initCurTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
		
		self.maxCurTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Max Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.maxCurTxt.Wrap( -1 )
		self.maxCurTxt.Enable( False )
		
		infoNameSizer.Add( self.maxCurTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
			
		self.stepSizeTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Step Size:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stepSizeTxt.Wrap( -1 )
		self.stepSizeTxt.Enable( False )
		
		infoNameSizer.Add( self.stepSizeTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
		
		infoSizer.Add( infoNameSizer, 1, 0, 5 )
		
		infoDataSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.modelNum = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.modelNum.Wrap( -1 )
		infoDataSizer.Add( self.modelNum, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )
		
		self.serNum = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.serNum.Wrap( -1 )
		infoDataSizer.Add( self.serNum, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )
		
		self.wavLen = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.wavLen.Wrap( -1 )
		infoDataSizer.Add( self.wavLen, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )
		
		self.initCur = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.initCur.Wrap( -1 )
		infoDataSizer.Add( self.initCur, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )
		
		self.maxCur = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.maxCur.Wrap( -1 )
		infoDataSizer.Add( self.maxCur, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )

		self.stepSize = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stepSize.Wrap( -1 )
		infoDataSizer.Add( self.stepSize, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )
		
		infoSizer.Add( infoDataSizer, 1, wx.EXPAND, 5 )
		
		leftSizer.Add( infoSizer, 0, wx.EXPAND|wx.RIGHT, 5 )
		
		self.botLine = wx.StaticLine( self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		leftSizer.Add( self.botLine, 0, wx.EXPAND|wx.ALL, 5 )
		
		controlSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		controlSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.newBtn = wx.Button( self.panel, wx.ID_ANY, u"New", wx.DefaultPosition, wx.DefaultSize, 0 )
		controlSizer.Add( self.newBtn, 0, wx.ALL, 5 )
		
		self.loadBtn = wx.Button( self.panel, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		controlSizer.Add( self.loadBtn, 0, wx.ALL, 5 )
		
		
		controlSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		leftSizer.Add( controlSizer, 1, wx.EXPAND, 5 )
		
		panelSizer.Add( leftSizer, 1, wx.EXPAND, 5 )
		
		self.vertLine = wx.StaticLine( self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		panelSizer.Add( self.vertLine, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )
		
		rightSizer = wx.BoxSizer( wx.VERTICAL )
		
		# create the right side controls
		idx = 0
		for n in self.tests:
			stepSizer = wx.BoxSizer( wx.HORIZONTAL )

			stepSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
			stepNameTxt = wx.StaticText( self.panel, wx.ID_ANY, n.name, wx.DefaultPosition, wx.DefaultSize, 0 )
			stepNameTxt.Wrap( -1 )
			stepNameTxt.Enable( False )
			stepSizer.Add( stepNameTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
			stepStartBtn = wx.Button( self.panel, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
			stepStartBtn.Enable( False )
			stepSizer.Add( stepStartBtn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
			stepCheck = wx.CheckBox( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
			stepCheck.Enable( False )
		
			stepSizer.Add( stepCheck, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 10 )
		
			rightSizer.Add( stepSizer, 0, wx.EXPAND, 5 )
			# add controls to the list
			controls = StepControls( stepNameTxt, stepStartBtn, stepCheck, idx)
			self.stepControls.append( controls )
			idx+=1
			# bind button
			def func(event):
				self.startTest( idx, n )
			stepStartBtn.Bind( wx.EVT_BUTTON, func )

	
		# create the right side controls
	#	idx=0
	#	for n in self.steps:
	#		stepSizer = wx.BoxSizer( wx.HORIZONTAL )
	#		stepSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
	#		stepNameTxt = wx.StaticText( self.panel, wx.ID_ANY, n[0], wx.DefaultPosition, wx.DefaultSize, 0 )
	#		stepNameTxt.Wrap( -1 )
	#		stepNameTxt.Enable( False )
	#		stepSizer.Add( stepNameTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
	#	
	#		stepStartBtn = wx.Button( self.panel, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
	#		stepStartBtn.Enable( False )
	#		stepSizer.Add( stepStartBtn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
	#	
	#		stepCheck = wx.CheckBox( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
	#		stepCheck.Enable( False )
	#	
	#		stepSizer.Add( stepCheck, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 10 )
	#	
	#		rightSizer.Add( stepSizer, 0, wx.EXPAND, 5 )
	#		# add controls to the list
	#		controls = StepControls( stepNameTxt, stepStartBtn, stepCheck, idx)
	#		self.stepControls.append( controls )
	#		idx+=1
	#		# bind button
	#		stepStartBtn.Bind( wx.EVT_BUTTON, n[1] )

		
	
		
		panelSizer.Add( rightSizer, 1, wx.EXPAND, 5 )
		
		self.panel.SetSizer( panelSizer )
		self.panel.Layout()
		panelSizer.Fit( self.panel )
		mainSizer.Add( self.panel, 1, wx.EXPAND, 5 )
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		#self.Centre( wx.BOTH )
		
		# Connect Events
		self.newBtn.Bind( wx.EVT_BUTTON, self.onNew )
		self.loadBtn.Bind( wx.EVT_BUTTON, self.onLoad )
	
	# Window event handlers
	def onNew( self, event ):
		old = self.diode
		self.diode = newDevice.newDevice(self.device)
		if self.diode is None:
			self.diode = old
		self.refresh()

	
	def onLoad( self, event ):
		old = self.diode
		self.diode = newDevice.loadDevice(self.device)
		if self.diode is None:
			self.diode = old
		self.refresh()



	def refresh(self):
		''' refreshes the GUI info and controls, and saves the diode object '''
		# enable controls
		enable = False
		if self.diode is not None:
			enable = True
			print self.diode.tests
		self.modelTxt.Enable(enable)
		self.modelNum.Enable(enable)
		self.serNumTxt.Enable(enable)
		self.serNum.Enable(enable)
		self.waveLenTxt.Enable(enable)
		self.wavLen.Enable(enable)
		self.initCurTxt.Enable(enable)
		self.initCur.Enable(enable)
		self.maxCurTxt.Enable(enable)
		self.maxCur.Enable(enable)
		self.stepSizeTxt.Enable(enable)
		self.stepSize.Enable(enable)

		complete = enable
		for c in self.stepControls:
			
			if complete:
				c.name.Enable(True)
				c.startBtn.Enable(True)
			
				# check if test-data exists and is more current than the previous test
				if self.diode is not None and self.steps[c.idx][0] in self.diode.tests and (c.idx == 0 or (self.steps[c.idx-1][0] in self.diode.tests and self.diode.tests[ self.steps[c.idx][0] ].time > self.diode.tests[ self.steps[c.idx-1][0] ].time)):
						complete = True
						c.check.SetValue(True)
				else:
					complete = False
					c.check.SetValue(False)
			else:
				c.name.Enable(False)
				c.startBtn.Enable(False)
				c.check.SetValue(False)

		# show info 
		if self.diode is not None:
			self.modelNum.SetLabel( str(self.diode.info.model))
			self.serNum.SetLabel( str(self.diode.info.serNum ))
			self.wavLen.SetLabel( str(self.diode.info.wavLen ))
			self.initCur.SetLabel( str(self.diode.info.initCur ))
			self.maxCur.SetLabel( str(self.diode.info.maxCur ))
			self.stepSize.SetLabel( str(self.diode.info.step ))
	
		#save diode
		if self.diode is not None:
			self.diode.save()

	def startTest( self, testIdx, test):
		if self.onStep(testIdx):
			test.runTest(self, self.diode)
	def onStep( self, stepIdx):
		print str(stepIdx) + " : "
		if self.diode is not None and self.steps[stepIdx][0] in self.diode.tests :
			#print "pass1"
			if len(self.steps) > stepIdx:
			#	print "pass2"
				if self.steps[stepIdx+1][0] in self.diode.tests:
			#		print "pass3"
					if self.diode.tests[ self.steps[stepIdx+1][0] ].time > self.diode.tests[ self.steps[stepIdx][0]].time:
						return logger.ask("Going back a step! this will invalidate other tests.\n Continue?")
		return True

	
	def onP1(self, event):
		''' button handler for initial test '''
		print "P1"
		if self.onStep(0):
			self.initTest()
	

	def onP2(self, event):
		print "P2"
		if self.onStep(1):
			self.diode.tests[ self.steps[1][0] ] = PowerCurve.CurveData(None, time.time(), None, None)
		self.refresh()
		return
		
	def onP3(self, event):
		print "P3"
		self.diode.tests[ self.steps[2][0] ] = PowerCurve.CurveData(None, time.time(), None, None)
		self.refresh()
		return
		
	def onP4(self, event):
		print "P4"
		self.diode.tests[ self.steps[3][0] ] = PowerCurve.CurveData(None, time.time(), None, None)
		self.refresh()
		return
		for n in range(len(self.steps)):
			if n>3 and n in self.diode.tests:
				self.diode.tests[n] = False

		self.diode.tests[3] = True
		self.refresh()
	def onP5(self, event):
		print "P5"
		for n in range(len(self.steps)):
			if n>4 and n in self.diode.tests:
				self.diode.tests[n] = False

		self.diode.tests[4] = True
		self.refresh()
	def onP6(self, event):
		print "P6"
		for n in range(len(self.steps)):
			if n>5 and n in self.diode.tests:
				self.diode.tests[n] = False

		self.diode.tests[5] = True
		self.refresh()


	def initTest(self):
		''' performs the initial diode test '''
				
		class initTestGUI( PowerCurve.PowerCurveGUI ):
			def __init__( self, parent, diode,  graphWnd=None ):
				PowerCurve.PowerCurveGUI.__init__( self, parent,  diode )
				self.parent = parent
				self.graphWnd=graphWnd
				self.data["Raw Diode"] = dict()
				
				self.slopeval = 0
				self.xintercept = 0
				self.intercept = 0
				self.r_value = 0
				self.p_value = 0

				self.dataInfo = PowerCurve.DataInfo("Initial Diode Test", "Data taken from raw diode ")

				slopeSizer = wx.BoxSizer( wx.VERTICAL )
				self.slopeTxt = wx.StaticText( self, wx.ID_ANY, u"Slope", wx.DefaultPosition, wx.DefaultSize, 0 )
				self.slopeTxt.Wrap( -1 )
				self.slopeTxt.SetFont( wx.Font( 12, 74, 90, 90, False, "Tahoma" ) )
				slopeSizer.Add( self.slopeTxt, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
			
				self.slope = wx.StaticText( self, wx.ID_ANY, u"----", wx.DefaultPosition, wx.DefaultSize, 0 )
				self.slope.Wrap( -1 )
				self.slope.SetFont( wx.Font( 16, 74, 90, 92, False, "Tahoma" ) )
				slopeSizer.Add( self.slope, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
				
				self.infoSizer.Add( slopeSizer, 1, wx.TOP, 20 )
				self.line = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
				self.infoSizer.Add( self.line, 0, wx.EXPAND |wx.ALL, 5 )
				# -----
				threshSizer = wx.BoxSizer( wx.VERTICAL )
				
				self.threshTxt = wx.StaticText( self, wx.ID_ANY, u"Threshold", wx.DefaultPosition, wx.DefaultSize, 0 )
				self.threshTxt.Wrap( -1 )
				self.threshTxt.SetFont( wx.Font( 12, 74, 90, 90, False, "Tahoma" ) )
				threshSizer.Add( self.threshTxt, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
				
				
				self.thresh = wx.StaticText( self, wx.ID_ANY, u"----", wx.DefaultPosition, wx.DefaultSize, 0 )
				self.thresh.Wrap( -1 )
				self.thresh.SetFont( wx.Font( 16, 74, 90, 92, False, "Tahoma" ) )
				threshSizer.Add( self.thresh, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
				
				self.infoSizer.Add( threshSizer, 1, wx.TOP, 20 )
				#------------------------
			def update(self):
				if self.graphWnd is not None:
					self.graphWnd.addPoint(self.diode.pwr, self.lastVal, 0)

				x = self.data["Raw Diode"].keys()
				y = self.data["Raw Diode"].values()
				print x
				print y
				try:
					self.slopeval, self.intercept, self.r_value, self.p_value, std_err = stats.linregress(x,y)
				#	self.xintercept = -self.intercept/self.slopeval
				except Exception as e:
					print "update(diodetesting)" + str(e   )
				slopestr = "{0:.3f}".format( self.slopeval )
				threshstr ="{0:.3f}".format(self.intercept)

				self.slope.SetLabel(slopestr)
				self.thresh.SetLabel(threshstr)
			def saveVal(self):
				PowerCurve.PowerCurveGUI.saveVal(self)
				print "!!!" + str(self.diode.pwr)
				self.data["Raw Diode"][self.lastPwr] = self.lastVal # "Raw Diode" entry initialized in __init__
			def saveData(self):
				PowerCurve.PowerCurveGUI.saveData(self)
				self.diode.initTest = self.curveData 
				self.diode.tests[ self.parent.steps[0][0] ] = self.curveData
				self.parent.refresh()
			def onClose(  self, event ):
				PowerCurve.PowerCurveGUI.onClose(self, event)

			




		graphWnd = graph.GraphFrame( self,xRange=(self.diode.info.initCur, self.diode.info.maxCur), title="Initial Diode Test", xlabel="Current (amp)",ylabel="Output", showPoints=True)
		wnd = initTestGUI(self,  self.diode, graphWnd )
		graphWnd.Show()
		wnd.Show()
		return True
		
	def couplingProcedure():
		''' P2'''
		pass
	def couplingTest():
		'''P2'''
		pass
	def moduleTest():
		'''P3'''
		pass
	def burnIn():
		'''P4'''
		pass
	def moduleTest():
		'''P3'''
		pass


		
				
				
			
