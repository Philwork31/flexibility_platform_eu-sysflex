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

from flexibility_platform.models import FlexibilityServiceProvider


class FSP:

    @staticmethod
    def get_fsp_id_by_identification(identification):
        fsp_identification = FlexibilityServiceProvider.objects.values_list('id', flat=True).get(identification=identification)
        return fsp_identification

    @staticmethod
    def get_fsp_identification_by_id(id):
        fsp_id = FlexibilityServiceProvider.objects.values_list('identification', flat=True).get(id=id)
        return fsp_id
