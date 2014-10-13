import tests


class DiodeModel():
	def __init__(self, maxRange):
		print("new model!")
		self.minCur = maxRange[0]
		self.maxCur = maxRange[1]
		self.tests = []
	
class Model1509_compatible(DiodeModel):
	def __init__(self, maxRange, range1, range2, step):
			# Does MinCur == Couple diode strength??

		DiodeModel.__init__(self, maxRange)
		print("new 1509-compatible diode")

		initTest = tests.RawPowerCurveTest("Initial diode test", "record raw diode readings", range1, step)
		coupleStep = tests.CoupleTest("Coupling procedure", "show constant readings to facilitate diode coupling procedure", maxRange[0] )
		postCouple = tests.PowerCurveTest("Test coupled diode", "test power readings after coupling", range2, step)
		postCouple_postEpoxy = tests.PowerCurveTest("Test assembled diode", "test power readings to assess epoxy bonds", range2, step)
		moduleTest = tests.PowerCurveTest("Test assembled module", "test power readings of the assembled module", range1, step )
		burnin = tests.BurnInTest( maxRange[1] )
		finalTest = tests.PowerCurveTest("Final test", "take a final power reading", range1, step)

		# each test is a function that performs the test, given the Laser object as input.
		self.tests.append(initTest)
		self.tests.append(coupleStep)
		self.tests.append(postCouple)
		self.tests.append(postCouple_postEpoxy)
		self.tests.append(moduleTest)
		self.tests.append(burnin)
		self.tests.append(finalTest)

class Model1509(Model1509_compatible):
	def __init__(self):
		Model1509_compatible.__init__(self, 1509, (3,30), (5, 10), (5,25), 1)

models = dict()
models["BLAH"] = Model1509_compatible((3,30), (5,10), (5,25), 1)
models["1509"] = Model1509_compatible((3,30), (5,10), (5,25), 1)

#class ModelKLS(Model1509_compatible):
#	def __init__(self):
#		model1509_compatible.__init__(self, ...)
#		self.tests[X] = NewTest()...


