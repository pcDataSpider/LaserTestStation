import wx
import os
import pickle
import newDevice
import logger
import threading
import time
#from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from collections import namedtuple
import graph




title = "Power Curve"
description = "take a power curve of the diode"


diodeFolder = "Diodes"


def run_tool(window_parent, device):
	diode = None
	if logger.ask("Load an existing diode?"):
		diode = newDevice.loadDevice(device)
	else:
		diode = newDevice.newDevice(device)
	if diode == None:
		logger.log("Warning", "could not test device", logger.WARNING)

	graphWnd = graph.GraphFrame( window_parent,xRange=(diode.info.initCur, diode.info.maxCur), title="Power Curve", xlabel="Current (amp)",ylabel="Output", showPoints=True)
	wnd = PowerCurveTool(window_parent,  diode, graphWnd=graphWnd)
	graphWnd.Show()
	wnd.Show()




#helper function -------
def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result






class CurveData():
	def __init__(self, date, time, vals, info):
		self.date = date
		self.time = time
		self.vals = vals
		self.info = info
	def __str__(self):
		result = "CurveData class STR method(NYI)" 
		return result
class DataInfo():
	def __init__(self, title, description):
		self.title = title
		self.description = description
	def __str__(self):
		result = "DataInfo class STR method(NYI)"
		return result


