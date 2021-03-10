# COEN445-BookingAndScheduler

## Created by
Nicholas Zombolas - 27184271

Yasmine Ghassemi - 40028336

Constantina Roumeliotis - 40002536


Project will be done in Python

## Messages:

### Sent by Client:

REQUEST 	(request meeting)

ACCEPT		(accept meeting invite)

REJECT		(reject meeting invite)

WITHDRAW(MT#)	(withdraw from previously accepted meeting)

ADD		(if client previously rejected meeting invite but now wants to join, they can send this message to server to attempt to regain access to meeting)

CANCEL 		(only organizing client can force cancel a meeting)



### Sent by Server:

RESPONSE 	(response from REQUEST from client)

INVITE 		(inviting various clients to join a meeting)

CONFIRM 	(sent to a particular client, informing them they are attending the meeting)

SCHEDULED 	(if a meeting is confirmed, SCHEDULED is sent to organizer client as final 			confirmation)

CANCEL 		(if a requested meeting doesn't meet the minimum # participants, meeting will be 			canceled with reason "# participants lower than min required". Sent to all clients who 			answered positively to the meeting. If requester cancels meeting there does not
		need to be a reason.)

NOT_SCHEDULED 	(if meeting canceled, this message sent to organizer to inform that meeting could
		not be scheduled)

WITHDRAW(MT#,IP)(notification to organizer that ip x withdrew from the meeting)

ADDED		(sent to organizing client to inform that a new client was added to meeting)

ROOM_CHANGE	(sent to all participants to update the room number for a meeting)
