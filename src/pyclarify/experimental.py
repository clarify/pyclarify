from datetime import datetime, timedelta
from typing import List, Optional, Union
from pydantic.json import timedelta_isoformat
import pyclarify
from pyclarify.__utils__.time import time_to_string
from pyclarify.fields.constraints import ApiMethod, ResourceID, IntegrationID
from pyclarify.fields.error import Error
from pyclarify.views.dataframe import DataFrameParams, InsertParams
from pyclarify.views.generics import Response
from pyclarify.views.evaluate import EvaluateParams
from pyclarify.views.items import PublishSignalsParams, SelectItemsParams
from pyclarify.views.signals import SaveSignalsParams, SelectSignalsParams
from .client import Client
from pydantic import BaseModel, ConfigDict, model_validator
from enum import Enum
from typing_extensions import deprecated


class ExperimentalApiMethod(str, Enum):
    # Same values as ApiMethod; the client sends the names each API version expects.
    insert = "integration.insert"
    save_signals = "integration.saveSignals"
    select_items = "clarify.selectItems"
    data_frame = "clarify.dataFrame"
    evaluate = "clarify.evaluate"
    select_signals = "admin.selectSignals"
    publish_signals = "admin.publishSignals"
    connect_signals = "admin.signals.connect"
    disconnect_signals = "admin.signals.disconnect"



class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ExperimentalApiMethod = ApiMethod.select_items
    id: Union[str,int] = "1"
    params: Union[
        dict,
        InsertParams,
        SaveSignalsParams,
        SelectItemsParams,
        SelectSignalsParams,
        PublishSignalsParams,
        DataFrameParams,
        EvaluateParams] = {}
    # TODO[pydantic]: The following keys are deprecated: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={timedelta: timedelta_isoformat, datetime: time_to_string})


class ExperimentalRequest(JSONRPCRequest):
    method: ExperimentalApiMethod

    @model_validator(mode='after')
    @classmethod
    def use_correct_params_based_on_method(cls, values):
        if values.method == ApiMethod.insert:
           values.params = InsertParams(**values.params)
        elif values.method == ApiMethod.save_signals:
           values.params = SaveSignalsParams(**values.params)
        elif values.method == ApiMethod.select_items:
           values.params = SelectItemsParams(**values.params)
        elif values.method == ApiMethod.select_signals:
           values.params = SelectSignalsParams(**values.params)
        elif values.method == ApiMethod.publish_signals:
           values.params = PublishSignalsParams(**values.params)
        elif values.method == ApiMethod.data_frame:
           values.params = DataFrameParams(**values.params)
        elif values.method == ApiMethod.evaluate:
           values.params = EvaluateParams(**values.params)
        return values


class ExperimentalResponse(Response):
    method: Optional[ExperimentalApiMethod] = None


@deprecated('ExperimentalClient is deprecated, use Client(..., api_version="1.2") instead.')
class ExperimentalClient(Client):
    """
    Deprecated, use ``Client(..., api_version="1.2")``. Talks to the 1.2alpha1 pre-release,
    which the API now serves as 1.2beta1.
    """

    def __init__(self, clarify_credentials):
        super().__init__(clarify_credentials, api_version="1.2alpha1")
        self.update_headers({"User-Agent": f"PyClarify/{pyclarify.__version__}/experimental"})
        super().__post_init__()

    def handle_response(self, request, response) -> ExperimentalResponse:
        """
        :meta private:
        """
        if not response.ok:
            err = {
                "code": response.status_code,
                "message": f"HTTP Response Error: {response.reason}",
                "data": response.text,
            }
            return ExperimentalResponse(id=request.id, error=Error(**err))
        response = response.json()
        if hasattr(response, "error"):
            return ExperimentalResponse(id=request.id, error=response["error"])
        response["method"] = request.method
        return ExperimentalResponse(**response)

    def connect_signals(self,
        filter={},
        skip: int = 0,
        limit: Optional[int] = 20,
        sort: List[str] = [],
        total: Optional[bool] = False,
        item: ResourceID = "",
        include: List[str] = [],
        dryrun: bool = False,
        integration: IntegrationID = None
        ) -> ExperimentalResponse:
        """See Client.connect_signals, which takes ``dry_run`` instead of ``dryrun``."""
        return super().connect_signals(
            item=item,
            filter=filter,
            skip=skip,
            limit=limit,
            sort=sort,
            total=total,
            include=include,
            dry_run=dryrun,
            integration=integration,
        )

    def disconnect_signals(self,
        filter={},
        skip: int = 0,
        limit: Optional[int] = 20,
        sort: List[str] = [],
        total: Optional[bool] = False,
        include: List[str] = [],
        dryrun: bool = False,
        integration: IntegrationID = None
        ) -> ExperimentalResponse:
        """See Client.disconnect_signals, which takes ``dry_run`` instead of ``dryrun``."""
        return super().disconnect_signals(
            filter=filter,
            skip=skip,
            limit=limit,
            sort=sort,
            total=total,
            include=include,
            dry_run=dryrun,
            integration=integration,
        )
