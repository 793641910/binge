import sys
sys.path.append("..")
import re
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import json
from base.spider import Spider
from urllib.parse import quote


class Spider(Spider):

    def getName(self):
        return "九龙趣看"

    def init(self, extend=""):
        self.host = self.host()
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def action(self, action):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):

        data = self.fetch(f"{self.host}/api/v3/drama/getCategory?orderBy=type_id", headers=self.headers).json()


        dy = {
            "class": "类型",
            "area": "地区",
            "lang": "语言",
            "year": "年份",
            "letter": "字母",
            "by": "排序",
            "sort": "排序"
        }


        result = {"class": [], "filters": {}}


        for item in data["data"]:

            jsontype_extend = json.loads(item["converUrl"])


            result["class"].append({"type_name": item["name"], "type_id": str(item["id"])})


            if any(key in jsontype_extend and jsontype_extend[key].strip() for key in dy):
                result["filters"][str(item["id"])] = []
                for dkey in dy:
                    if dkey in jsontype_extend and jsontype_extend[dkey].strip():
                        values = [value.strip() for value in jsontype_extend[dkey].split(",") if value.strip()]
                        result["filters"][str(item["id"])].append({
                            "key": dkey,
                            "name": dy[dkey],
                            "value": [{"n": v, "v": v} for v in values]
                        })


        return result

    def categoryContent(self, tid, pg, filter, extend):
        params = []
        if extend.get('area'):
            params.append(f"vodArea={extend['area']}")
        if extend.get('classs'):
            params.append(f"vodClass={extend['class']}")
        params.append("pagesize=20")
        params.append(f"typeId1={tid}")
        params.append(f"page={pg}")
        if extend.get('year'):
            params.append(f"vodYear={extend['year']}")
        body = '&'.join(params)
        path = self.aes(self.aes(body, self.key[1], 'encrypt'), self.key[0], 'encrypt', True)
        data = self.fetch(f"{self.host}/api/ex/v3/security/drama/list?query={path}", headers=self.headers).json()[
            "data"]
        data = self.aes(self.aes(data, self.key[0]), self.key[1], 'decrypt', True)['list']
        list = []
        for item in data:
            list.append({
                'vod_id': item.get("id"),
                'vod_pic': item["coverImage"].get("path"),
                'vod_name': item.get("name"),
                'vod_year': item.get("year"),
                'vod_remarks': item.get("remark")
            })
        result = {}
        result["list"] = list
        result["page"] = pg
        result["pagecount"] = 9999
        result["limit"] = 90
        result["total"] = 999999
        return result

    def detailContent(self, ids):
        url = f"{self.host}/api/v3/drama/getDetail?id={ids[0]}"
        data = self.fetch(url, headers=self.headers).json()["data"]
        vod = {
            'vod_name': data.get("name"),
            'vod_area': data.get("area"),
            'type_name': data.get("clazz"),
            'vod_actor': data.get("actor"),
            'vod_director': data.get("director"),
            'vod_content': data.get("brief").strip(),
        }
        play = []
        names = []
        plays = {}
        for itt in data["videos"]:
            if itt["sourceCn"] not in names:
                plays[itt["source"]] = []
                names.append(itt["sourceCn"])
            url = f"vodPlayFrom={itt['source']}&playUrl={itt['path']}"
            if re.search(r"\.(mp4|m3u8|flv)$", itt["path"]):
                url = itt["path"]
            plays[itt["source"]].append(f"{itt['titleOld']}${url}")
        for it in plays:
            play.append("#".join(plays[it]))
        vod["vod_play_from"] = "$$$".join(names)
        vod["vod_play_url"] = "$$$".join(play)
        result = {"list": [vod]}
        return result

    def searchContent(self, key, quick, pg=1):
        body = f"pagesize=20&page={pg}&searchKeys={key}"
        path = self.aes(self.aes(body, self.key[1], 'encrypt'), self.key[0], 'encrypt', True)
        data = self.fetch(f"{self.host}/api/ex/v3/security/drama/list?query={path}", headers=self.headers).json()[
            "data"]
        data = self.aes(self.aes(data, self.key[0]), self.key[1], 'decrypt', True)['list']
        list = []
        for item in data:
            list.append({
                'vod_id': item.get("id"),
                'vod_pic': item["coverImage"].get("path"),
                'vod_name': item.get("name"),
                'vod_year': item.get("year"),
                'vod_remarks': item.get("remark")
            })
        result = {"list": list, "page": pg}
        return result

    def playerContent(self, flag, id, vipFlags):
        url = id
        if "vodPlayFrom" in url:
            try:
                path = self.aes(self.aes(id, self.key[1], 'encrypt'), self.key[0], 'encrypt', True)
                data = self.fetch(f"{self.host}/api/ex/v3/security/videoUsableUrl?query={path}", headers=self.headers).json()[
                    "data"]
                url = self.aes(self.aes(data, self.key[0]), self.key[1], 'decrypt', True)['playUrl']
                # try:
                #     url1 = self.fetch(url, headers=self.headers, timeout=5, allow_redirects=False).headers['Location']
                #     if "http" in url1 and url1:
                #         url = url1
                # except:
                #     pass
            except Exception as e:
                pass
        if '.jpg' in url or '.jpeg' in url or '.png' in url:
            url = self.getProxyUrl() + "&url=" + b64encode(url.encode('utf-8')).decode('utf-8') + "&type=m3u8"
        result = {}
        result["parse"] = 0
        result["url"] = url
        result["header"] = {'User-Agent': 'okhttp/3.12.1'}
        return result

    def localProxy(self, param):
        url = b64decode(param["url"]).decode('utf-8')
        durl = url[:url.rfind('/')]
        data = self.fetch(url, headers=self.headers).content.decode("utf-8")
        lines = data.strip().split('\n')
        for index, string in enumerate(lines):
            if '#EXT' not in string and 'http' not in string:
                lines[index] = durl + ('' if string.startswith('/') else '/') + string
        data = '\n'.join(lines)
        return [200, "application/vnd.apple.mpegur", data]

    def host(self):
        return "http://110.42.49.188:9902"

    headers = {
        'User-Agent': 'okhttp/3.12.1',
        'Content-Type': 'application/json;'
    }
    key = ['ALHMZJVVOFVNQ2HTOEPFZZFXYWH1D2RN', '2C1A06E197EF10CF3F6058CA7A803B5E']

    def aes(self, word, key, mode='decrypt', bool=False):
        key = key.encode('utf-8')
        if mode == 'decrypt':
            word = b64decode(word)
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(word)
            word = unpad(decrypted, AES.block_size).decode('utf-8')
            if bool:
                word = json.loads(word)
        elif mode == 'encrypt':
            cipher = AES.new(key, AES.MODE_ECB)
            padded = pad(word.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded)
            word = b64encode(encrypted).decode('utf-8')
            if bool:
                word = quote(word)
        return word
