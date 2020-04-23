from lxml import html
import requests
import pytesseract
from PIL import Image
from io import BytesIO
import json
import bs4
from datetime import datetime

URL = "http://tracuuhoadon.gdt.gov.vn/"
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

#xu li anh
def imgCaptcha(path):
    capt_byte = BytesIO(path)
    capt_img = Image.open(capt_byte)
    return pytesseract.image_to_string(capt_img)

# Ham xu li ma captcha
def convert_captcha(req):
    page = req.get(URL +"tbphtc.html")
    page = html.fromstring(page.content.decode('utf-8'))


    captcha = ""

    while True:
        capt = req.get(URL+ "Captcha.jpg").content
        captcha =imgCaptcha(capt)

        url =  URL + "validcode.html"
        data = {
            "captchaCode":captcha
        }
        vald = req.post(url=url,data=data)

        if "Sai" not in vald.text:
            return captcha
    return




#get data each taxcode
def getInfEach(req,tax,captcha):
    test1 = req.post(URL+"gettin.html?tin={tax}&captchaCode={captcha}".format(tax=tax,captcha=captcha)).content.decode('utf-8')

    test1 = json.loads(test1)

    return test1

def getDataEach(req,tax,token,page,captcha,timestamp):

    data = req.get(URL + "searchtbph.html?search=false&nd={timestamp}&rows=20&page={page}&sidx=&sord=asc&kind=tc&tin={taxcode}&ngayTu=01%2F02%2F2010&ngayDen=10%2F10%2F2020&captchaCode={captcha}&token={token}"
                "&struts.token.name=token&_={timestamp}".format(taxcode=tax, captcha=captcha, token=token, timestamp=timestamp,page=page)).content.decode('utf-8')
    data = json.loads(data)
    list_id = [data["total"]]
    #print(len(data["list"]))
    for row in data["list"]:
        list_id.append(row['id'])
    return list_id

def getToken(req):
    s = req.get(URL+"tbphtc.html")
    soup = bs4.BeautifulSoup(s.text, 'html.parser')
    inputTag = soup.findAll(attrs={"name": "token"})

    return inputTag[0]['value']

#Lay thong tin tung hang trong bang

def getTableRow(req,id,time,mst):
    abc =  req.get(URL+"viewtbph.html?id={id}&ltd=0&dtnt_tin={mst}&loaitb_phanh=01".format(id=id , mst=mst))
    data = req.get(URL+"gettbphdtl.html?id={id}&ltd=0&search=false&nd={time}&rows=1000&page=1&sidx=&sord=asc&={time}".format(id=id,time=time)).content.decode('utf-8')
    data = json.loads(data)
    res =  []
    for x in data['dtls']:
        infor_row = {
            "tendonviphathanh": x['nin_ten'],
            "kyhieuhoadon": x['kyhieu'],
            "soluong": x['soluong'],
            "masothue": x['nin_tin'],
        }
        res.append(infor_row)
    return res

#Ham lay thong tu website voi input list taxcode
def getInfor(req,tax,captcha):
    token = getToken(req)
    #print(captcha)
    #print(token)

    res = []
    res.append(getInfEach(req,tax,captcha))
    now = datetime.now()
    timestamp = int(datetime.timestamp(now))

    # lay thong tin bang hoa don cua cong ty
    # info_order = req.get(URL +"searchtbph.html?search=false&nd={timestamp}&rows=10&page=1&sidx=&sord=asc&kind=tc&tin={taxcode}&ngayTu=01%2F01%2F2010&ngayDen=01%2F04%2F2020&captchaCode={captcha}&token={token}&struts.token.name=token&={timestamp}".format(taxcode=tax,captcha=captcha, token=token,timestamp=timestamp))
    info_order = getDataEach(req,tax,token,"1",captcha,timestamp)

    # Tong so trang cua 1 request
    total = (int)(info_order[0]) + 1
    print(total)


    del info_order[0]

    for z in info_order:
        print(getTableRow(req,z,timestamp,tax))




    for x in range(2,total):
        new_token = req.get(URL + "getnewtoken.html?token={token}&struts.token.name=token&={timestamp}".format(token=token,timestamp=timestamp))
        new_token = json.loads(new_token.text)
        token = new_token["newToken"]
        info_order = getDataEach(req, tax, token, x , captcha, timestamp)
        del info_order[0]
        for k in info_order:
            print(getTableRow(req,k,timestamp,tax))




    return res


req = requests.Session()
captcha = convert_captcha(req)

a=["0101243150"]
for x in a:
    a=(getInfor(req,x,captcha))
    for y in a:
        print (y)