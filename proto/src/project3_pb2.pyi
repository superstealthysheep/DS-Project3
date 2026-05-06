from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
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

class GetItemRequest(_message.Message):
    __slots__ = ("item_id",)
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    def __init__(self, item_id: _Optional[str] = ...) -> None: ...

class GetItemResponse(_message.Message):
    __slots__ = ("success", "item")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    success: bool
    item: Item
    def __init__(self, success: bool = ..., item: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class CreateItemRequest(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: Item
    def __init__(self, item: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class CreateItemResponse(_message.Message):
    __slots__ = ("success", "item")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    success: bool
    item: Item
    def __init__(self, success: bool = ..., item: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class UpdateItemRequest(_message.Message):
    __slots__ = ("item_id", "current_version", "new_value")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    NEW_VALUE_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    current_version: str
    new_value: Item
    def __init__(self, item_id: _Optional[str] = ..., current_version: _Optional[str] = ..., new_value: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class UpdateItemResponse(_message.Message):
    __slots__ = ("success", "item")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    success: bool
    item: Item
    def __init__(self, success: bool = ..., item: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = ("node_id",)
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    def __init__(self, node_id: _Optional[str] = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
