from twilio.rest import Client
import asyncio
from random import randint

#С НАСТЕНОГО АКК
#GB7FG4MNX99EUH82EFXPYURS
SID='ACb772b7b3cb5cef93ac1c64599314f921'
AUTH='47ce23ef7eef90b767b6789f0d8e2147'


#TF7T2Q58GQGXURBUEZ82PGZF
#SID='ACc23314fb580658fe9867ea0bf0006b3c'
#AUTH='75b0bbdbfa2f0565d36d434d2cff8538'
async def sending_sms(text,receiver):
    code = randint (1000, 9999)
    try:

        client=Client(SID,AUTH)

        message=client.messages.create(
             body=text+str(code),
             from_='+17403654726',
             to=f'+{receiver}'
         )
        print(code)
        return code
    except Exception as exc:
        print (exc)

        return code

