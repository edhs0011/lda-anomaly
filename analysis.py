from model import FlowSuspiciousConnectsModel

class FlowConnectsAnalysis:

	def __init__(self, data, config):
		self.data = data
		self.config = config

	def detect(self):
		model = FlowSuspiciousConnectsModel(self.data, self.config)
		model.train_new_model()