HEADERS = {'content-type': 'text/xml'}

HEADERS_SOAP = {'content-type': 'application/soap+xml'}

XML_VERSION = '<?xml version="1.0" encoding="UTF-8"?>'

ENVELOPE_OPEN = (
    '<SOAP-ENV:Envelope '
    'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
    'xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
    'xmlns:{ns}="http://opcfoundation.org/webservices/XMLDA/1.0/">'
)
ENVELOPE_HEADER = '<SOAP-ENV:Header></SOAP-ENV:Header>'
ENVELOPE_BODY_OPEN = '<SOAP-ENV:Body>'
ENVELOPE_BODY_OPEN_NS_1 = '<SOAP-ENV:Body xmlns:'
ENVELOPE_BODY_OPEN_NS_2 = '="http://opcfoundation.org/webservices/XMLDA/1.0/">'
# PAYLOAD GOES HERE
ENVELOPE_BODY_CLOSE = '</SOAP-ENV:Body>'
ENVELOPE_CLOSE = '</SOAP-ENV:Envelope>'


class DataType:
    BOOL        = 'boolean'
    BYTE        = 'byte'
    UBYTE       = 'unsignedByte'
    SHORT       = 'short'
    USHORT      = 'unsignedShort'
    INT         = 'int'
    UINT        = 'unsignedInt'
    FLOAT       = 'float'
    DOUBLE      = 'double'
    LONG        = 'long'
    ULONG       = 'unsignedLong'
    DECIMAL     = 'decimal'
    STRING      = 'string'
    DATETIME    = 'dateTime'
    ARRAY       = 'ArrayOf'
