import sys, os, time
import fcntl,socket
import select
MODULE_PATH = "/usr/lib/python2.6/tansy"
sys.path.insert(0, MODULE_PATH)
import libr2d2 as r2d2

PIPE_NAME = "/tmp/sender.pipe"
RECEIVER_IP = "192.168.10.11"
PORT = 12345 
ITERS = 100000 
MSG_LEN = 1500 
MODE = "MSG" 

def main():
	NUM_MSG_BLOCK = 100
	total_bytes = 0
	start_time = time.time()
	num_ack = 1	
	limit_ack = 10
	idx = 0

	if not os.path.exists(PIPE_NAME):
		os.mkfifo(PIPE_NAME)  

	if(r2d2.init_ctx(NUM_MSG_BLOCK) < 0):
		print("init_ctx() failed.")
		sys.exit(1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((RECEIVER_IP, PORT))
	lo_conn = r2d2.send_ib_info(sock)
	remote_conn = r2d2.recv_ib_info(sock)
	
	re = r2d2.set_ib_remote_connection(remote_conn)
	if (re < 0):
		print("Error on set_ib_remote_connection() : %i" % (re))
	r2d2.print_local_conn()
	r2d2.print_remote_conn()
	sock.close()

	r2d2.set_wr_id(r2d2.RDMA_WRID_SEND)

	PIPEIN = open(PIPE_NAME, 'r')
	#fcntl.fcntl(PIPEIN, fcntl.F_SETFL, fcntl.fcntl(PIPEIN, fcntl.F_GETFL) | os.O_NONBLOCK)
	while True:
		[rlist, olist, elist] = select.select([PIPEIN], [], [])
		if rlist:
			_payload = PIPEIN.read(2048)
		else:
			continue
		
		if len(_payload) == 0:
			continue
		r2d2.rdma_send(_payload, len(_payload), idx)
		#print "%i===========================" %(len(_payload))
		if (idx >= NUM_MSG_BLOCK-1):
			idx = 0
		else:
			idx += 1
		total_bytes += len(_payload)
		ex_wc = r2d2.get_notify(num_ack)
		if (ex_wc.err_code != 0):
			print "Error on get_notify() : %i "% (ex_wc.err_code)
			sys.exit(1)
		else:
			wc = ex_wc.wc
		#print "Got %s.\n" % (r2d2.wr_id_str(wc.wr_id))
		if(wc.wr_id == r2d2.RDMA_WRID_SEND):
			pass
		else:
			print "Error %i " % (wc.wr_id)			
			sys.exit(1)
if __name__ == "__main__":
	main()

