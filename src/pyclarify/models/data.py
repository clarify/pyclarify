from pydantic import BaseModel
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime


class ClarifyDataFrame(BaseModel):
    times: List[datetime] = None
    series: Dict[str, List[Union[float, int, None]]] = None