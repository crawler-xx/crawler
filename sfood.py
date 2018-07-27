from pyquery import PyQuery as pq
import sqlite3
import requests

DB_NAME = "food.db"
DROP_TABLE_FOODS = '''DROP TABLE IF EXISTS "foods";'''
CREATE_TABLE_FOODS = '''
	CREATE TABLE "foods" (
	    "name" TEXT NOT NULL,
        "yyjson" TEXT NOT NULL,
        "dljson" TEXT NOT NULL,
        "pj" TEXT NOT NULL,
        "pic" TEXT NOT NULL,
        "dj" TEXT NOT NULL,
        "url" TEXT NOT NULL
);
'''
INSERT_TABLE_FOODS = '''
	insert into foods ("name", "yyjson","dljson", "pj",  "pic", "dj","url") 
	values (?, ?,?, ?,?,?, ?);
'''
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}
POOL_PROXY_URL = 'http://192.168.9.135:5510/get/'
proxy = None

def _main():
    
    cursor.execute(DROP_TABLE_FOODS)
    cursor.execute(CREATE_TABLE_FOODS)

    for fpage in xrange(1,11):
        for page in xrange(1,11):
            urls = "http://www.boohee.com/food/group/{fp}?page={p}".format(fp=fpage,p=page)
            try:
                delgroupurl(urls)
            except Exception as e:
                print(e)
                pass
            

    conn.close()


glourl={}

def delgroupurl(urls):
    if urls not in glourl:
        glourl[urls] = 1
        htmlcontent = get_index_html(urls)
        doc = pq(htmlcontent)
        objli = doc('.food-list')
        lis = objli('li')
        for li in lis.items():
            try:
                delurl(li('a').attr.href)
            except Exception as e:
                print(e)
            else:
                pass
            finally:
                pass
   


def delurl(url):
    durl = 'http://www.boohee.com{url}'.format(url=url)  ### url
    if durl not in glourl:
        glourl[durl] = 1
        # print(durl)
        htmlcontent = get_index_html(durl)
        docpre = pq(htmlcontent)
        doc = docpre('div.widget-group-content')
        # print(doc)

        try:
            # 1. 获取相关食物 进行递归
            relative = doc("div.widget-relative")
            lis = relative('li')
            for li in lis.items():
                minurl = li('a').attr.href
                #print(minurl)
                suburl = 'http://www.boohee.com{url}'.format(url=minurl)
                #print(suburl)
                if suburl not in glourl:
                    delurl(minurl)
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass
        
        try:
            # 1. 原料 同样进行递归  
            more = doc("div.widget-more")
            lis = more('li')
            for li in lis.items():
                minurl = li('a').attr.href
                #print(minurl)
                suburl = 'http://www.boohee.com{url}'.format(url=minurl)
                #print(suburl)
                if suburl not in glourl:
                    delurl(minurl)
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass

        data = []
        name = ""
        pj = ""
        yyjson = ""
        try:
            nitem = doc('h2').text()
            arr = nitem.split('/')
            name = arr[len(arr)-1]   #####  name
            #print(name)

        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass

        try:
            # 2. 解析详情
            # 2.1 评价
            content = getFirst(doc('div.content')('p'))
            #print(url)
            pj = content.html()      #####  pj
            #print(pj)
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass
        
        yyjson = "["                   #### yyjson
        dljsondef = ""
        try:
            ## 2.2 营养
            nutrtag = doc('div.nutr-tag')
            dls = nutrtag('dl').not_('.header')
            for dl in dls.items():
                dd = dl('dd')
                for d in dd.items():
                    dtitle = d('.dt').text()
                    dvalue = d('.dd').text()
                    yyjson = yyjson+'{"'+dtitle+'":"'+dvalue+'"},'
                    #print(yyjson)

                    if len(dljsondef)==0:
                        dljsondef = '[{"标准(100克)":"'+dvalue+'大卡"}]'
                        pass
                    pass
                pass
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass
        if yyjson.endswith(","):
            yyjson = yyjson[0:len(yyjson)-1]
            pass
        yyjson = yyjson+"]"

        dljson = "["   ### 度量
        try:
            ## 3 度量单位
            nutrtag = doc('div.widget-unit')
            trs = nutrtag('tbody')('tr')
            for tr in trs.items():
                td = tr('td')
                dljson = dljson +"{"
                for d in td.items():
                    dva = d.text()
                    dljson = dljson+'"'+dva+'":'
                    pass
                if dljson.endswith(":"):
                    dljson = dljson[0:len(dljson)-1]
                    pass
                dljson = dljson +"},"
                pass
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass
        if dljson.endswith(","):
            dljson = dljson[0:len(dljson)-1]
            pass
        dljson = dljson+"]"
        
        if dljson == '[]':
            dljson = dljsondef
            pass

        pic = ""
        try:
            ## 4 图片 pic
            picdoc = doc('div.food-pic')
            imgs = picdoc('img')
            pic = imgs.attr.src
           # print(pic)
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass

        dj = ""
        try:
            ## 5 等级  dj
            djdoc = doc('ul.basic-infor')
            djimg = djdoc('img')
            dj = djimg.attr.src
            #print(dj)
        except Exception as e:
            print(e)
        else:
            pass
        finally:
            pass

        data = []
        name = name.strip()
        yyjson = yyjson.strip()
        pj = pj.strip()
        durl = durl.strip()

        if pic == None:
            pic=""
            pass
        if dj == None:
            dj = ""
            pass
        data.append((name, yyjson,dljson, pj,pic,dj, durl))
        cursor.executemany(INSERT_TABLE_FOODS, data)
        conn.commit()

def getFirst(doc):
    for d in doc.items():
        return d

def xrange(idx, x):
    n = idx
    while n < x:
        yield n
        n += 1


def get_index_html(url):
    print('正在爬取', url)
    global proxy
    try:
        if proxy:
            print('正在使用代理', proxy)
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(
                url, headers=headers, allow_redirects=False, proxies=proxies)
        else:
            response = requests.get(
                url, headers=headers, allow_redirects=False)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # Need proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                return get_index_html(url)
            else:
                print('请求代理失败')
                return None

    except Exception:
        proxy = get_proxy()
        return get_index_html(url)

def get_proxy():
    print('正在请求代理')
    try:
        response = requests.get(POOL_PROXY_URL)
        if response.status_code == 200:
            return response.text
        else:
            print('请求代理失败')
            return None
    except Exception:
        return None

if __name__ == "__main__":
	_main()

