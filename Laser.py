import wx # for more message boxes than in logger
import os
import pickle
import time
import logger

# class to contain all info and methods related to a laser diode
class LaserDiode():
	def __init__(self, serialNumber, waveLength, modelNum, maxRange, fName=None):

		self.serialNumber = serialNumber
		self.waveLength = waveLength
		self.modelNum = modelNum
		self.maxRange = maxRange

		self.fName = fName
		self.on = False
		self.lastOn = 0
		self.lastWarm = 0
		self.digitals = None
		self.laserInChan = None
		self.laserOutChan = None
		# pins
		self.FLOW =   0b1000
		self.RLY = 0b0100

		# states
		self.RLYON =  0b0001
		self.RDYON =  0b0001
		self.RDYOFF = 0b1000
		self.LSRON =  0b0101

		self.mask =   0b1111
		self.RLYmask =   0b1111


		# test results:
		#self.initTest = None
		#self.diodePreCouple = None
		#self.diodePostCouple = None
		#self.diodePostAssemble = None
		#self.burnIn = None
		#self.final = None
		
		self.tests = dict()
		self.powerCurves = [] # List of results from the power curve tool.
	def generateReport(self):
		pass

	def save(self):
		''' saves this object to a file '''
		try:
			self.stop()
			digitals = self.digitals
			MPD = self.MPD
			LSR_PWR = self.LSR_PWR
			TEMP = self.TEMP
			CUR_READ = self.CUR_READ
			laserOutChan = self.laserOutChan

			self.digitals = None
			self.MPD = None
			self.LSR_PWR = None
			self.TEMP = None
			self.CUR_READ = None
			self.laserOutChan = None
			
			if self.fName is not None:
				d = os.path.dirname(self.fName)
				print d
				try:
					os.makedirs(d)
				except OSError:
					if not os.path.isdir(d):
						raise
				outFile = open(self.fName, "w")
				pickle.dump( self, outFile )
				outFile.close()

			self.digitals = digitals
			self.MPD = MPD
			self.LSR_PWR = LSR_PWR
			self.TEMP = TEMP
			self.CUR_READ = CUR_READ
			self.laserOutChan = laserOutChan
		except Exception as e:
			logger.log("Failed to save diode", e, logger.ERROR)
			logger.message("Failed to save diode info! Any test data was not saved")

	def start(self, warm=True, relay=False):
		''' starts the laser at minCur '''

		if self.on :
			return True


		self.setValue( 0 )

		
		# TODO finish start procedure

		# turn LSR_RDY high
		if relay:
			self.digitals.setValue( self.RDYON, pinmask=self.RLYmask )
			#test relay...
			time.sleep(1)
		else:
			self.digitals.setValue( self.RDYON, pinmask=self.mask )

		# test water flow sensor
		while self.digitals.inVals & self.FLOW:
			val = wx.MessageBox("Water flow error: Ignore?", "Error", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
			if val==wx.YES:
				break
			elif val==wx.NO:
				pass
			else:
				return False

		# test relay sensor
		while self.digitals.inVals & self.RLY and self.relay:
			val = wx.MessageBox("Relay wont open: Ignore?", "Error", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
			if val==wx.YES:
				break
			elif val==wx.NO:
				pass
			else:
				return False

		# set current level on P2 to min cur
		#self.pwr = self.info.minCur
		#self.setValue( self.info.minCur )

		val = wx.MessageBox("!! Laser Activation !!", "!! WARNING !!", wx.OK | wx.CANCEL | wx.ICON_WARNING)
		if val != wx.OK:
			return False
		# wait 3 sec
		#time.sleep(3)

		# turn LSR_ON and LSR_RDY high ( p18 )
		if relay:
			self.digitals.setValue( self.LSRON, pinmask=self.RLYmask )
		else:
			self.digitals.setValue( self.LSRON, pinmask=self.mask )
		
		# start laser at diode's minCur
		self.setValue( self.maxRange[0] )
		self.laserOutChan.start()
		#self.laserOutChan.setValue( self.info.minCur )


		# wait 3 min to warm-up and display message 

		# TODO count down   and  cancel
		if warm and time.time() - self.lastWarm > 60*60* 3:
			if logger.ask("Warm up Laser?"):
				logger.message("-- Laser warming up --", logger.WARNING)
				time.sleep( 60 * 3 )
				self.lastWarm = time.time()
		self.on = True
		
		
		return True
	def stop(self):
		''' shuts off the laser '''
		if self.on and self.digitals is not None and self.laserOutChan is not None:
			# turn LSR_ON low and LSR_RDY low (p18)
			self.digitals.setValue( self.RDYOFF, pinmask=self.RLYmask )
			self.laserOutChan.stop()
			# save last on time
			self.lastOn = time.time()
			#self.laserOutChan = None
			#self.digitals = None
		self.on = False
	def setValue(self, newPwr):
		''' changes the output power of the laser '''
		if self.digitals is None or self.laserOutChan is None:
			logger.log("Laser", "improper load.", logger.ERROR)
			return False
			
		if newPwr > self.maxRange[1]:
			logger.log("Laser", "Power set too high")
			return False
			
		self.pwr = int( newPwr )
		self.curpwr = self.curPwr()
		if self.on:
			self.laserOutChan.setValue( self.curpwr )
		return True

	def curPwr(self):
		''' returns current power level in PWM output ( 0 - 1000 ) '''
		return self.pwr * 20


