import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from . import constants as const
from .tag import (
    Elements,
    Fault,
    Properties,
    Status,
    Subscription,
    Tag
)
from .utility import cast_data

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(message)s',
    handlers=[
        # logging.FileHandler("output.log"),
        logging.StreamHandler()
    ]
)


class Client:
    __log = logging.getLogger(f"{__name__}")

    def __init__(self, host: str, port: int = 9500, namespace: str = "ns0"):
        self.ipAddress = host
        self.port = port
        self.url = f"http://{self.ipAddress}:{self.port}/?wsdl"
        self.session = requests.Session()
        self.itemList = []
        self.namespace = namespace
        self.headers = const.HEADERS_SOAP
        self.timeout = 5
        self.backoff = 5

    # used by statement with
    def __enter__(self):
        return self

    # used by statement with
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def _buildEncapsulationHeader(self, namespace: str = "") -> str:
        """
        Build the encapsulation header

        Args:
            namespace(str): override namespace

        Returns:
            header(str): header string
        """

        ns = self.namespace if not namespace else namespace
        header = const.ENVELOPE_OPEN.format(ns=ns)
        header += const.ENVELOPE_HEADER
        header += const.ENVELOPE_BODY_OPEN_NS_1
        header += ns
        header += const.ENVELOPE_BODY_OPEN_NS_2

        return header

    def _buildEncapsulationFooter(self) -> str:
        """
        Build the encapsulation footer

        Returns:
            header(str): header string
        """

        footer = const.ENVELOPE_BODY_CLOSE
        footer += const.ENVELOPE_CLOSE

        return footer

    def set_debug(self, enable: bool):
        if enable:
            self.__log.setLevel(logging.DEBUG)
        else:
            self.__log.setLevel(logging.ERROR)

    def close(self):
        """
        Terminate sessions
        """
        self.session.close()

    def send(self, payload: str, timeout: int = -1) -> bytes:
        """
        Send payload to server

        Args:
            payload(str): payload to be sent
            timeout(int): override self.timeout

        Returns:
            response(str): send response
        """
        timeout = self.timeout if timeout < 0 else timeout

        try:
            response = self.session.post(
                url=self.url,
                data=payload,
                headers=self.headers,
                timeout=timeout
            )
        except requests.ConnectTimeout:
            self.__log.error(f"self.send(): {str(requests.ConnectTimeout)}")
            return b""
        except requests.ConnectionError:
            self.__log.error(f"self.send(): {str(requests.ConnectionError)}")
            return b""
        except requests.Timeout:
            self.__log.error(f"self.send(): {str(requests.Timeout)}")
            return b""
        return response.content

    def browse(
            self,
            namespace: str = "",
            itemPath: str = "",
            itemName: str = "",
            clientRequestHandle: str = "",
            continuationPoint: str = "",
            maxElementsReturned: int = 0,
            browseFilter: str = "all",
            elementNameFilter: str = "",
            vendorFilter: str = "",
            returnAllProperties: bool = False,
            returnPropertyValues: bool = False,
            returnErrorText: bool = False
    ) -> list:
        """
        Browse

        Args:
            namespace:(str),
            itemPath:(str),
            itemName:(str),
            clientRequestHandle:(str),
            continuationPoint:(str),
            maxElementsReturned:(int),
            browseFilter:(str),
            elementNameFilter:(str),
            vendorFilter:(str),
            returnAllProperties:(bool),
            returnPropertyValues:(bool),
            returnErrorText:(bool)

        Returns:
            result(list[ELements]): list of Elements
        """

        ns = self.namespace if not namespace else namespace
        payload = const.XML_VERSION
        payload += self._buildEncapsulationHeader(namespace=ns)
        payload += (
            f'<{ns}:Browse LocaleID="" '
            f'ItemPath="{itemPath}" '
            f'ClientRequestHandle="{clientRequestHandle}" '
            f'ItemName="{itemName}" '
            f'ContinuationPoint="{continuationPoint}" '
            f'MaxElementsReturned="{maxElementsReturned}" '
            f'BrowseFilter="{browseFilter}" '
            f'ElementNameFilter="{elementNameFilter}" '
            f'VendorFilter="{vendorFilter}" '
            f'ReturnAllProperties="{str(returnAllProperties).lower()}" '
            f'ReturnPropertyValues="{str(returnPropertyValues).lower()}" '
            f'ReturnErrorText="{str(returnErrorText).lower()}">'
            f'</{ns}:Browse>'
        )
        payload += self._buildEncapsulationFooter()
        self.__log.debug(f"Sent Browse Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received Browse Response: \n{response}")
        result = self._parseBrowseResponse(content=response)
        return result

    def _parseBrowseResponse(self, content: bytes) -> list:
        """
        Parse Browse response

        Args:
            content(str): the string content to be parsed

        Returns:
            result(list[ELements]): list of Elements
        """

        fault = Fault()
        result = []
        # walk the XML tree and focus on Items as results
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            self.__log.error(f"self._parseBrowseResponse(): {str(ET.ParseError)}")
            result.append(
                Elements(
                    fault=fault._replace(faultcode="ET.ParseError", detail=str(ET.ParseError))
                )
            )
            return result

        for p in root.findall('.//'):
            if "Elements" in p.tag:
                result.append(
                    Elements(
                        xsiType=p.get("{http://www.w3.org/2001/XMLSchema-instance}type").replace("xsd:", ""),
                        hasChildren=(p.attrib["HasChildren"] == "true"),
                        isItem=(p.attrib["IsItem"] == "true"),
                        name=p.attrib["Name"],
                        itemName=p.attrib["ItemName"],
                        itemPath=p.attrib["ItemPath"],
                    )
                )
            elif "faultcode" in p.tag:
                fault = fault._replace(faultcode=p.text)
            elif "faultstring" in p.tag:
                fault = fault._replace(faultstring=p.text)
            elif "detail" in p.tag:
                fault = fault._replace(detail=p.text)

        if fault:
            result.append(Elements(fault=fault))

        return result

    def getProperties(
            self,
            itemList: list = None,
            namespace: str = "",
            localeID: str = "",
            clientRequestHandle: str = "",
            itemPath: str = "",
            returnAllProperties: bool = True,
            returnPropertyValues: bool = True,
            returnErrorText: bool = True
    ) -> list:
        """
        Get Properties of an item(s)

        Args:
            itemList(list[Tag]): list of tag
            namespace(str): override namespace
            localeID(str): language setting
            clientRequestHandle(str): request identifier
            itemPath(str): overall path
            returnAllProperties(bool):
            returnPropertyValues(bool):
            returnErrorText(bool):

        Returns:
            result(Properties): named tuple
        """

        if itemList is None:
            itemList = []
        ns = self.namespace if not namespace else namespace
        tags = self.itemList if not itemList else itemList

        payload = const.XML_VERSION
        payload += self._buildEncapsulationHeader(namespace=ns)
        payload += (
            f'<{ns}:GetProperties '
            f'LocaleID="{localeID}" '
            f'ClientRequestHandle="{clientRequestHandle}" '
            f'ItemPath="{itemPath}" '
            f'ReturnAllProperties="{str(returnAllProperties).lower()}" '
            f'ReturnPropertyValues="{str(returnPropertyValues).lower()}" '
            f'ReturnErrorText="{str(returnErrorText).lower()}"'
            '>'
        )
        items = ""
        for tag in tags:
            itemName = tag.itemName
            itemPath = "" if tag.itemPath is None else tag.itemPath
            items += (
                f'<{ns}:ItemIDs '
                f'ItemPath="{itemPath}" '
                f'ItemName="{itemName}" '
                f'></{ns}:ItemIDs>'
            )
        payload += items
        payload += f'</{ns}:GetProperties>'
        payload += self._buildEncapsulationFooter()
        self.__log.debug(f"Sent GetProperties Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received GetProperties Response: \n{response}")
        result = self._parseGetPropertiesResponse(content=response)
        return result

    def _parseGetPropertiesResponse(self, content: bytes) -> list:
        """
        Parse Get Properties response

        Args:
            content(str): the string content to be parsed

        Returns:
            properties(Properties): named tuple
        """

        # walk the XML tree and focus on Items as results
        result = []
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            self.__log.error(f"self._parseGetPropertiesResponse(): {str(ET.ParseError)}")
            result.append(Properties(error=str(ET.ParseError)))
            return result

        properties = Properties()
        for p in root.findall('.//'):
            if p.tag.endswith("PropertyLists"):
                properties = properties._replace(itemName=p.attrib["ItemName"], itemPath=p.attrib["ItemPath"])
                if properties:
                    result.append(properties)
            elif p.tag.endswith("Properties"):
                name = p.attrib["Name"]
                value = p.find('.//')
                # TODO: properly cast data
                if value is not None:
                    if "dataType" in name:
                        properties = properties._replace(dataType=value.text)
                    elif "value" in name:
                        properties = properties._replace(value=value.text)
                    elif "timestamp" in name:
                        properties = properties._replace(timestamp=value.text)
                    elif "accessRights" in name:
                        properties = properties._replace(accessRights=value.text)
                    elif "scanRate" in name:
                        properties = properties._replace(scanRate=value.text)
                    elif "quality" in name:
                        properties = properties._replace(quality=value.attrib["QualityField"])
                    elif "euType" in name:
                        properties = properties._replace(euType=value.text)
            elif p.tag.endswith("Errors"):
                value = p.find('.//')
                if value is not None:
                    properties = properties._replace(error=value.text)
        if properties:
            result.append(properties)
        return result

    def getStatus(self, clientRequestHandle: str = "", localeID: str = "") -> Status:
        """
        Get the server status

        Args:
            clientRequestHandle(str): request/response identifier
            localeID(str): language settings

        Returns:
            status(Status): tuple that contains server information
        """

        ns = self.namespace
        payload = const.XML_VERSION
        payload += self._buildEncapsulationHeader(namespace=ns)
        payload += f'<{ns}:GetStatus LocaleID="{localeID}" ClientRequestHandle="{clientRequestHandle}" ></{ns}:GetStatus>'
        payload += self._buildEncapsulationFooter()
        self.__log.debug(f"Sent GetStatus Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received GetStatus Response: \n{response}")

        status = Status()
        root = ET.fromstring(response)
        for p in root.findall('.//'):
            if p.tag.endswith("Status"):
                if "ProductVersion" in p.attrib:
                    status = status._replace(productVersion=p.attrib["ProductVersion"])
            elif p.tag.endswith("StatusInfo"):
                status = status._replace(statusInfo=p.text)
            elif p.tag.endswith("VendorInfo"):
                status = status._replace(vendorInfo=p.text)
            elif p.tag.endswith("SupportedLocaleIDs"):
                status = status._replace(supportedLocaleIDs=p.text)
            elif p.tag.endswith("SupportedInterfaceVersions"):
                status = status._replace(supportedInterfaceVersions=p.text)

        return status

    def _buildReadItems(self, itemList: list, namespace: str = "") -> str:
        """
        Build the <Items> content payload for read request

        Args:
            itemList(list):  list of tags
                example:
                [
                    Tag(itemName="//node/path/to/item")
                ]
            namespace(str):  namespace
        Returns:
            items(str):      items that are delimited by new line char

        """

        tags = self.itemList if not itemList else itemList
        ns = self.namespace if not namespace else namespace
        items = ""
        for tag in tags:
            itemName = tag.itemName
            itemPath = tag.itemPath
            items += f'<{ns}:Items '
            if itemName != "":
                items += f'ItemName="{itemName}" '
            if itemPath != "":
                items += f'ItemPath="{itemPath}" '
            items += f'ClientItemHandle="{itemName}"'
            items += f'></{ns}:Items>'
        return items

    def _buildOptionItems(self, options: dict, namespace: str = "") -> str:
        """
        Build the <Options> content payload for a request

        Args:
            options(dict): dict of options
                example: {ReturnItemName="true" ReturnItemPath="true" ReturnItemTime="true"}
            namespace(str): namespace

        Returns:
            option_payload(str): options in XMLDA format

        """
        ns = self.namespace if not namespace else namespace
        option_payload = ""
        if options:
            option_payload += f"<{ns}:Options"
            for o_key, o_value in options.items():
                if isinstance(o_value, bool):
                    o_value = str(o_value).lower()
                option_payload += f" {o_key}=\"{o_value}\""
            option_payload += "/>"
        return option_payload

    def _buildReadPayload(self, itemList: list, options: dict = None, namespace: str = "") -> str:
        """
        Build read request payload that encapsulates a list of <Item> tags

        Args:
            itemList(list[Tag]):  list of tags
                example:
                [
                    Tag(itemName="", itemPath="", value="", type="")
                ]
            namespace(str): override the default namespace
        Returns:
            payload(str):     items that are delimited by new line char
        """

        if options is None:
            options = {}
        ns = self.namespace if not namespace else namespace
        payload = self._buildEncapsulationHeader(namespace=ns)
        payload += f"<{ns}:Read>"
        payload += self._buildOptionItems(options=options, namespace=ns)
        payload += f"<{ns}:ItemList>"
        payload += self._buildReadItems(itemList=itemList, namespace=ns)
        payload += f"</{ns}:ItemList></{ns}:Read>"
        payload += self._buildEncapsulationFooter()
        return payload

    def read(self, itemList: list = None, options: dict = None, namespace: str = "") -> list:
        """
        Read tags data from the server

        Args:
            itemList(list): the list of tags
            options: dict of options
                Example: {ReturnItemName="true" ReturnItemPath="true" ReturnItemTime="true"}
            namespace(str): override the default namespace

        Returns:
            result(list): list of tags
        """

        if itemList is None:
            return []
        if options is None:
            options = {}
        tags = self.itemList if not itemList else itemList
        namespace = self.namespace if not namespace else namespace

        payload = self._buildReadPayload(itemList=tags, options=options, namespace=namespace)
        self.__log.debug(f"Sent Read Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received Read Response: \n{response}")
        result = self._parseReadWriteResponse(content=response)
        return result

    def subscribe(self,
                  itemList: list = None,
                  namespace: str = "",
                  returnValuesOnReply: bool = False,
                  subscriptionPingRate: int = 0,
                  returnErrorText: bool = True,
                  returnDiagnosticInfo: bool = False,
                  returnItemTime: bool = False,
                  returnItemPath: bool = False,
                  returnItemName: bool = False,
                  requestDeadline: str = "",
                  clientRequestHandle: str = "",
                  localeID: str = "",
                  itemPath: str = "",
                  deadband: float = 0.0,
                  requestedSamplingRate: int = 0,
                  enableBuffering: bool = False
                  ) -> Subscription:
        """
        Subscribe item(s)

        Args:
            itemList:list=[Tag],
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
            enableBuffering:bool=False

        Returns:
            result(Subscription): named tuple
        """

        if itemList is None:
            itemList = []
        ns = self.namespace if not namespace else namespace
        tags = self.itemList if not itemList else itemList

        payload = const.XML_VERSION
        payload += self._buildEncapsulationHeader(namespace=ns)
        payload += (
            f'<{ns}:Subscribe '
            f'ReturnValuesOnReply="{str(returnValuesOnReply).lower()}" '
            f'SubscriptionPingRate="{subscriptionPingRate}">'
        )
        payload += (
            f'<{ns}:Options '
            f'xsi:type="{ns}:RequestOptions" '
            f'ReturnErrorText="{str(returnErrorText).lower()}" '
            f'ReturnDiagnosticInfo="{str(returnDiagnosticInfo).lower()}" '
            f'ReturnItemTime="{str(returnItemTime).lower()}" '
            f'ReturnItemPath="{str(returnItemPath).lower()}" '
            f'ReturnItemName="{str(returnItemName).lower()}" '
            f'RequestDeadline="{requestDeadline}" '
            f'ClientRequestHandle="{clientRequestHandle}" '
            f'LocaleID="{localeID}"'
            '>'
            f'</{ns}:Options>'
        )
        payload += (
            f'<{ns}:ItemList '
            f'xsi:type="{ns}:SubscribeRequestItemList" '
            f'ItemPath="{itemPath}" '
            # 'ReqType="" '
            f'Deadband="{deadband}" '
            f'RequestedSamplingRate="{requestedSamplingRate}" '
            f'EnableBuffering="{str(enableBuffering).lower()}"'
            '>'
        )
        items = ""
        for tag in tags:
            itemName = tag.itemName
            itemPath = "" if tag.itemPath is None else tag.itemPath
            items += (
                f'<{ns}:Items '
                f'xsi:type="{ns}:SubscribeRequestItem" '
                f'ItemPath="{itemPath}" '
                # 'ReqType="xsd:unsignedInt" '
                f'ItemName="{itemName}" '
                f'ClientItemHandle="{itemName}" '
                f'Deadband="{deadband}" '
                f'RequestedSamplingRate="{requestedSamplingRate}" '
                f'EnableBuffering="{str(enableBuffering).lower()}"'
                '>'
                f'</{ns}:Items>'
            )
        payload += items
        payload += f'</{ns}:ItemList></{ns}:Subscribe>'
        payload += self._buildEncapsulationFooter()
        self.__log.debug(f"Sent Subscribe Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received Subscribe Response: \n{response}")
        result = self._parseSubscribeResponse(content=response)
        return result

    def _parseSubscribeResponse(self, content: bytes) -> Subscription:
        """
        Parse Subscribe response

        Args:
            content(str): the string content to be parsed

        Returns:
            subscription(Subscription): named tuple
        """

        subscription = Subscription()
        # walk the XML tree and focus on Items as results
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            self.__log.error(f"self._parseSubscribeResponse(): {str(ET.ParseError)}")
            subscription = subscription._replace(error=str(ET.ParseError))
            return subscription

        itemList = []
        for p in root.findall('.//'):
            if p.tag.endswith("SubscribeResponse"):
                attribute = p.attrib["ServerSubHandle"]
                subscription = subscription._replace(serverSubHandle=attribute)
            elif p.tag.endswith("ItemValue"):
                tag_name = p.attrib["ClientItemHandle"]
                value = p.find('.//')
                if value is not None:
                    data_type = value.get("{http://www.w3.org/2001/XMLSchema-instance}type").replace("xsd:", "")
                    itemList.append(
                        {
                            "clientItemHandle": f"{tag_name}",
                            "type": data_type,
                            "value": cast_data(value=value.text, data_type=data_type)
                        }
                    )
            elif p.tag.endswith("Errors"):
                value = p.find('.//')
                if value is not None:
                    subscription = subscription._replace(error=value.text)
        subscription = subscription._replace(items=itemList)
        return subscription

    def subscriptionCancel(self, serverSubHandle: str, clientRequestHandle: str = "", namespace: str = "") -> Fault:
        """
        Subscription Cancel

        Args:
            serverSubHandle(str): the server sub handle identifier
            clientRequestHandle(str): the request/response identifier
            namespace(str): override namespace

        Returns:
            result(Fault): named tuple
        """

        ns = self.namespace if not namespace else namespace
        payload = const.XML_VERSION
        payload += self._buildEncapsulationHeader(namespace=ns)
        payload += (
            f'<{ns}:SubscriptionCancel '
            f'ServerSubHandle="{serverSubHandle}" '
            f'ClientRequestHandle="{clientRequestHandle}">'
            f'</{ns}:SubscriptionCancel>'
        )
        payload += self._buildEncapsulationFooter()
        self.__log.debug(f"Sent SubscriptionCancel Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received SubscriptionCancel Response: \n{response}")
        result = self._parseSubscriptionCancelResponse(content=response)
        return result

    def _parseSubscriptionCancelResponse(self, content: bytes) -> Fault:
        """
        Parse Subscription Cancel response

        Args:
            content(str): the string content to be parsed

        Returns:
            result(Fault): named tuple
        """

        fault = Fault()
        # walk the XML tree and focus on Items as results
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            self.__log.error(f"self._parseSubscriptionCancelResponse(): {str(ET.ParseError)}")
            fault = fault._replace(faultcode="ET.ParseError", detail=str(ET.ParseError))
            return fault

        for p in root.findall('.//'):
            if p.tag.endswith("faultcode"):
                fault = fault._replace(faultcode=p.text)
            elif p.tag.endswith("faultstring"):
                fault = fault._replace(faultstring=p.text)
            elif p.tag.endswith("detail"):
                fault = fault._replace(detail=p.text)
        return fault

    def _buildSubscriptionPolledRefreshItems(self, subscriptions: list, namespace: str = "") -> str:
        """
        Build the <Items> content payload for Subscription Polled Refresh request

        Args:
            subscriptions(list):  list of subscriptions
                example:
                [
                    Subscription(serverSubHandle="//node/path/to/item")
                ]
            namespace(str):  namespace
        Returns:
            items(str):      items that are delimited by new line char
        """

        ns = self.namespace if not namespace else namespace
        items = ""
        for subscription in subscriptions:
            items += f'<{ns}:ServerSubHandles xsi:type="xsd:string">{subscription.serverSubHandle}</{ns}:ServerSubHandles>'

        return items

    def subscriptionPolledRefresh(
            self,
            subscriptions: list,
            namespace: str = "",
            holdTime: str = "",
            waitTime: int = 0,
            returnAllItems: bool = False,
            returnErrorText: bool = True,
            returnDiagnosticInfo: bool = False,
            returnItemTime: bool = False,
            returnItemPath: bool = False,
            returnItemName: bool = False,
            requestDeadline: str = "",
            clientRequestHandle: str = "",
            localeID: str = ""
    ) -> list:
        """
        Poll subscribed items

        Args:
            subscriptions(list):  list of subscriptions
                example:
                [
                    Subscription(serverSubHandle="//node/path/to/item")
                ]
            namespace(str):  namespace
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
            localeID:str=""
        Returns:
            items(str):      items that are delimited by new line char

        """

        ns = self.namespace if not namespace else namespace

        payload = const.XML_VERSION
        payload += self._buildEncapsulationHeader(namespace=ns)
        payload += (
            f'<{ns}:SubscriptionPolledRefresh '
            f'HoldTime="{holdTime}" '
            f'WaitTime="{waitTime}" '
            f'ReturnAllItems="{str(returnAllItems).lower()}">'
        )
        payload += (
            f'<{ns}:Options '
            f'xsi:type="{ns}:RequestOptions" '
            f'ReturnErrorText="{str(returnErrorText).lower()}" '
            f'ReturnDiagnosticInfo="{str(returnDiagnosticInfo).lower()}" '
            f'ReturnItemTime="{str(returnItemTime).lower()}" '
            f'ReturnItemPath="{str(returnItemPath).lower()}" '
            f'ReturnItemName="{str(returnItemName).lower()}" '
            f'RequestDeadline="{requestDeadline}" '
            f'ClientRequestHandle="{clientRequestHandle}" '
            f'LocaleID="{localeID}"'
            '>'
            f'</{ns}:Options>'
        )
        payload += self._buildSubscriptionPolledRefreshItems(subscriptions=subscriptions, namespace=namespace)
        payload += f'</{ns}:SubscriptionPolledRefresh>'
        payload += self._buildEncapsulationFooter()
        self.__log.debug(f"Sent SubscriptionPolledRefresh Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received SubscriptionPolledRefresh Response: \n{response}")
        result = self._parseSubscriptionPolledRefreshResponse(content=response)
        return result

    def _parseSubscriptionPolledRefreshResponse(self, content: bytes) -> list:
        """
        Parse Subscription Polled Refresh response

        Args:
            content(str): the string content to be parsed

        Returns:
            subscription(subscription): named tuple
        """

        result = []
        # walk the XML tree and focus on Items as results
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            self.__log.error(f"self._parseSubscriptionPolledRefreshResponse(): {str(ET.ParseError)}")
            result.append(Subscription(error=str(ET.ParseError)))
            return result

        subscription = Subscription()
        itemList = []
        f = True
        for p in root.findall('.//'):
            if p.tag.endswith("RItemList"):
                if not f:
                    # added items already
                    subscription = subscription._replace(items=itemList)
                    result.append(subscription)
                    subscription = Subscription()
                    itemList = []
                    f = True

                subscription = subscription._replace(serverSubHandle=p.attrib["SubscriptionHandle"])
            elif p.tag.endswith("Items"):
                f = False
                itemName = p.attrib["ClientItemHandle"]
                value = p.find('.//')
                if value is not None:
                    data_type = value.get("{http://www.w3.org/2001/XMLSchema-instance}type").replace("xsd:", "")
                    itemList.append(
                        {
                            "itemName": f"{itemName}",
                            "type": data_type,
                            "value": cast_data(value=value.text, data_type=data_type)
                        }
                    )
            elif p.tag.endswith("Errors"):
                f = False
                value = p.find('.//')
                if value is not None:
                    subscription = subscription._replace(error=value.text)
        if not f:
            subscription = subscription._replace(items=itemList)
            result.append(subscription)

        return result

    def _buildWriteItems(self, itemList: list, namespace: str = "") -> str:
        """
        Build the <Items> content payload for write request

        Args:
            itemList(list):  list of tags
                example:
                [
                    Tag(itemName="//node/path/to/item", itemPath="", value=5, type="unsignedInt")
                ]
            namespace(str):  namespace
        Returns:
            items(str):     items that are delimited by new line char
        """

        ns = self.namespace if not namespace else namespace
        items = ""
        for item in itemList:
            items += (f'<{ns}:Items ClientItemHandle="{item.itemName}" '
                      f'ItemPath="{item.itemPath}" ItemName="{item.itemName}" '
                      f'ValueTypeQualifier="xsd:{item.type}">'
                      f'<Value xsi:Type="xsd:{item.type}">{item.value}</Value></{ns}:Items>'
                      )
        return items

    def _buildWritePayload(self, itemList: list, namespace: str = "") -> str:
        """
        Build write request payload that encapsulates a list of <Item> tags

        Args:
            itemList(list):  list of tags
                example:
                [
                    Tag(itemName="", itemPath="", value="", type="")
                ]
            namespace(str): override the default namespace
        Returns:
            payload(str):     items that are delimited by new line char

        """

        ns = self.namespace if not namespace else namespace
        payload = self._buildEncapsulationHeader(namespace=ns)
        payload += f"<{ns}:Write><{ns}:ItemList>"
        payload += self._buildWriteItems(itemList=itemList, namespace=ns)
        payload += f"</{ns}:ItemList></{ns}:Write>"
        payload += self._buildEncapsulationFooter()
        return payload

    def write(self, itemList: list = None, namespace: str = "") -> list:
        """
        Write tags data to the server

        Args:
            itemList(list): the list of tags
            namespace(str): override the default namespace

        Returns:
            result(list[Tag]): list of tags
        """

        if itemList is None:
            itemList = []
        tags = self.itemList if not itemList else itemList
        ns = self.namespace if not namespace else namespace

        payload = self._buildWritePayload(itemList=tags, namespace=ns)
        self.__log.debug(f"Sent Write Payload: \n{payload}")
        response = self.send(payload=payload)
        self.__log.debug(f"Received Write Response: \n{response}")
        result = self._parseReadWriteResponse(content=response)
        return result

    def _parseReadWriteResponse(self, content: bytes) -> list:
        """
        Parse either Read / Write response

        Args:
            content(str): the string content to be parsed

        Returns:
            result(list[Tag]): list of tags
        """

        result = []
        # walk the XML tree and focus on Items as results
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            self.__log.error(f"self._parseReadWriteResponse(): {str(ET.ParseError)}")
            result.append(Tag(itemName="", error=str(ET.ParseError)))
            return result
        for p in root.findall('.//'):
            if "Items" in p.tag:
                ts = p.attrib.get("Timestamp", None)
                if ts:
                    ts = datetime.fromisoformat(ts)
                tag = Tag(
                    itemName=p.attrib["ClientItemHandle"],
                    timestamp=ts
                )
                value = p.find('.//')
                # get value
                if value is not None:
                    data_type = value.get("{http://www.w3.org/2001/XMLSchema-instance}type").replace("xsd:", "")
                    if "Array" in data_type:
                        values = []
                        for v in value.findall('.//'):
                            values.append(v.text)
                        tag = tag._replace(
                            value=cast_data(value=values, data_type=data_type),
                            type=data_type
                        )
                    else:
                        tag = tag._replace(
                            value=cast_data(value=value.text, data_type=data_type),
                            type=data_type
                        )
                if "ResultID" in p.attrib:
                    tag = tag._replace(error=p.attrib["ResultID"])
                result.append(tag)
            if "Quality" in p.tag:
                if len(result) == 0:
                    result.append(Tag(itemName=""))
                result[-1] = result[-1]._replace(quality={
                    "QualityField": p.attrib["QualityField"],
                    "LimitField": p.attrib["LimitField"],
                    "VendorField": p.attrib["VendorField"]
                })
        return result
