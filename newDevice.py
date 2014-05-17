
import wx
import os
import pickle
#import logger


#import wx
#import wx.lib.plot
import time
import logger
import Laser
#import graph

title = "New Device"
description = "Wizard to create a new device"

modelsFilename = "models.pkl"
models = [ "1509", "1511", "Other"]
modelsInfo = [ (5, 25, 3, 1,  "1509"), (8, 30, 3, 1,  "1509") ]
diodeFolder = "Diodes"



def run_tool(window_parent, device):
	diode = newDevice(device=device)

def loadModels():
	''' loads model# descriptions from file '''
	global models
	global modelsInfo
	outFile = open(modelsFilename, "r")
	dat = pickle.load(outFile)
	models = dat[0]
	modelsInfo = dat[1]
	outFile.close()
	
def newDevice(propCom, parent=None):
	''' returns a new diode object created by the user OR NONE if user cancels '''
	loadModels()
	dlg = NewDiodeInfoBox(parent)
	ret = dlg.ShowModal()



	cwd = os.getcwd()
	if ret == wx.ID_OK:
		#test for file existence
		try:
			fName = os.path.join(cwd, diodeFolder)
			fName = os.path.join(fName, (str(dlg.diodeInfo.model) + "-" + str(dlg.diodeInfo.serNum) + ".pkl") )
			print fName
			if os.path.isfile(fName):
				if logger.ask("Diode already exists. Do you want to replace the existing diode?") == False:
					while os.path.isfile(fName):
						fName = fName[0:-3] + "-2.pkl"
			dlg.Destroy()
			diode = Laser.LaserDiode(dlg.diodeInfo, fName=fName)
			if propCom is not None:	
				diode.MPD = propCom.channels[0]
				diode.LSR_PWR = propCom.channels[1]
				diode.TEMP = propCom.channels[2]
				diode.CUR_READ = propCom.channels[3]
				diode.laserOutChan = propCom.channels[4]
				diode.digitals = propCom.digitals
			return diode
		except Exception as e:
			logger.log("Error creating device", e, logger.ERROR)
			logger.message("Error creating new diode")
	else:
		dlg.Destroy()
		return None
	os.chdir(cwd)
	
	
def loadDevice(propCom, parent=None ):
	''' returns a diode object loaded from a file, OR NONE if user cancels '''
	filetypes = "PKL files (*.pkl)|*.pkl|All files|*"
	cwd = os.getcwd()
	defdir = os.path.join(cwd, diodeFolder)
	dlg = wx.FileDialog(parent, "Choose a file",defaultDir=defdir, style=wx.FD_OPEN , wildcard=filetypes)
	outFile = None
	if dlg.ShowModal()==wx.ID_OK:
		try:
			filename=dlg.GetFilename()
			dirname=dlg.GetDirectory()
			fullPath = os.path.join(dirname, filename)	
			outFile = open(fullPath, "r")
			diode = pickle.load(outFile)
			outFile.close()
			dlg.Destroy()
			if propCom is not None:
				diode.MPD = propCom.channels[0]
				diode.LSR_PWR = propCom.channels[1]
				diode.TEMP = propCom.channels[2]
				diode.CUR_READ = propCom.channels[3]
				diode.laserOutChan = propCom.channels[4]
				diode.digitals = propCom.digitals
			return diode
		except IOError as e:
			logger.log("Error opening file", e, logger.WARNING)
			logger.message("Error opening file.", logger.ERROR)
		except ValueError as e:
			logger.log("Error writing file", e, logger.WARNING)
			logger.message("Error writing file.", logger.ERROR)
		except Exception as e:
			logger.log("Error loading device", e, logger.ERROR)
			logger.message("Error loading device")
	else:
		dlg.Destroy()
		return None
	os.chdir(cwd)





