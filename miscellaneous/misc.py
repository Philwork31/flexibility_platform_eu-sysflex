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

from datetime import datetime
import string
import random


class Miscellaneous:

    @staticmethod
    def format_date_with_seconds(non_format_date):
        if "UTC" in non_format_date or "GMT" in non_format_date:
            formatted_date = datetime.strptime(non_format_date, '%a %d %b %Y %H:%M:%S %Z')
        else:
            non_format_date = non_format_date.replace("T", " ")
            if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
                    "PM" in non_format_date:
                formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M:%S %p')
            else:
                non_format_date = non_format_date.replace("T", " ").replace("Z", "")
                formatted_date = datetime.strptime(str(non_format_date), '%Y-%m-%d %H:%M:%S')
        return formatted_date

    @staticmethod
    def format_date_without_seconds(non_format_date):
        print(non_format_date)
        if "UTC" in non_format_date or "GMT" in non_format_date:
            formatted_date = datetime.strptime(non_format_date, '%a %d %b %Y %H:%M:%S %Z')
        else:
            non_format_date = non_format_date.replace("T", " ")
            if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
                    "PM" in non_format_date:
                formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M %p')
            else:
                formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M')
        return formatted_date

    @staticmethod
    def random_string(string_length):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(string_length))

    @staticmethod
    def date_output_estfeed_format(date_object):
        if "Z" in date_object:
            date_result = date_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            date_result = date_object.strftime("%Y-%m-%dT%H:%M:%S")
        return date_result
