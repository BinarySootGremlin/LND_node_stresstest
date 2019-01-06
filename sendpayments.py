import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc
import os
import time
import codecs
##dependencies (run following commands to get rpc_pb2 and grpc covered)
#sudo apt-get install python-pip
#pip install grpcio grpcio-tools googleapis-common-protos
#git clone https://github.com/googleapis/googleapis.git
#curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto
#python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
#pip install google
#pip install --upgrade google-api-python-client
##


## Due to updated ECDSA generated tls.cert we need to let gprc know that
## we need to use that cipher suite otherwise there will be a handhsake
## error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'

## Lnd cert is at ~/.lnd/tls.cert on Linux and
## ~/Library/Application Support/Lnd/tls.cert on Mac
cert = open(os.path.expanduser('/home/bitcoin/.lnd/tls.cert'), 'rb').read()
creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', creds)
stub = lnrpc.LightningStub(channel)

## Lnd admin macaroon is at ~/.lnd/data/chain/bitcoin/simnet/admin.macaroon on Linux and
## ~/Library/Application Support/Lnd/data/chain/bitcoin/simnet/admin.macaroon on Mac
with open(os.path.expanduser('/home/bitcoin/.lnd/data/chain/bitcoin/testnet/admin.macaroon'), 'rb') as f:
    macaroon_bytes = f.read()
    macaroon = codecs.encode(macaroon_bytes, 'hex')

metadata = [('macaroon',macaroon)]

def send_payment(pay_req):
	##SENDPAYMENT START
	
	## Extract details from the invoice
	## https://api.lightning.community/?python#decodepayreq
	pay_req=pay_req.rstrip()
	raw_invoice = ln.PayReqString(pay_req=str(pay_req))
	#get details from pay_req
	invoice_details = stub.DecodePayReq(raw_invoice, metadata=[('macaroon', macaroon)])

	## https://api.lightning.community/?python#sendrequest
	request = ln.SendRequest(
	  dest_string=invoice_details.destination,
	  amt=invoice_details.num_satoshis,
	  payment_hash_string=invoice_details.payment_hash,
	  final_cltv_delta=144#final_cltv_delta=144 is default for lnd
	);
	##send simple payment via req_key
	response = stub.SendPaymentSync(request, metadata=[('macaroon', macaroon)])

	print(response)

	##SENDPAYMENT END

##prepare file into string array
lines = [line.rstrip('\n') for line in open('invoices.txt')]
overalltime=0

starttime = time.time() * 1000#milliseconds
num_lines = len(lines)
##if the file doesn't contain invoices: skip!
##if lines are found that means, we want to send payments via these pay_reqs line by line
if(num_lines > 0):

	for line in lines:
		send_payment(line)
	endtime = (time.time() * 1000)-starttime
	averagetime = endtime / num_lines
else:
	print("invoices empty!")
##print overall and average time per transaction
print("time= " + str(endtime) + "ms - average= " + str(averagetime) + "ms")
