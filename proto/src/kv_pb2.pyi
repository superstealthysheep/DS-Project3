from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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
    starting_price: float
    current_price: float
    quantity: int
    status: str
    version: int
    def __init__(self, item_id: _Optional[str] = ..., seller_id: _Optional[str] = ..., title: _Optional[str] = ..., category: _Optional[str] = ..., description: _Optional[str] = ..., starting_price: _Optional[float] = ..., current_price: _Optional[float] = ..., quantity: _Optional[int] = ..., status: _Optional[str] = ..., version: _Optional[int] = ...) -> None: ...

class CreateItemRequest(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: Item
    def __init__(self, item: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class CreateItemResponse(_message.Message):
    __slots__ = ("ok", "item_id", "pod")
    OK_FIELD_NUMBER: _ClassVar[int]
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    POD_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    item_id: str
    pod: str
    def __init__(self, ok: bool = ..., item_id: _Optional[str] = ..., pod: _Optional[str] = ...) -> None: ...

class GetItemRequest(_message.Message):
    __slots__ = ("item_id",)
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    def __init__(self, item_id: _Optional[str] = ...) -> None: ...

class GetItemResponse(_message.Message):
    __slots__ = ("found", "item", "pod")
    FOUND_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    POD_FIELD_NUMBER: _ClassVar[int]
    found: bool
    item: Item
    pod: str
    def __init__(self, found: bool = ..., item: _Optional[_Union[Item, _Mapping]] = ..., pod: _Optional[str] = ...) -> None: ...

class SearchItemsRequest(_message.Message):
    __slots__ = ("keyword", "category")
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    keyword: str
    category: str
    def __init__(self, keyword: _Optional[str] = ..., category: _Optional[str] = ...) -> None: ...

class SearchItemsResponse(_message.Message):
    __slots__ = ("items", "pod")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    POD_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[Item]
    pod: str
    def __init__(self, items: _Optional[_Iterable[_Union[Item, _Mapping]]] = ..., pod: _Optional[str] = ...) -> None: ...

class UpdateItemRequest(_message.Message):
    __slots__ = ("item_id", "item")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    item: Item
    def __init__(self, item_id: _Optional[str] = ..., item: _Optional[_Union[Item, _Mapping]] = ...) -> None: ...

class UpdateItemResponse(_message.Message):
    __slots__ = ("ok", "new_version", "pod")
    OK_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSION_FIELD_NUMBER: _ClassVar[int]
    POD_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    new_version: int
    pod: str
    def __init__(self, ok: bool = ..., new_version: _Optional[int] = ..., pod: _Optional[str] = ...) -> None: ...

class PlaceBidRequest(_message.Message):
    __slots__ = ("item_id", "bidder_id", "bid_amount")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    BIDDER_ID_FIELD_NUMBER: _ClassVar[int]
    BID_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    bidder_id: str
    bid_amount: float
    def __init__(self, item_id: _Optional[str] = ..., bidder_id: _Optional[str] = ..., bid_amount: _Optional[float] = ...) -> None: ...

class PlaceBidResponse(_message.Message):
    __slots__ = ("ok", "new_price", "pod")
    OK_FIELD_NUMBER: _ClassVar[int]
    NEW_PRICE_FIELD_NUMBER: _ClassVar[int]
    POD_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    new_price: float
    pod: str
    def __init__(self, ok: bool = ..., new_price: _Optional[float] = ..., pod: _Optional[str] = ...) -> None: ...

class JoinAuctionRequest(_message.Message):
    __slots__ = ("item_id", "bidder_id")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    BIDDER_ID_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    bidder_id: str
    def __init__(self, item_id: _Optional[str] = ..., bidder_id: _Optional[str] = ...) -> None: ...

class AuctionUpdate(_message.Message):
    __slots__ = ("item_id", "current_price", "bidder_id", "status", "timestamp")
    ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    BIDDER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    item_id: str
    current_price: float
    bidder_id: str
    status: str
    timestamp: int
    def __init__(self, item_id: _Optional[str] = ..., current_price: _Optional[float] = ..., bidder_id: _Optional[str] = ..., status: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...
