# pyopcxmlda
A Python3 implementation of OPC XML DA.

## Installation 
```console 
pip3 install pyopcxmlda
```

## Supported functions
* Browse
    * browse server
* Get Properties
    * get item properties for a set of items
* Get Status
    * get status of server, vendor specific info, etc
* Read
    * read a set of item values
* Subscribe
    * subscribe a set of item values
* Subscription Cancel
    * cancel a subscription
* Subscription Polled Refresh
    * poll subscribed items
* Write
    * write a set of item values


## How to use pyopcxmlda 
### 1. Connect and Send Commands
```python
from datetime import datetime
from pyopcxmlda import Client
from pyopcxmlda.tag import Tag
from pyopcxmlda.constants import DataType

"""
Typical data types:
    * boolean
    * byte
    * short
    * unsignedShort
    * int
    * unsignedInt
    * float
    * double
    * long
    * unsignedLong
    * decimal
    * string
    * dateTime
"""

__ITEMS = [
    Tag(itemName="//path/to/node/item1", value=-10, type=DataType.INT),
    Tag(itemName="//path/to/node/item2", value=10, type=DataType.UINT),
    Tag(itemName="//path/to/node/item3", value=-10.0, type=DataType.FLOAT),
    Tag(itemName="//path/to/node/item4", value=-1000, type=DataType.LONG)
]

__HOST = '192.168.1.15' # REQUIRED
__PORT = 9500           # OPTIONAL: default is 9500
__NAMESPACE = 'ns0'     # OPTIONAL: default is 'ns0'


with Client(host=__HOST, port=__PORT, namespace=__NAMESPACE) as plc:
    """
    Browse OPC nodes
        example: browse specified path

    Args:
        namespace:str="", 
        itemPath:str="", 
        clientRequestHandle:str="",
        itemName:str="",
        continuationPoint:str="",
        maxElementsReturned:int=0, 
        browseFilter:str="all",
        elementNameFilter:str="",
        vendorFilter:str="",
        returnAllProperties:bool=False,
        returnPropertyValues:bool=False,
        returnErrorText:bool=False
    Returns:
        list[elements]: list of Elements
            example:
                [
                    Elements(
                        xsiType='ns1:BrowseElement', 
                        hasChildren=False, 
                        isItem=True, 
                        name='item', 
                        itemName='//path/to/valid/item', 
                        itemPath='',
                        fault=None
                    )
                ]
    Notes:
        Elements has a sub Fault class that is filled on error
            example:
                [
                    Elements(
                        xsiType='', 
                        hasChildren=False, 
                        isItem=False, 
                        name='', 
                        itemName='', 
                        itemPath='',
                        fault=Fault(
                            faultcode='ns1:E_UNKNOWNITEMNAME', 
                            faultstring='E_UNKNOWNITEMNAME', 
                            detail='Browse invalid/unknown item path/name=//path/to/invalid/item'
                        )
                    )
        to access the fields of each entry in result
            for element in result:
                print((f'xsiType:{element.xsiType}, '
                        f'hasChildren:{element.HasChildren}, '
                        f'isItem:{element.IsItem}, '
                        f'name:{element.Name}, '
                        f'itemName:{element.ItemName}, '
                        f'itemPath:{element.ItemPath}'))
    """
    # to browse root
    response = plc.browse()
    # to specified path
    response = plc.browse(itemName="//path/")



    """
    Get Properties of an item(s)

    Args:
        itemList:list=[], 
        namespace:str="",
        localeID:str="",
        clientRequestHandle:str="",
        itemPath:str="",
        returnAllProperties:bool=True,
        returnPropertyValues:bool=True,
        returnErrorText:bool=True

    Returns:
        list[Properties]: list of named tuple
            example:
                [
                    Properties(
                        itemPath='', 
                        itemName='//path/to/node', 
                        dataType='unsignedInt', 
                        value=3620759, 
                        timestamp='2022-08-31T18:23:04Z', 
                        accessRights='readable', 
                        scanRate='10', 
                        quality='good', 
                        euType='noEnum', 
                        error=''
                    )
                ]
    """
    response = plc.getProperties(itemList=__ITEMS)



    """
    Get the server status

    Args:
        clientRequestHandle(str): request/response identifier
        localeID(str): language settings

    Returns:
        Status: tuple that contains server information
            example: 
                Status(
                    statusInfo="Running",
                    vendorInfo='Test',
                    supportedLocaleIDs="en",
                    supportedInterfaceVersions="XML_DA_Version_1_0",
                    productVersion="MyMachine"
                )
    """
    response = plc.getStatus()



    """
    Read mixed item values
        example: read randomly mixed data types

    Args:
        itemList(list[Tag])[Required]: list of data class Tag
            example: itemList=__ITEMS
        namespace(str): override namespace
            example: namespace="ns1"
    Returns:
        list[Tag]: list of Tag
            example:
                [
                    Tag(
                        itemName='//path/to/node/item2',
                        value=3556464,
                        itemPath='',
                        type='unsignedInt',
                        error=''
                    )
                ]
    Notes:
        look at __ITEMS to understand named tuple setup
        to access the fields of each entry in result
            for tag in read_result:
                print((f'device:{tag.device}, '
                        f'value:{tag.value}, '
                        f'data_type:{tag.type}, '
                        f'status:{tag.error}'))
    """
    read_result = plc.read(itemList=__ITEMS)



    """
    Subscribe a set of item values

    Args:
        itemList:list=[],
        namespace:str="",
        returnValuesOnReply:bool=False,
        subscriptionPingRate:int=0,
        returnErrorText:bool=True,
        returnDiagnosticInfo:bool=False,
        returnItemTime:bool=False,
        returnItemPath:bool=False,
        returnItemName:bool=False,
        requestDeadline:str="",
        clientRequestHandle:str="",
        localeID:str="",
        itemPath:str="",
        deadband:float=0.0,
        requestedSamplingRate:int=0,
        enableBuffering:bool=False,

    Returns:
        Subscription: tuple that contains subscription information
            example: 
                Subscription(
                    ServerSubHandle="1657752351",
                    error='',
                    items=[
                        {
                            'ClientItemHandle': '//path/to/node', 
                            'type': 'unsignedInt', 
                            'value': 6229
                        }
                    ]
                )
    """
    response = plc.subscribe(itemList=__ITEMS)



    """
    Cancel specified subscription

    Args:
        serverSubHandle:str, 
        clientRequestHandle:str="", 
        namespace:str=""

    Returns:
        Fault: tuple that contains fault information
            example: fault exists on invalid handle
                Fault(
                    faultcode="ns1:E_NOSUBSCRIPTION",
                    faultstring="E_NOSUBSCRIPTION",
                    detail="Subscription not found"
                )
    """
    response = plc.subscriptionCancel(serverSubHandle="3621660")



    """
    Poll subscribed items

    Args:
        subscriptions:list[Subscription],
        holdTime:str="",
        waitTime:int=0,
        returnAllItems:bool=False,
        returnErrorText:bool=True,
        returnDiagnosticInfo:bool=False,
        returnItemTime:bool=False,
        returnItemPath:bool=False,
        returnItemName:bool=False,
        requestDeadline:str="",
        clientRequestHandle:str="",
        localeID:str="",
        namespace:str=""

    Returns:
        Fault: tuple that contains fault information
            example: fault exists on invalid handle
                [
                    Subscription(
                        serverSubHandle='1657752363', 
                        items=[
                            {
                                'itemName': '//path/to/node1', 
                                'type': 'unsignedInt', 
                                'value': 3624471
                            }, 
                            {
                                'itemName': '//path/to/node2', 
                                'type': 'unsignedInt', 
                                'value': 6241
                            }
                        ]
                    ), 
                    error='')
                ]
    """
    response = plc.subscriptionPolledRefresh(subscriptions=__SUBSCRIPTIONS)



    """
    Write mixed item values
        example: write randomly mixed data types

    Args:
        itemList(list[Tag])[Required]: list of data class Tag
            example: itemList=__ITEMS
        namespace(str): override namespace
            example: namespace="ns1"
    Returns:
        list[Tag]: list of incorrectly defined Tag or access
            example:
                [
                    Tag(
                        itemName='//path/to/item',
                        value='',
                        itemPath='',
                        type='',
                        error='E_READONLY'
                    )
                ]
    Notes:
        look at __ITEMS to understand named tuple setup
    """
    response = plc.write(itemList=__ITEMS)

```
