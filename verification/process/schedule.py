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

from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from miscellaneous.misc import Miscellaneous
from verification.models import Schedule


class ScheduleProcess:

    @staticmethod
    def process(new_schedule, new_schedule_dp_date, new_schedule_dp_time, new_schedule_dp_energy, new_schedule_dp_datetime=None):
        schedule_to_create = None

        try:
            if len(new_schedule_dp_time) == 0:
                raise Exception("Empty field(s) in the form.")

            for i in range(len(new_schedule_dp_time)):
                if not new_schedule_dp_time[i] or not new_schedule_dp_date[i] or not \
                        new_schedule_dp_energy[i]:
                    raise Exception("Empty field(s) in the form.")

            for i in range(len(new_schedule_dp_time)):
                if new_schedule_dp_datetime:
                    dp = Miscellaneous.format_date_without_seconds(new_schedule_dp_datetime[i])
                else:
                    dp = Miscellaneous.format_date_with_seconds(new_schedule_dp_date[i] + " " + new_schedule_dp_time[i])

                schedule_to_create = Schedule(product_id=new_schedule.get("product_id"),
                                              fsp_id=new_schedule.get("flexibility_service_provider_id"),
                                              metering_point_id=new_schedule.get("metering_point_id"),
                                              start_of_delivery_period=dp,
                                              energy=new_schedule_dp_energy[i],
                                              )
                schedule_to_create.save()

                # NOTIFICATION
                consumers.SocketConsumer.notification_trigger("Schedule registered for product {} by FSP {}."
                                                              "".format(schedule_to_create.product.product_name,
                                                                        schedule_to_create.fsp.identification))
                event_to_record = EventRecorder(text="%1 registered for product %2 by FSP %3",
                                                business_object_info='[{{"order" : 1, "type": "schedule", "id": "{}",'
                                                                     ' "text": "Schedule"}}, '
                                                                     '{{"order" : 2, "type": "product", '
                                                                     '"id": "{}", "text": "{}"}}, '
                                                                     '{{"order" : 3, "type": '
                                                                     '"fsp", "id": "{}", "text": "{}"}}]'.
                                                format(schedule_to_create.id,
                                                       schedule_to_create.product.id,
                                                       schedule_to_create.product.product_name,
                                                       schedule_to_create.fsp.id,
                                                       schedule_to_create.fsp.identification),
                                                types="schedule")
                event_to_record.save()

            message = "Schedule registered with success."
        except Exception as e:
            message = "Schedule registration failed : {}".format(e)

        return [schedule_to_create, message]