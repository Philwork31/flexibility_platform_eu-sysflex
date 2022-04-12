"""
Copyright 2021 AKKA Technologies (philippe.szczech@akka.eu)

Licensed under the EUPL, Version 1.2 or – as soon they will be approved by
the European Commission - subsequent versions of the EUPL (the "Licence");
You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/software/page/eupl

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and
limitations under the Licence.
"""

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime
import json


class SocketConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print('/!\\ Websocket ouverte : {}'.format(datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")))
        async_to_sync(self.channel_layer.group_add)("notification", self.channel_name)

    def disconnect(self, close_code):
        print('/!\\ Websocket close : {}, {}'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), close_code))
        pass

    def notification_event(self, event):
        message = event['text']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    @staticmethod
    def notification_trigger(message):
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "notification",
            {
                "type": "notification_event",
                "text": message,
            },
        )
