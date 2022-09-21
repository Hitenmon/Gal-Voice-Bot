import requests

def Translate(content):
    try:
        if(content=='最喜欢哥哥了'):
            return 'お兄ちゃん大好き'
        url = 'http://fanyi.youdao.com/translate'
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
        data = {}
        data['i'] = content
        data['type'] = 'AUTO'
        data['smartresult'] = 'dict'
        data['client'] = 'fanyideskweb'
        data['doctype'] = 'json'
        data['keyfrom'] = 'fanyi.web'
        data['action'] = 'FY_BY_REALTIME'

        response = requests.post(url,headers=headers,data=data)
        # print(data)
        dictTrans = response.json()
        langs = dictTrans['type'].split('2')
        if(langs[0]!='ZH_CN'):
            return content
        data['type'] = 'ZH_CN2JA'
        response = requests.post(url,headers=headers,data=data)
        dictTrans = response.json()
        print('翻译中：{}'.format(dictTrans))
        return dictTrans['translateResult'][0][0]['tgt']
    except:
        return content

# if __name__=='__main__':
#     print(Translate('お兄ちゃん大好き'))