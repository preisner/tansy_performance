import sys, time, os, getopt
import socket
from tPacket import *
import libr2d2 as r2d2

PORT = 12345
ITERS = 100000
MODE = "MSG"
NUM_MSG_BLOCK = 100
TANSY_HEADER_LEN = 32

PROTOCOL = {'TCP': SOL_TCP, 'UDP': SOL_UDP, 'ICMP': SOL_ICMP}
def wait_sender(_sock):
	_sock.bind(("", PORT)) 
	_sock.listen(1) 
	return _sock.accept()

def DecodeTansyHeader(header):
	_version = header[0:2]
	_etc = header[2:4]
	_payload_length = int(header[4:10])
	_proto = int(header[10:12])

	return {'ver': _version, 'etc': _etc, 'payload_length': _payload_length, '_proto': _proto}


def main():
	_sck_l = []
	for _protocol in PROTOCOL.keys():
		_sck_l.append(socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW))
		_sck_l[len(_sck_l) - 1].setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)	

	print "Receiver starts."
	if(r2d2.init_ctx(NUM_MSG_BLOCK) < 0):
		print("init_ctx() failed.")
		sys.exit(1)

	_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	c_sock, address = wait_sender(_sock)
	remote_conn = r2d2.recv_ib_info(c_sock)
	lo_conn = r2d2.send_ib_info(c_sock)
	r2d2.set_ib_remote_connection(remote_conn)
	r2d2.print_local_conn()
	r2d2.print_remote_conn()
	_sock.close()
	c_sock.close()

	total_bytes = 0
	start_time = time.time()
	num_ack = 0
	limit_ack = 10

	idx = 0
	r2d2.set_wr_id(r2d2.RDMA_WRID_RECV)
	
	while True:
		r2d2.post_recv()
		ex_wc = r2d2.get_notify(1)
		if (ex_wc.err_code != 0):
			print "Error on get_notify() : %i "% (ex_wc.err_code)
			sys.exit(1)
		else:
			wc  = ex_wc.wc

		#print "Got %s.\n" % (r2d2.wr_id_str(wc.wr_id))
		if(wc.wr_id == r2d2.RDMA_WRID_RECV):
			_payload = r2d2.rdma_recv(wc.byte_len, idx)
			if (idx >= NUM_MSG_BLOCK-1):
				idx = 0
			else:
				idx += 1
			_header = DecodeTansyHeader(_payload[:TANSY_HEADER_LEN])
			#print _header['payload_length']
			_payload = _payload[TANSY_HEADER_LEN:TANSY_HEADER_LEN+_header['payload_length']]
			#print len(_payload)
			_packet = DecodePacket(_payload)
			if _header['_proto'] == SOL_TCP:
				_sck_l[0].sendto(_payload, (_packet['D_ADDR'], 0))
 			elif _header['_proto'] == SOL_UDP:
				_sck_l[1].sendto(_payload, (_packet['D_ADDR'], 0))
			elif _header['_proto'] == SOL_ICMP:
				_sck_l[2].sendto(_payload, (_packet['D_ADDR'], 0))
			else:
				print "Unsupported protocol." 

			#print "_payload : %i\n" % (len(_payload))
			total_bytes += len(_payload)
		else:
			print "Error %i " % (wc.wr_id)


if __name__ == "__main__":
	main()
