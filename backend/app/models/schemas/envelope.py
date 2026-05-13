from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class ResponseEnvelope(GenericModel, Generic[DataT]):
    success: bool
    data: DataT | None
    error: dict | None
