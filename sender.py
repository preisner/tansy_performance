import sys, os, time
from tPacket import *
MODULE_PATH = "/usr/lib/python2.6/tansy"
sys.path.insert(0, MODULE_PATH)
from netfilterqueue import NetfilterQueue
TANSY_VERSION = 1
TANSY_HEADER_LEN = 32

PIPE_NAME = "/tmp/sender.pipe"
#PIPEOUT = os.open(PIPE_NAME, os.O_WRONLY)
PIPEOUT = open(PIPE_NAME, 'w')
def TansyHeader(proto, payload_length):
	# Header length : 32Byte
	# 4B : Version, etc..
	_version = str(TANSY_VERSION).zfill(2)
	_etc = "".zfill(2)
	# 6B: total length of payload(except Header)
	_payload_length = str(payload_length).zfill(6)
	# 2B transport layer protocol
	_proto = str(proto).zfill(2)
	# 20B : reserved
	_rest = "".zfill(20)
	return _version + _etc + _payload_length + _proto + _rest


def get_packet(pkt):
	global PIPE_OUT
	try:
		_payload = pkt.get_payload()
		_packet = DecodePacket(_payload)
		#print _packet
		_header = TansyHeader(_packet['PROTOCOL'], len(_payload))
		_payload = _header + _payload
		#_payload = (_header+_payload).zfill(2048)
		#PIPEOUT.write(_payload.zfill(2048))
		PIPEOUT.write(_payload.ljust(2048,'0'))
		PIPEOUT.flush()
		pkt.drop()
	except Exception, err:
		print "Error on getting payload in get_packet() : %s" % str(err)
		return

def main(id):

	"""
	_payload = "0"*1500
	while True:
		PIPEOUT.write(_payload.zfill(2048))
		PIPEOUT.flush()
		print "%i--------------" %(len(_payload.zfill(2048)))
		time.sleep(1)
	
	"""
	try:
		nfqueue = NetfilterQueue()
		nfqueue.bind(id + 1, get_packet, max_len=50000)
		while True:
			nfqueue.run()
	except Exception, err:
		print "Error on binding NF_QUEUE: %s" % str(err)
		sys.exit(1)


if __name__ == "__main__":
	main(0)
