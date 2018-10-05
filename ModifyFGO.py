import os
import execjs

os.environ["NODE_PATH"] = os.getcwd()+"/node_modules"
def request(flow):
    #jsstr = get_js()
    #ctx = execjs.compile(jsstr)
    #return (ctx.call('beforeSendRequest', request))

def response(flow):
    #jsstr = get_js()
    #ctx = execjs.compile(jsstr)
    #return (ctx.call('beforeSendResponse', response))

def http_connect(flow):
  if flow.request.host.find('bilibiligame.net') ==- 1:
    flow.response = http.HTTPResponse.make(
      404,''
    )

def get_js():
    f = open("fgo.js", 'r', encoding='utf-8') # 打开JS文件
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr+line
        line = f.readline()
    return htmlstr