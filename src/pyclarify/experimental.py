from typing import List, Optional
import pyclarify
from pyclarify.fields.constraints import ResourceID, IntegrationID
from pyclarify.fields.error import Error
from pyclarify.query.filter import Filter
from pyclarify.query.query import ResourceQuery
from pyclarify.views.generics import Request, Response
from .client import Client
from pydantic import validate_arguments
from enum import Enum


class ExperimentalApiMethod(str, Enum):
    insert = "integration.Insert"
    save_signals = "integration.SaveSignals"
    select_items = "clarify.SelectItems"
    data_frame = "clarify.dataFrame"
    evaluate = "clarify.evaluate"
    select_signals = "admin.SelectSignals"
    publish_signals = "admin.PublishSignals"
    connect_signals = "admin.connectSignals"
    disconnect_signals = "admin.disconnectSignals"


class ExperimentalRequest(Request):
    method: ExperimentalApiMethod


class ExperimentalResponse(Response):
    method: ExperimentalApiMethod


class ExperimentalClient(Client):
    def __init__(self, clarify_credentials):
        super().__init__(clarify_credentials)
        self.update_headers({"X-API-Version": "1.2alpha1"})
        self.update_headers({"User-Agent": f"PyClarify/{pyclarify.__version__}/experimental"})
        self.authenticate(clarify_credentials)
        self.base_url = f"{self.authentication.api_url}rpc"

    def handle_response(self, request: ExperimentalRequest, response) -> ExperimentalResponse:
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
        include: [str] = [],
        dryrun: bool = False,
        integration: IntegrationID = None
        ) -> ExperimentalResponse:

        query = ResourceQuery(
        filter=filter.to_query() if isinstance(filter, Filter) else filter,
        sort=sort,
        limit=limit,
        skip=skip,
        total=total,
        )
        params = {
            "integration": integration, 
            "query": query,
            "item": item,
            "include": include, 
            "format": {"dataAsArray":True,"groupIncludedByType":False}, 
            "dryRun": dryrun
        }

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        request_data = ExperimentalRequest(method="admin.connectSignals", params=params)

        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )
        return self.iterate_requests(request_data, lambda x: False)


    def disconnect_signals(self, 
            filter={},
            skip: int = 0,
            limit: Optional[int] = 20,
            sort: List[str] = [],
            total: Optional[bool] = False,            
            include: [str] = [],
            dryrun: bool = False,
            integration: IntegrationID = None
            ) -> ExperimentalResponse:
            
            query = ResourceQuery(
            filter=filter.to_query() if isinstance(filter, Filter) else filter,
            sort=sort,
            limit=limit,
            skip=skip,
            total=total,
            )
            params = {
                "integration": integration, 
                "query": query,
                "include": include, 
                "format": {"dataAsArray":True,"groupIncludedByType":False}, 
                "dryRun": dryrun
            }

            # assert integration parameter
            if not params["integration"]:
                params["integration"] = self.authentication.integration_id

            request_data = ExperimentalRequest(method="admin.disconnectSignals", params=params)

            self.update_headers(
                {"Authorization": f"Bearer {self.authentication.get_token()}"}
            )
            return self.iterate_requests(request_data, lambda x: False)
