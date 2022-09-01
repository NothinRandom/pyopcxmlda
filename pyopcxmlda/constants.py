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
# PAYLOAD GOES HERE
ENVELOPE_BODY_CLOSE = '</SOAP-ENV:Body>'
ENVELOPE_CLOSE = '</SOAP-ENV:Envelope>'
