from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ItemStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ITEM_STATUS_SOLD: _ClassVar[ItemStatus]
    ITEM_STATUS_AVAILABLE: _ClassVar[ItemStatus]
ITEM_STATUS_SOLD: ItemStatus
ITEM_STATUS_AVAILABLE: ItemStatus

class Item(_message.Message):
    __slots__ = ("item_id", "seller_id", "title", "category", "description", "starting_price", "current_price", "quantity", "status", "version")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STARTING_PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    seller_id: str
    title: str
    category: str
    description: str
    starting_price: int
    current_price: int
    quantity: int
    status: ItemStatus
    version: str
    def __init__(self, item_id: _Optional[str] = ..., seller_id: _Optional[str] = ..., title: _Optional[str] = ..., category: _Optional[str] = ..., description: _Optional[str] = ..., starting_price: _Optional[int] = ..., current_price: _Optional[int] = ..., quantity: _Optional[int] = ..., status: _Optional[_Union[ItemStatus, str]] = ..., version: _Optional[str] = ...) -> None: ...
