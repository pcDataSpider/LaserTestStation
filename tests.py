
import time
import wx
#import os
#import pickle
import newDevice
import PowerCurve
import tests

import Queue
import logger
import graph
from scipy import stats

			

#helper function -------
def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result	


class InitialTest():
	def  __init__(self):
		self.name = "Initial Diode Test"
		self.description  = "Test of the raw diode's output power"
		
	def runTest( self, parent, diode):
		graphWnd = graph.GraphFrame( parent,xRange=(diode.info.initCur, diode.info.maxCur), title=self.name, xlabel="Current (amp)",ylabel="Output", showPoints=True)
		wnd = initTestGUI(parent, diode, self, graphWnd )
		graphWnd.Show()
		wnd.Show()
				
class CoupleProcedure():
	def  __init__(self):
		self.name = "Couple Diode"
		self.description  = "Allow user to couple the diode"
		
	def runTest( self, parent, diode):
		billboard = CoupleBillboard(parent, diode, self )
		billboard.Show()

		#controls = LaserControls(parent, diode, self, 1, initCur=diode.info.minCur)
		#controls.Show()
	


#------------------- GUI classes ----------------

	
class LaserControl(wx.Dialog):

	def __init__(self, parent, diode, testInfo, sample_size=1,initCur=None, maxCur=None):
		self.parent = parent
		self.diode = diode
		self.testInfo = testInfo
		wx.Dialog.__init__ ( self, parent, title = "Laser Controls" ) 
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.onBitmap = scale_bitmap(wx.Bitmap("red-led-on-md.png"), 30, 30)
		self.offBitmap = scale_bitmap(wx.Bitmap("red-led-off-md.png"), 30, 30)

		if initCur == None:
			self.initCur = self.diode.info.initCur
		else:
			self.initCur = initCur
		if maxCur == None:
			self.maxCur = self.diode.info.maxCur
		else:
			self.maxCur = maxCur

		ico = wx.Icon('OFSI-Logo.ico', wx.BITMAP_TYPE_ICO )
		self.SetIcon( ico )
	
		
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

		self.bottomSizer.Add( self.controlSizer, 0, wx.EXPAND, 5 )
		
		self.mainSizer.Add( self.bottomSizer, 1, wx.EXPAND, 5 )
		
		self.SetSizer( self.mainSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.laserToggle.Bind( wx.EVT_LEFT_DOWN, self.onLaserToggle )
		self.laserPwr.Bind( wx.EVT_SPINCTRL, self.onCurChange )
		self.startBtn.Bind( wx.EVT_BUTTON, self.onStartBtn )

		self.Bind( wx.EVT_CLOSE, self.onClose )

	def start(self):
		if self.diode.start(warm=self.warm, relay=self.relay) == False:
			return False
		self.diode.LSR_PWR.start()
		self.diode.setValue( self.initCur )

				
	def stop(self):
		self.diode.stop()
		self.diode.LSR_PWR.stop()

	

	# Window event handlers
	def onLaserToggle( self, event ):
		if self.isOn:
			self.stop()
			self.laserToggle.SetBitmap(self.offBitmap)
		else:
			self.start()
			self.laserToggle.SetBitmap(self.onBitmap)

	
	def onStartBtn( self, event ):
		self.diode.LSR_PWR.setValue( self.sampleRate )
		self.start()

		
	def onClose(  self, event ):
		self.stop()
		self.Destroy()

class CoupleControls(LaserControl):

	def __init__(self, parent, diode, testInfo, sample_size=1,initCur=None, maxCur=None):
		initCur = diode.info.minCur
		maxCur = diode.info.initCur
		LaserControl.__init__(self, parent, diode, testInfo, sample_size, initCur, maxCur)


	
	
class CoupleBillboard(wx.Frame):

	def __init__(self, parent, diode, testInfo, sample_size=1):
		self.timer = None
		self.parent = parent
		self.diode = diode
		self.testInfo = testInfo
		wx.Frame.__init__(self, parent, wx.ID_ANY, "BillBoard - Diode Coupling")
		ico = wx.Icon('OFSI-Logo.ico', wx.BITMAP_TYPE_ICO )
		self.SetIcon( ico )
	
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		panelSizer = wx.BoxSizer( wx.HORIZONTAL )
		controlSizer = wx.BoxSizer( wx.VERTICAL )
		self.font = wx.Font(300, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		self.font2 = wx.Font(150, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		self.font3 = wx.Font(20, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

	
		panel = wx.Panel(self)
		initVal = "0000.0"
		if sample_size == 1:
			initVal = "0000"
		self.txtValue = wx.StaticText(self, label=initVal)
		self.txtCE = wx.StaticText(self, label="CE:000.0")
		self.txtApp = wx.StaticText(self, label="Apperature :")
		self.txtValue.SetFont(self.font)
		self.txtCE.SetFont(self.font2)
		self.txtApp.SetFont(self.font3)
		self.gaugeMeter = wx.Gauge( self, wx.ID_ANY, 4096, wx.DefaultPosition, wx.Size( 75,-1 ), wx.GA_VERTICAL|wx.GA_SMOOTH )
		self.appBox = wx.ToggleButton(self,wx.ID_ANY,size=wx.Size(50,50),label="Off")
		self.appBox.SetFont(self.font3)


		controlSizer.Add(self.txtValue,0,wx.ALL,20)
		controlSizer.Add((0,0),1)
		controlSizer.Add(self.txtCE,0,wx.ALL,10)

		bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
		bottomSizer.Add( self.txtApp,0,wx.ALL,20)
		bottomSizer.Add(self.appBox, 0, wx.ALL, 5)


		panelSizer.Add(controlSizer,0,wx.ALL,5)
		panelSizer.Add(self.gaugeMeter, 0, wx.ALL|wx.EXPAND, 5)
		panel.SetSizer(panelSizer)
		mainSizer.Add(panel, 1, wx.ALL|wx.EXPAND)
		mainSizer.Add(bottomSizer,0,wx.ALL,5)
		self.SetSizer(mainSizer)
		self.Fit()

		self.samples = Queue.Queue(sample_size)
		self.total = 0
		self.nSamples = 0
		self.lastValue_W_App = 0
		self.lastValue_WO_App = 0
		
		self.diode.LSR_PWR.register(self)	
		self.appBox.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle)
		self.Bind( wx.EVT_CLOSE, self.OnClose )


	def onPoint(self, chan, propCom, pVal, tStamp, rTime):
		self.add(pVal)
	def add(self, value):
		if self.samples.full():
			self.nSamples = self.sample_size
			self.total-=self.samples.get()
		else:
			self.nSamples += 1
		self.samples.put(value)
		self.total+=value


		if self.control.appBox.GetValue():
			self.lastValue_W_App = value
		else:
			self.lastValue_WO_App = Value

		self.label = "{0:06.1f}".format( float(self.total)/self.nSamples)
		if self.sample_size == 1:
			self.label = "{0:04}".format( self.total )
		CE = float(self.total)/self.nSamples
		self.labelCE = "Coupling Efficiency: {0:06.1f}".format(CE)

		self.gaugeMeter.SetValue(CE)
		if self.timer is None:
			self.timer = threading.Timer(0.2,self.update)
			self.timer.start()

	def update(self):
		self.txtValue.SetLabel(self.label)
		self.txtCE.SetLabal(self,labelCE)
		self.timer = None

	def OnToggle(self, event):
		if self.appBox.GetValue():
			self.appBox.SetLabel("On")
		else:
			self.appBox.SetLabel("Off")
	
	def OnClose(self, event):
		try:
			self.diode.LSR_PWR.deregister(self)
		except KeyError as e:
			logger.log("Can't deregister billboard hook", self)
		self.Destroy()

	
class initTestGUI( PowerCurve.PowerCurveGUI ):
	def __init__( self, parent, diode,  testInfo, graphWnd=None ):
		PowerCurve.PowerCurveGUI.__init__( self, parent,  diode )
		self.parent = parent
		self.graphWnd=graphWnd
		self.testInfo =  testInfo
		self.data["Raw Diode"] = dict()
		
		self.slopeval = 0
		self.xintercept = 0
		self.intercept = 0
		self.r_value = 0
		self.p_value = 0

		self.dataInfo = PowerCurve.DataInfo(testInfo.name, testInfo.description)

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
		self.diode.tests[ self.testInfo.name ] = self.curveData
		self.parent.refresh()
	def onClose(  self, event ):
		PowerCurve.PowerCurveGUI.onClose(self, event)