# class to enter info for a new diode
class NewDiodeInfoBox ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Diode Wizard", pos = wx.DefaultPosition, size = wx.Size( 267,329 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		modelSelectionChoices = models
		self.modelSelection = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, modelSelectionChoices, wx.LB_SINGLE )
		mainSizer.Add( self.modelSelection, 1, wx.ALL|wx.EXPAND, 5 )
		
		serNumSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.serNumTxt = wx.StaticText( self, wx.ID_ANY, u"Serial Number:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.serNumTxt.Wrap( -1 )
		serNumSizer.Add( self.serNumTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.LEFT, 5 )
		
		self.serNumBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		serNumSizer.Add( self.serNumBox, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		mainSizer.Add( serNumSizer, 0, wx.EXPAND, 5 )
		
		wavLenSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.wavLenTxt = wx.StaticText( self, wx.ID_ANY, u"Wave Length:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.wavLenTxt.Wrap( -1 )
		wavLenSizer.Add( self.wavLenTxt, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.LEFT, 5 )
		
		self.wavLenBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		wavLenSizer.Add( self.wavLenBox, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mainSizer.Add( wavLenSizer, 0, wx.EXPAND, 5 )
		
		btnSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		btnSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.cancelBtn = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnSizer.Add( self.cancelBtn, 0, wx.ALL, 5 )
		
		self.okBtn = wx.Button( self, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.okBtn.SetDefault() 
		btnSizer.Add( self.okBtn, 0, wx.ALL, 5 )
		
		mainSizer.Add( btnSizer, 0, wx.EXPAND, 5 )


		self.okBtn.Bind( wx.EVT_BUTTON, self.onOk )
		self.cancelBtn.Bind( wx.EVT_BUTTON, self.onCancel )
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
	def onOk(self, event):
		info = self.getModelInfo()
		if info is not None:
			self.diodeInfo = Laser.LaserDiodeInfo( self.serNumBox.GetValue(), self.wavLenBox.GetValue(), *info)
			self.EndModal(wx.ID_OK)
		else:
			self.onCancel(None)
	def onCancel(self, event):
		self.EndModal(wx.ID_CANCEL)
	def getModelInfo(self):
		''' returns the model info for the current selection '''
		sel = self.modelSelection.GetSelection()
		if sel == len(models)-1:
			dlg = NewModelBox(self)
			if dlg.ShowModal() == wx.ID_OK:
				return dlg.info
			else:
				self.onCancel(None)
		else:
			return modelsInfo[sel]



# class to create a new diode model
class NewModelBox ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"New Model Wizard", pos = wx.DefaultPosition, size = wx.Size( 274,215 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		modelNameSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.modelNameTxt = wx.StaticText( self, wx.ID_ANY, u"Model Name:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.modelNameTxt.Wrap( -1 )
		modelNameSizer.Add( self.modelNameTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.modelNameBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		modelNameSizer.Add( self.modelNameBox, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mainSizer.Add( modelNameSizer, 0, wx.EXPAND, 5 )
		
		initCurSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.initCurTxt = wx.StaticText( self, wx.ID_ANY, u"Initial Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.initCurTxt.Wrap( -1 )
		initCurSizer.Add( self.initCurTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.initCurBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		initCurSizer.Add( self.initCurBox, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mainSizer.Add( initCurSizer, 0, wx.EXPAND, 5 )
		
		maxCurSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.maxCurTxt = wx.StaticText( self, wx.ID_ANY, u"Max Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.maxCurTxt.Wrap( -1 )
		maxCurSizer.Add( self.maxCurTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.maxCurBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		maxCurSizer.Add( self.maxCurBox, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mainSizer.Add( maxCurSizer, 0, wx.EXPAND, 5 )

		
		minCurSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.minCurTxt = wx.StaticText( self, wx.ID_ANY, u"Minimum Current:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.minCurTxt.Wrap( -1 )
		minCurSizer.Add( self.minCurTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.minCurBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		minCurSizer.Add( self.minCurBox, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mainSizer.Add( minCurSizer, 0, wx.EXPAND, 5 )
		
		stepSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.stepTxt = wx.StaticText( self, wx.ID_ANY, u"Power Step:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stepTxt.Wrap( -1 )
		stepSizer.Add( self.stepTxt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.stepBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		stepSizer.Add( self.stepBox, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mainSizer.Add( stepSizer, 0, wx.EXPAND, 5 )

		
		
		mainSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		btnSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.saveModelCheck = wx.CheckBox( self, wx.ID_ANY, u"save model", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnSizer.Add( self.saveModelCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		btnSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.cancelBtn = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnSizer.Add( self.cancelBtn, 0, wx.ALL, 5 )
		
		self.okBtn = wx.Button( self, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.okBtn.SetDefault() 
		btnSizer.Add( self.okBtn, 0, wx.ALL, 5 )
		
		mainSizer.Add( btnSizer, 0, wx.EXPAND, 5 )

		self.okBtn.Bind( wx.EVT_BUTTON, self.onOk )
		self.cancelBtn.Bind( wx.EVT_BUTTON, self.onCancel )
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )

	def onOk(self, event):
		try:
			self.info = (float(self.initCurBox.GetValue()), float(self.maxCurBox.GetValue()), str(self.minCurBox.GetValue()), float(self.stepBox.GetValue()), str(self.modelNameBox.GetValue()))
		except ValueError as e:
			wx.MessageBox("Entered values must be a number", "Error", wx.OK | wx.ICON_ERROR)
			return 
		models.pop()
		models.append(str(self.modelNameBox.GetValue()))
		models.append("other")
		modelsInfo.append( self.info )
		if self.saveModelCheck.GetValue():
			outFile = open(modelsFilename, "w")
			pickle.dump( (models, modelsInfo), outFile )
			outFile.close()


		self.EndModal(wx.ID_OK)
	def onCancel(self, event):
		self.EndModal(wx.ID_CANCEL)
	


