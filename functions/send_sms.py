from twilio.rest import Client
import asyncio
from random import randint

#TF7T2Q58GQGXURBUEZ82PGZF
SID='ACc23314fb580658fe9867ea0bf0006b3c'
AUTH='75b0bbdbfa2f0565d36d434d2cff8538'
async def sending_sms(text,receiver):
    code = randint (1000, 9999)
    try:

        # client=Client(SID,AUTH)

        # message=client.messages.create(
        #     body=text+str(code),
        #     from_='+14782177526',
        #     to=receiver
        # )
        print(code)
        return code
    except Exception as exc:
        print (exc)

        return code

