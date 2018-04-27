import sys
import requests


# Description: Helper function to create object of given object 
# Params: 
# return: 
# TODO: 
def jsonify(encoded):
	decoded = '';

	try:
		decoded = encoded.json()
	except ValueError:
		sys.exit("Error in jsonify: ", sys.exc_info()[0])

	return decoded


# Description: Returns item(s) to be scanned by avast
# Params: argv - list of arguments given at cmd line
# return: item at [0th] of argv
# TODO: For testing puproses, remove for bounties later
def getItem(argv):
	return argv[1];


def getArtifact(hash):
	print('Sending GET')
	repsonse = ''

	try:
		response = requests.get('http://localhost:31337/artifacts/'+hash+'/0')

	print('Sent GET')
	json = jsonify(response)

	print(json)

	return True


# Description: Unlock test account for use
# Params: N/A
# return: 1 for success, 0 for fail
# TODO: Create new account, take account as argument
def unlockAccount():

	#unlock account
	headers = {'Content-Type': 'application/json'}
	dataUnlock = '{"password": "password"}'
	try:
		response = requests.post('http://localhost:31337/accounts/af8302a3786a35abeddf19758067adc9a23597e5/unlock', headers=headers, data=dataUnlock)
	
	except:
		print("Error in unlockAccount: ", sys.exc_info()[0])

	unlockJSON = jsonify(response)
	statusUnlock = unlockJSON['status']

	#check that acocunt was unlocked
	if statusUnlock !='OK':
		print(unlockJSON)		
		return False

	print("Unlock: "+ statusUnlock)

	return True


# Description: Retrieve hash from polyswarm of bounty
# Params: Hash of bounty
# return: TODO
# TODO: Look at ipfs for bounty
def getAllBounties():

	#get list of bounties
	response = requests.get('http://localhost:31337/bounties')
	json = jsonify(response)
	result = json['result']

	guidList = []
	uriList = []

	#parse out guid for each
	for i in range(0, len(result)):
		curResult = result[i]
		uriList.append(curResult['uri'])
		guidList.append(curResult['guid'])


	return (guidList, uriList)


# Description: Upload artifact
# Params: file to upload
# return: id of bounty
# TODO: 
def postArtifact(item):

	headers = {'Content-Type': 'application/json'}
	file =  {'file': open(item, 'rb')}
	response = requests.post('http://localhost:31337/artifacts', headers=headers, files=file)

	print(response.url)

	json  = response.json()
	print(json)
	if json['status'] is not 'OK':
		sys.exit("Error in postArtifact: "+ json['message'])

	print(json)
	#get id of artifact posted
	artifact = json['result']

	print("Artifact: "+ artifact);

	return artifact


# Description: Create bounty on polyswarm
# Params: id of artifact uploaded
# return: hash of bounty
# TODO: Parse response for return value
def postBounty(id):

	headers = {'Content-Type': 'application/json'}
	data = '{"amount": "62500000000000000", "uri": '+id+', "duration": 10}'

	try:
		response = requests.post('http://localhost:31337/bounties', headers=headers, data=data)
	except:
		print("Error in postBounty: ", sys.exc_info()[0])		

	#parse for success/status
	json = jsonify(response)



	print("postBounty:")
	print(json['guid'])

	return json['result']


# Description: Relay verdict to swarm
# Params: Verdict - true or false, Hash - the bounty that was scanned
# return: status of post
# TODO: Parse resposne
def sendVerdict(verdict, hash):

	headers = {'Content-Type': 'application/json'}
	data = '{"verdicts": ['+verdict+']}'

	try:
		response = requests.post('http://localhost:31337/bounties/'+hash+'/settle', headers=headers, data=data)
	except:
		print("Error in sendVerdict: ", sys.exc_info()[0])

	#parse for success/status
	json = jsonify(response)

	print("sendVerdict:")
	print(json)

	return json['status']


# Description: Take artifact from user for a hard coded bounty. Send a verdict
# Params: N/A
# return: N/A
# TODO: N/A
def runPolyswarmTest(item, verdict):

	#unlock
	if unlockAccount() is False:
		sys.exit("Error in main: Invalid Account")

	#upload aritfact
	id = postArtifact(item)

	#create bounty
	hash = postBounty(id)

	#get bounty item
	#bounty = getBounty(hash)

	#assert verdict
	if sendVerdict(verdict, hash) is not 'OK':
		sys.exit("Error attempting to send verdict for bounty "+hash+". Try again")

	return 1

# Description: Listen for bounty for over websocket. Scan and assert
# Params: N/A
# return: N/A
# TODO: All
def waitForBounties():
	return