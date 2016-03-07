from cffi import FFI
ffi = FFI()
lib = ffi.dlopen('./_libr2d2.so')
C = ffi.cdef("""
struct ib_connection {
    int                 lid;
    int                 qpn;
    int                 psn;
    unsigned            rkey;
    unsigned long long  vaddr;
};
enum ibv_wc_status {
    IBV_WC_SUCCESS,
    IBV_WC_LOC_LEN_ERR,
    IBV_WC_LOC_QP_OP_ERR,
    IBV_WC_LOC_EEC_OP_ERR,
    IBV_WC_LOC_PROT_ERR,
    IBV_WC_WR_FLUSH_ERR,
    IBV_WC_MW_BIND_ERR,
    IBV_WC_BAD_RESP_ERR,
    IBV_WC_LOC_ACCESS_ERR,
    IBV_WC_REM_INV_REQ_ERR,
    IBV_WC_REM_ACCESS_ERR,
    IBV_WC_REM_OP_ERR,
    IBV_WC_RETRY_EXC_ERR,
    IBV_WC_RNR_RETRY_EXC_ERR,
    IBV_WC_LOC_RDD_VIOL_ERR,
    IBV_WC_REM_INV_RD_REQ_ERR,
    IBV_WC_REM_ABORT_ERR,
    IBV_WC_INV_EECN_ERR,
    IBV_WC_INV_EEC_STATE_ERR,
    IBV_WC_FATAL_ERR,
    IBV_WC_RESP_TIMEOUT_ERR,
    IBV_WC_GENERAL_ERR
};

enum ibv_wc_opcode {
    IBV_WC_SEND,
    IBV_WC_RDMA_WRITE,
    IBV_WC_RDMA_READ,
    IBV_WC_COMP_SWAP,
    IBV_WC_FETCH_ADD,
    IBV_WC_BIND_MW,
/*
 * Set value of IBV_WC_RECV so consumers can test if a completion is a
 * receive by testing (opcode & IBV_WC_RECV).
 */
    IBV_WC_RECV         = 128,
    IBV_WC_RECV_RDMA_WITH_IMM
};
struct ibv_wc {
        uint64_t                wr_id;          /* ID of the completed Work Request (WR) */
        enum ibv_wc_status      status;         /* Status of the operation */
        enum ibv_wc_opcode      opcode;         /* Operation type specified in the completed WR */
        uint32_t                vendor_err;     /* Vendor error syndrome */
        uint32_t                byte_len;       /* Number of bytes transferred */
        uint32_t                imm_data;       /* Immediate data (in network byte order) */
        uint32_t                qp_num;         /* Local QP number of completed WR */
        uint32_t                src_qp;         /* Source QP number (remote QP number) of completed WR (valid only for UD QPs) */
        int                     wc_flags;       /* Flags of the completed WR */
        uint16_t                pkey_index;     /* P_Key index (valid only for GSI QPs) */
        uint16_t                slid;           /* Source LID */
        uint8_t                 sl;             /* Service Level */
        uint8_t                 dlid_path_bits; /* DLID path bits (not applicable for multicast messages) */
};
struct ibv_notification {
    /* extented struct of ibv_wc */
    struct ibv_wc   wc;
    int err_code;
};
int init_ctx(unsigned int num_msg_block);
int print_ctx();
struct ib_connection get_ib_local_connection();
int set_ib_remote_connection(struct ib_connection ib_conn);
int set_wr_id(int wr_id);
int rdma_send(char *msg, unsigned int size, unsigned idx);
char *rdma_recv(unsigned int size, unsigned idx);
int post_recv();
struct ibv_notification get_notify(unsigned int num_ack);
int print_local_conn();
int print_remote_conn();
""")
KEY_LENGTH				= 44
RDMA_WRID_SEND				= 10
RDMA_WRID_RECV			= 11
RDMA_WRID_RECV_DONE		= 12

def init_ctx(NUM_MSG_BLOCK):
    return lib.init_ctx(NUM_MSG_BLOCK)

def get_ib_local_connection():
	return lib.get_ib_local_connection()

def set_ib_remote_connection(remote_conn):
	remote_conn = remote_conn.split(':')
	ib_conn = ffi.new("struct ib_connection[1]") 
	ib_conn[0].lid = int(remote_conn[0],16)
	ib_conn[0].qpn = int(remote_conn[1],16)
	ib_conn[0].psn = int(remote_conn[2],16)
	ib_conn[0].rkey = int(remote_conn[3],16)
	ib_conn[0].vaddr = int(remote_conn[4],16)

	return lib.set_ib_remote_connection(ib_conn[0])

def send_ib_info(sock):
	ib_conn = get_ib_local_connection()
	lo_conn = "%04x:%06x:%06x:%08x:%016Lx" % (ib_conn.lid, ib_conn.qpn, ib_conn.psn, ib_conn.rkey, ib_conn.vaddr)
	sock.send(lo_conn)	
	return lo_conn

def set_wr_id(wr_id):
	return lib.set_wr_id(wr_id)

def post_recv():
	return lib.post_recv()

def get_notify(num_ack):
	return lib.get_notify(num_ack)

def rdma_send(msg, size, idx):
	return lib.rdma_send(msg, size, idx)

def rdma_recv(length, idx):
	return ffi.buffer(lib.rdma_recv(length, idx), length)

def recv_ib_info(sock):
	remote_conn = sock.recv(KEY_LENGTH)	
	return remote_conn

def wr_id_str(wr_id):
	if wr_id == RDMA_WRID_SEND:
		return "RDMA_WRID_SEND"
	elif wr_id == RDMA_WRID_RECV:
		return "RDMA_WRID_RECV"
	elif wr_id == RDMA_WRID_RECV_DONE:
		return "RDMA_WRID_RECV_DONE"
	else:
		return "ERROR"

def print_ctx():
	lib.print_ctx()
def print_local_conn():
	print "=========== Local =============================="
	lib.print_local_conn()
def print_remote_conn():
	print "=========== Remote ============================="
	lib.print_remote_conn()
