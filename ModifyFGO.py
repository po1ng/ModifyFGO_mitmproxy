from mitmproxy import http
import re
import json
import base64
import urllib

def readSetting(url) :
  uid = re.search(r'\d{12}',url,re.I)
  return json.loads(readFile(profile+uid+'setting.json'))

def readFile(path) :
  file_object = open(path)
  try:
    file_context = file_object.read()
    return file_context
  finally:
    file_object.close()

def wirteFile(path, content) :
  with open(path, 'w') as f:
    f.write(content)

def replaceSvt(sv, id) :
	svt = json.loads(readFile('./svtData.json'))
	sv["svtId"] = svt["svt"][id]["id"]
	sv["treasureDeviceId"] = svt["svt"][id]["tdid"]
	sv["skillId1"] = svt["svt"][id]["sk1"]
	sv["skillId2"] = svt["svt"][id]["sk2"]
	sv["skillId3"] = svt["svt"][id]["sk3"]
	sv["hp"] = svt["svt"][id]["hp"]
	sv["atk"] = svt["svt"][id]["atk"]
	if svt["svt"][id]["limit"] :
		sv["limitCount"] = 0
		sv["dispLimitCount"] = 0
		sv["commandCardLimitCount"] = 0
		sv["iconLimitCount"] = 0

def isUndefined(var) :
  return isinstance(var, int) or var.isalpha()

mitmSetting = readFile('./setting.txt')
profile = re.search(r'profile=.*',mitmSetting,re.I)
serverAddress = re.search(r'serverAddress=.*',mitmSetting,re.I)

def http_connect(flow):
  if flow.request.host.find('bilibiligame.net') ==- 1:
    flow.response = http.HTTPResponse.make(
      404,''
    )

def request(flow: http.HTTPFlow) -> None :
  if flow.request.url.find(serverAddress) > -1 :
    uid = re.search(r'\d{12}',flow.request.url,re.I)
    request_str = str(flow.request.content, encoding='utf-8')
    wirteFile(profile+uid+'setting.json', request_str)
  if flow.request.url.find("ac.php") > -1 :
    query_key = flow.request.urlencoded_form['key']
    if query_key == "battleresult" :
      request_str = str(flow.request.content, encoding='utf-8')
      request_str = request_str.split('&')[11]
      request_json = json.loads(request_str[7:])
      if request_json["battleResult"] == 3 :
        setting = readSetting(flow.request.url)
        if setting["battleCancel"] :
          request_json["battleResult"] = 1
          request_json["elapsedTurn"] = 11
          request_json["aliveUniqueIds"] = []
          requset_bytes = bytes(json.dumps(request_json), encoding='utf-8')
          flow.request.content = requset_bytes

def response(flow: http.HTTPFlow) -> None :
  if flow.request.url.find("ac.php") > -1 :
    query_key = flow.request.urlencoded_form['key']
    if query_key == "battlesetup" or query_key == "battleresume" :
      #decode
      body_bytes = flow.response.content
      body_str = urllib.parse.unquote(body_bytes)
      base64_decrypt = base64.b64decode(body_str)
      json_data = json.loads(base64_decrypt)
      #print(json_data["sign"])
      #modify
      options = readSetting(flow.request.url)
      json_data["sign"]=""
      options = readSetting(flow.request.url)
      uHp = options["uHp"]
      uAtk = options["uAtk"]
      limitCountSwitch = options["limitCountSwitch"]
      skillLv = options["skillLv"]
      tdLv = options["tdLv"]
      enemyActNumSwitch = options["enemyActNumSwitch"]
      enemyActNumTo = options["enemyActNumTo"]
      enemyChargeTurnSwitch = options["enemyChargeTurnSwitch"]
      enemyChargeTurnto = options["enemyChargeTurnto"]
      replaceSvtSwitch = options["replaceSvtSwitch"]
      replaceSvtSpinner = options["replaceSvtSpinner"]
      replaceSvt1 = options["replaceSvt1"]
      replaceSvt2 = options["replaceSvt2"]
      replaceSvt3 = options["replaceSvt3"]
      replaceSvt4 = options["replaceSvt4"]
      replaceSvt5 = options["replaceSvt5"]
      replaceSvt6 = options["replaceSvt6"]
      replaceCraftSwitch = options["replaceCraftSwitch"]
      replaceCraftSpinner = options["replaceCraftSpinner"]

      if json_data['response']['resCode'] == 00 :
          svts = json_data['cache']['replaced']['battle'][0]['battleInfo']['userSvt']
          for sv in svts :
            # ----------------------------------------
            # enemy
            if isUndefined(sv['hpGaugeType']) :
              # replace enemy act num
              if enemyActNumSwitch :
                sv['maxActNum'] = enemyActNumTo
              # replace enemy charge turn
              if enemyChargeTurnSwitch :
                sv['chargeTurn'] = enemyChargeTurnto
              continue
            # ----------------------------------------

            # ----------------------------------------
            # svt
            if isUndefined(sv['status']) and isUndefined(sv['userId']) and sv['userId'] != '0' and sv['userId'] != 0 :
              if isinstance(sv['hp'], int) :
                sv['hp'] = int(sv['hp'])*uHp
              else :
                sv['hp'] = str(int(sv['hp'])*uHp)
              if isinstance(sv['atk'], int) :
                sv['atk'] = int(sv['atk'])*uAtk
              else :
                sv['atk'] = str(int(sv['atk'])*uAtk)

              # replace skill level
              if (skillLv) :
                sv['skillLv1'] = 10
                sv['skillLv2'] = 10
                sv['skillLv3'] = 10

              # replace treasure device level
              if tdLv :
                sv["treasureDeviceLv"] = 5

              # replace limit count
              if limitCountSwitch :
                sv['limitCount'] = 4
                sv['dispLimitCount'] = 4
                sv['commandCardLimitCount'] = 3
                sv['iconLimitCount'] = 4

              # replace svt
              if replaceSvtSwitch :
                if replaceSvtSpinner != 0 :
                  replaceSvt(sv, replaceSvtSpinner)
                if replaceSvt1 and sv['svtId'] == "600200" : replaceSvt(sv, 0)
                if replaceSvt2 and sv['svtId'] == "600100" : replaceSvt(sv, 1)
                if replaceSvt3 and sv['svtId'] == "601400" : replaceSvt(sv, 2)
                if replaceSvt4 and sv['svtId'] == "700900" : replaceSvt(sv, 3)
                if replaceSvt5 and sv['svtId'] == "700500" : replaceSvt(sv, 4)
                if replaceSvt6 and sv['svtId'] == "701500" :
                  replaceSvt(sv, 5)
                  sv["treasureDeviceLv"] = 1
                continue
            # ----------------------------------------

            # ----------------------------------------
            # carft            
            if replaceCraftSwitch and isUndefined(sv["parentSvtId"]) :
              carftMap = [990068,990645,990066,990062,990131,990095,990113,990064,990333,990629,990327,990306]
              sv["skillId1"] = carftMap[replaceCraftSpinner-1]
            # ----------------------------------------
      #encode
      body_str = bytes(json.dumps(json_data), encoding='utf-8')
      base64_encrypt = str(base64.b64encode(body_str), encoding='utf-8')
      body_str = urllib.parse.quote(base64_encrypt)
      body_bytes = bytes(body_str, encoding='utf-8')
      #print(body_bytes)
      flow.response.content = body_bytes