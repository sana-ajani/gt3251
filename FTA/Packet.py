class Packet:
	def __init__(self, src_port, dest_port, seq_num, ack_num, flags, data, checksum = None):
		self.src_port = src_port & 0xffff
		self.dest_port = dest_port & 0xffff
		self.seq_num = seq_num
		self.ack_num = ack_num
		self.data = data
		self.ACK = flags[0]
		self.PSH = flags[1]
		self.RST = flags[2]
		self.SYN = flags[3]
		self.FIN = flags[4]
