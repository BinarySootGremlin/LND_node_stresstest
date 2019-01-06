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

def add_invoice(memo,amt):
	##ADDINVOICE START

	invoice_req = ln.Invoice(memo = memo, value = amt)
	response = stub.AddInvoice(invoice_req, metadata=metadata)
	return response.payment_request
	##ADDINVOICE END

repeat = 0
##prompt user to specify number of invoices, later used to calculate average time	
while(int(repeat) <= 0):	
	repeat = raw_input("How many invoices to make: ")
##empty invoices from entries		
f = open("invoices.txt", "w") 
f.close()	
	
invoice_list = list()
starttime = time.time() * 1000#milliseconds
##repeat append to list as often as user wanted to
for x in range(int(repeat)):
    invoice_list.append(add_invoice("testinvoice",1500))#send 1500 satoshis which in this case is arbitrary, 1 satoshi = 1e-8 BTC = 0.00000001 BTC
	
endtime = (time.time() * 1000)-starttime
averagetime = endtime / int(repeat)

f = open("invoices.txt", "a")
##write line into file for every element in our list
for line in invoice_list:
	f.write(line + "\n") 	
##print overall and average time per invoice created	
print("time= " + str(endtime) + "ms - average= " + str(averagetime) + "ms")
