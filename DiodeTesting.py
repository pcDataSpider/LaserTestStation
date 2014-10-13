
import time
import wx
#import os
#import pickle
import model
import newDevice
import PowerCurve

import logger
import graph
#from scipy import stats
import numpy as np


title = "Diode Testing"
description = "open the diode testing interface"




def run_tool(window_parent, device):
	wnd = DiodeTestingGUI(window_parent, device)
	wnd.Show()




# class to hold the widgets for each procedure
class TestControls():
	def __init__(self, name, txt, startBtn, check, idx, test):
		self.name = name
		self.txt = txt
		self.startBtn = startBtn
		self.check = check
		self.idx = idx
		self.test = test

# GUI 'home screen' for all diode test procedures
class DiodeTestingGUI ( wx.Frame ):
	

	def __init__( self, parent, device ):
		parent = None
		self.diode = None
		self.model = None
		self.parent = parent
		self.device = device



		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Diode Testing", pos = wx.DefaultPosition, size = wx.Size( 466,329 ) )
		##self.tests = [ tests.InitialTest(), tests.CoupleProcedure() ]

		self.testControls = []

		
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
		
		self.minCurTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Minimum Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.minCurTxt.Wrap( -1 )
		self.minCurTxt.Enable( False )
		
		infoNameSizer.Add( self.minCurTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
		
		self.maxCurTxt = wx.StaticText( self.panel, wx.ID_ANY, u"Max Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.maxCurTxt.Wrap( -1 )
		self.maxCurTxt.Enable( False )
		
		infoNameSizer.Add( self.maxCurTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.ALIGN_RIGHT, 0 )
			
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
		
		self.minCur = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.minCur.Wrap( -1 )
		infoDataSizer.Add( self.minCur, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )
		
		self.maxCur = wx.StaticText( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.maxCur.Wrap( -1 )
		infoDataSizer.Add( self.maxCur, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )

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
		
		self.rightSizer = wx.BoxSizer( wx.VERTICAL )
		
		panelSizer.Add( self.rightSizer, 1, wx.EXPAND, 5 )
		
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
		self.changeDiodes( newDevice.newDevice(self.device))
	
	def onLoad( self, event ):
		self.changeDiodes(newDevice.loadDevice(self.device))

	def changeDiodes( self, diode):
		if diode is None:
			return
		self.diode = diode
		self.loadTests( self.diode.modelNum)
		self.refresh()


	def loadTests( self, modelNum ):
		try:
			self.model = model.models[ modelNum ]
		except KeyError as e:
			logger.message( "Unsupported model type: " + str(modelNum) )
			return

		self.rightSizer.DeleteWindows()
		self.testControls = []
		idx = 0
		for test in self.model.tests:
			print test
			testSizer = wx.BoxSizer( wx.HORIZONTAL )

			testTxt = wx.StaticText( self.panel, wx.ID_ANY, test.name, wx.DefaultPosition, wx.DefaultSize, 0)
			testTxt.Wrap( -1)
			testTxt.Enable(False)


			testBtn = wx.Button( self.panel, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
			testBtn.Enable( False )
		
			testChk = wx.CheckBox( self.panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
			testChk.Enable( False )

			testSizer.Add( testTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
			testSizer.AddStretchSpacer(1)
			testSizer.Add( testBtn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
			testSizer.Add( testChk, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)

			def funcBuilder(test, idx):
				def func(event):
					print "Running Test " + str(idx) + " : " + str( test.name )
					return self.runTest( test )
				return func
			testBtn.Bind( wx.EVT_BUTTON, funcBuilder(test, idx))
			self.rightSizer.Add( testSizer, 0, wx.EXPAND, 5)

			self.testControls.append( TestControls( test.name, testTxt, testBtn, testChk, idx, test ))
			idx = idx + 1

		self.rightSizer.Layout()
		self.panel.Layout()
		self.Layout()
		self.GetSizer().Fit(self)



	def runTest(self, test):
		testResult = test.runTest( self, self.diode )
		print testResult
		print testResult.data
		if not testResult.passed:
			return
		self.diode.tests[test.name] = testResult
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

		self.minCurTxt.Enable(enable)
		self.minCur.Enable(enable)
		self.maxCurTxt.Enable(enable)
		self.maxCur.Enable(enable)



		complete = enable
		prevTest = None
		if self.model and self.diode:
			for t in self.testControls:
				if complete:
					t.txt.Enable(True)
					t.startBtn.Enable(True)
				
					# check if test-data exists and is more current than the previous test, or there is no previous test
					if t.name in self.diode.tests and (prevTest is None or (prevTest.name in self.diode.tests and self.diode.tests[t.name].time > self.diode.tests[prevTest.name].time)):
						print "complete!"
						complete = True
						t.check.SetValue(True)
					else:
						print "not yet complete"
						complete = False
						t.check.SetValue(False)
				else:
					print "prev test not complete"
					t.txt.Enable(False)
					t.startBtn.Enable(False)
					t.check.SetValue(False)
				prevTest = t

		# show info 
		if self.diode is not None:
			self.modelNum.SetLabel( str(self.diode.modelNum))
			self.serNum.SetLabel( str(self.diode.serialNumber ))
			self.wavLen.SetLabel( str(self.diode.waveLength ))
			if self.model is not None:
				self.minCur.SetLabel( str(self.model.minCur ) + "amps")
				self.maxCur.SetLabel( str(self.model.maxCur ) + "amps")
	
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

