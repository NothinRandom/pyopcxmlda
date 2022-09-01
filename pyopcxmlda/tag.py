from typing import NamedTuple, Any, Optional
from reprlib import repr as _r


__all__ = ["Tag"]


class Fault(NamedTuple):
    faultcode: Optional[str] = ''
    faultstring: Optional[str] = ''
    detail: Optional[str] = ''


    def __bool__(self):
        """
        ``True`` if both ``value`` is not ``None`` and ``error`` is ``None``
        ``False`` otherwise
        """
        return self.faultcode is not '' or self.faultstring is not '' or self.detail is not ''


    def __str__(self):
        return (
            f"{self.faultcode},"
            f"{(self.faultstring)},"
            f"{(self.detail)}"
        )


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"faultcode={self.faultcode!r}, "
            f"faultstring={self.faultstring!r}, "
            f"detail={self.detail!r}"
            ")"
        )


class Tag(NamedTuple):
    itemName: str                   #: item name tag read/written or request name
    value: Optional[Any] = None     #: value read/written, may be ``None`` on error
    itemPath: Optional[str] = ''    #: item path
    type: Optional[str] = ''        #: data type of tag
    error: Optional[str] = ''       #: error message if unsuccessful, else ``None``


    def __bool__(self):
        """
        ``True`` if both ``value`` is not ``None`` and ``error`` is ``None``
        ``False`` otherwise
        """
        return self.value is not None and self.error is None


    def __str__(self):
        return f"{self.itemName}, {_r(self.value)}, {self.type}, {self.itemPath}, {self.error}"


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"itemName={self.itemName!r},"
            f"value={self.value!r},"
            f"itemPath={self.itemPath!r},"
            f"type={self.type!r},"
            f"error={self.error!r}"
            ")"
        )


class Status(NamedTuple):
    statusInfo: Optional[str] = ''
    vendorInfo: Optional[str] = ''
    supportedLocaleIDs: Optional[str] = ''
    supportedInterfaceVersions: Optional[str] = ''
    productVersion: Optional[str] = ''


    def __str__(self):
        return (
            f"{self.statusInfo},"
            f"{_r(self.vendorInfo)},"
            f"{self.supportedLocaleIDs},"
            f"{self.supportedInterfaceVersions},"
            f"{self.productVersion}"
        )


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"StatusInfo={self.statusInfo!r}, "
            f"VendorInfo={self.vendorInfo!r}, "
            f"SupportedLocaleIDs={self.supportedLocaleIDs!r}, "
            f"SupportedInterfaceVersions={self.supportedInterfaceVersions!r}, "
            f"ProductVersion={self.productVersion!r}"
            ")"
        )


class Properties(NamedTuple):
    itemPath: Optional[str] = ''
    itemName: Optional[str] = ''
    dataType: Optional[str] = ''
    value: Optional[Any] = None
    timestamp: Optional[str] = '' 
    accessRights: Optional[str] = ''
    scanRate: Optional[str] = ''
    quality: Optional[str] = ''
    euType: Optional[str] = ''
    error: Optional[str] = ''


    def __bool__(self):
        """
        ``True`` ``value`` is not ``None``
        ``False`` otherwise
        """
        return self.value is not None or self.error is not ''


    def __str__(self):
        return (
            f"{self.itemPath},"
            f"{self.itemName},"
            f"{self.dataType},"
            f"{_r(self.value)},"
            f"{self.timestamp},"
            f"{self.accessRights},"
            f"{self.scanRate},"
            f"{self.quality},"
            f"{self.euType},"
            f"{self.error}"
        )


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"itemPath={self.itemPath!r}, "
            f"itemName={self.itemName!r}, "
            f"dataType={self.dataType!r}, "
            f"value={self.value!r}, "
            f"timestamp={self.timestamp!r}, "
            f"accessRights={self.accessRights!r}, "
            f"scanRate={self.scanRate!r}, "
            f"quality={self.quality!r}, "
            f"euType={self.euType!r}, "
            f"error={self.error!r})"
        )


class Subscription(NamedTuple):
    serverSubHandle: Optional[str] = ''
    items: Optional[list] = []
    error: Optional[str] = ''


    def __str__(self):
        return (
            f"{self.serverSubHandle},"
            f"{_r(self.items)},"
            f"{_r(self.error)}"
        )


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"serverSubHandle={self.serverSubHandle!r}, "
            f"items={self.items!r}), "
            f"error={self.error!r}"
            ")"
        )


class Elements(NamedTuple):
    xsiType: Optional[str] = ''
    hasChildren: Optional[bool] = False
    isItem: Optional[bool] = False 
    name: Optional[str] = ''
    itemName: Optional[str] = ''
    itemPath: Optional[str] = ''
    fault: Optional[Fault] = None


    def __str__(self):
        return (f"{self.xsiType},"
            f"{_r(self.hasChildren)},"
            f"{self.isItem},"
            f"{self.name},"
            f"{self.itemName},"
            f"{self.itemPath},"
            f"{self.fault}"
        )


    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"xsiType={self.xsiType!r}, "
            f"hasChildren={self.hasChildren!r}, "
            f"isItem={self.isItem!r}, "
            f"name={self.name!r}, "
            f"itemName={self.itemName!r}, "
            f"itemPath={self.itemPath!r},"
            f"fault={self.fault!r}"
            ")"
        )
