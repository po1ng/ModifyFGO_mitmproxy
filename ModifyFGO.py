from mitmproxy import http

def request(flow: http:HTTPFlow) ->None:

 
def response(flow: http.HTTPFlow) -> None:
  flow.response.headers["server"] = "nginx"