class PowerCurveGUI ( wx.Dialog ):
	
	def __init__( self, parent, diode ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 353,209 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.onBitmap = scale_bitmap(wx.Bitmap("red-led-on-md.png"), 30, 30)
		self.offBitmap = scale_bitmap(wx.Bitmap("red-led-off-md.png"), 30, 30)
		self.diode = diode
		self.initCur = self.diode.info.initCur
		self.maxCur = self.diode.info.maxCur
		self.step = self.diode.info.step
		self.warm = True
		self.relay = False

		self.isOn = False
		self.sampleSize = 10
		self.sampleRate = 10
		self.data = dict()
		self.val = 0
		self.nVals = 0
		
		
		self.dataInfo = DataInfo("Power Curve", "Data taken from diode at varying power levels")

		
		self.diode.LSR_PWR.register(self)
		#self.diode.CIR_READ.register(self)
		#self.diode.MPD.register(self)

		
	
		
		self.mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.infoSizer = wx.BoxSizer( wx.HORIZONTAL )
	
	# --------------------------
		
		self.mainSizer.Add( self.infoSizer, 1, wx.EXPAND, 5 )
		
		self.bottomSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		self.bottomSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.controlSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.saveSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		# bitmap
		self.laserToggle = wx.StaticBitmap( self, wx.ID_ANY, self.offBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.laserToggle.SetToolTipString( u"Laser status indicator. Click to toggle laser states." )
		
		
		self.controlSizer.Add( self.laserToggle, 0, wx.ALL, 5 )
		
		self.laserPwr = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 50, self.initCur )
		self.controlSizer.Add( self.laserPwr, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.startBtn = wx.Button( self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.startBtn.SetToolTipString( u"Activate the laser" )
		self.controlSizer.Add( self.startBtn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		#self.openBtn = wx.Button( self, wx.ID_ANY, "Open", wx.DefaultPosition, wx.DefaultSize, 0 )
		#self.openBtn.SetToolTipString( u"Open the results using Excel" )
		#self.saveSizer.Add( self.openBtn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
		
		self.saveBtn = wx.Button( self, wx.ID_ANY, "Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.saveBtn.SetToolTipString( u"save the results to a seperate file" )
		self.saveSizer.Add( self.saveBtn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
		
		
		self.bottomSizer.Add( self.controlSizer, 0, wx.EXPAND, 5 )

		line = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		self.bottomSizer.Add( line ,1, wx.EXPAND, 5)

		self.bottomSizer.Add( self.saveSizer, 0, wx.EXPAND, 5 )
		
		self.mainSizer.Add( self.bottomSizer, 1, wx.EXPAND, 5 )
		
		self.SetSizer( self.mainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.laserToggle.Bind( wx.EVT_LEFT_DOWN, self.onLaserToggle )
		self.laserPwr.Bind( wx.EVT_SPINCTRL, self.onCurChange )
		self.startBtn.Bind( wx.EVT_BUTTON, self.onStartBtn )
		self.saveBtn.Bind( wx.EVT_BUTTON, self.onSaveBtn )

		self.Bind( wx.EVT_CLOSE, self.onClose )
	

	def start(self):
		if self.diode.start(warm=self.warm, relay=self.relay) == False:
			return False
		self.diode.LSR_PWR.start()
		self.diode.setValue( self.initCur )

				
	def stop(self):
		self.diode.stop()
		self.diode.LSR_PWR.stop()
		self.saveData()

	def saveVal(self):
		''' save the last laser output value for later and move to the next level '''
		self.val = self.val / self.sampleSize
		self.lastVal = self.val
		self.lastPwr = self.diode.pwr
		self.val = 0
		self.nVals = 0
		self.update()
		newPwr = self.laserPwr.GetValue() + self.step
		if newPwr <= self.maxCur:
			self.diode.LSR_PWR.deregister(self)
			self.laserPwr.SetValue( newPwr )
			self.onCurChange(None)
			def timerFunc():
				self.diode.LSR_PWR.register(self)
			t = threading.Timer( .5, timerFunc )
			t.start()
		else:
			self.laserPwr.SetValue( self.initCur )
			self.stop()

	def saveData(self):
		''' save the entire power curve data to the Diode object '''
		date = time.asctime()
		self.curveData = CurveData(date, time.time(), self.data, self.dataInfo )


	def update(self):
		''' update the display '''
		pass
			
			
	# Channel event handlers
	def onPoint(self, chan, propCom, pVal, tStamp, rTime):
		self.val += pVal
		self.nVals += 1
		if self.nVals >= self.sampleSize:
			self.saveVal()
		
		
	def onStart(self, chan, propCom):
		self.isOn = True
		self.val = 0
		self.nVals = 0
		self.laserToggle.SetBitmap(self.onBitmap)
		self.startBtn.Enable(False)
	def onStop(self, chan, propCom):
		self.isOn = False
		self.laserToggle.SetBitmap(self.offBitmap)
		self.startBtn.Enable(True)
	def onSet(self, chan, propCom, newval):
		self.val = 0
		self.nVals = 0

	# Window event handlers
	def onLaserToggle( self, event ):
		if self.isOn:
			self.stop()
			self.laserToggle.SetBitmap(self.offBitmap)
		else:
			self.start()
			self.laserToggle.SetBitmap(self.onBitmap)

		
	
	def onCurChange( self, event ):
		self.diode.setValue( self.laserPwr.GetValue() )
		self.val = 0
		self.nVals = 0

	def onSaveBtn( self, event, path=None ):
		''' save the data to a file '''
		if self.curveData is None:
			logger.msg("No data yet!")
		filetypes = "CSV files (*.CSV)|*.csv|All files|*"
		cwd = os.getcwd()
		#defdir = os.path.join(cwd, diodeFolder)
		dlg = wx.FileDialog(self, "Choose a file", defaultDir=cwd, style=wx.FD_SAVE , wildcard=filetypes)
		outFile = None
		if dlg.ShowModal()==wx.ID_OK:
			self.saveData()
			print self.curveData
			try:

				filename=dlg.GetFilename()
				dirname=dlg.GetDirectory()
				fullPath = os.path.join(dirname, filename)	
				outFile = open(fullPath, "w")
				strFmt = str(self.curveData.info.title) + "\n" + str(self.curveData.info.description) + "\n,Power (adc reading)\ncurrent (amps)"
				for sets in self.curveData.vals:
					strFmt += "," + str(sets)
				outFile.write(strFmt+"\n")


				rangeVals = []
				for vals in self.curveData.vals.itervalues():
					for n in vals:
						if not n in rangeVals:
							rangeVals.append(n)
				rangeVals.sort()
				
				for n in rangeVals:
					strFmt = str(n) + ","
					for vals in self.curveData.vals.itervalues():
						if n in vals:
							strFmt += str(vals[n]) + ","
						else:
							strFmt += ","
					strFmt = strFmt[:-1] +  "\n"
					outFile.write(strFmt)
						


				outFile.close()
				dlg.Destroy()

			except IOError as e:
				logger.log("Error opening file", e, logger.WARNING)
			except ValueError as e:
				logger.log("Error writing file", e, logger.WARNING)
			except Exception as e:
				logger.log("Error writing file ?", e, logger.ERROR)
		else:
			dlg.Destroy()
	
	def onStartBtn( self, event ):
		self.diode.LSR_PWR.setValue( self.sampleRate )
		self.onCurChange(None)
		self.start()
		
	def onClose(  self, event ):
		self.stop()
		self.diode.LSR_PWR.deregister(self)
		self.Destroy()

	

	

class PowerCurveTool( PowerCurveGUI ):

	def __init__( self, parent,  diode ,graphWnd=None ):
		PowerCurveGUI.__init__( self, parent, diode )
		self.graphWnd=graphWnd

		appSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.appTxt = wx.StaticText( self, wx.ID_ANY, u"With Apperture", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.appTxt.Wrap( -1 )
		self.appTxt.SetFont( wx.Font( 12, 74, 90, 90, False, "Tahoma" ) )
		
		appSizer.Add( self.appTxt, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.CETxt1 = wx.StaticText( self, wx.ID_ANY, u"Coupling Efficiency", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.CETxt1.Wrap( -1 )
		appSizer.Add( self.CETxt1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.appCE = wx.StaticText( self, wx.ID_ANY, u"1.42", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.appCE.Wrap( -1 )
		self.appCE.SetFont( wx.Font( 16, 74, 90, 92, False, "Tahoma" ) )
		
		appSizer.Add( self.appCE, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.infoSizer.Add( appSizer, 1, wx.TOP, 20 )
		
		self.line = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		self.infoSizer.Add( self.line, 0, wx.EXPAND |wx.ALL, 5 )
		
		noAppSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.noAppTxt = wx.StaticText( self, wx.ID_ANY, u"Without Apperture", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.noAppTxt.Wrap( -1 )
		self.noAppTxt.SetFont( wx.Font( 12, 74, 90, 90, False, "Tahoma" ) )
		
		noAppSizer.Add( self.noAppTxt, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.CETxt2 = wx.StaticText( self, wx.ID_ANY, u"Coupling Efficiency", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.CETxt2.Wrap( -1 )
		noAppSizer.Add( self.CETxt2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.noAppCE = wx.StaticText( self, wx.ID_ANY, u"1.12", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.noAppCE.Wrap( -1 )
		self.noAppCE.SetFont( wx.Font( 16, 74, 90, 92, False, "Tahoma" ) )
		
		noAppSizer.Add( self.noAppCE, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.infoSizer.Add( noAppSizer, 1, wx.TOP, 20 )
		#------------------------
		self.appOnCheck = wx.CheckBox( self, wx.ID_ANY, u"Apperture", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.controlSizer.Add( self.appOnCheck, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
	def update(self):
		self.graphWnd.addPoint(self.diode.pwr, self.lastVal, self.wApp())

	def saveVal(self):
		PowerCurveGUI.saveVal(self)
		if not self.wApp() in self.data:
			self.data[self.wApp()]=dict()
		self.data[self.wApp()][self.diode.pwr] = self.lastVal
	def saveData(self):
		PowerCurveGUI.saveData(self)
		self.diode.powerCurves.append( self.curveData )
	def wApp(self):
		if self.appOnCheck.GetValue():
			return "With Aperature"
		else:
			return "Without Aperature"

	
	


