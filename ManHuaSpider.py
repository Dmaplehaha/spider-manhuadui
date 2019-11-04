#开始时间：2019年10月22日 16:07:40
#结束时间：2019年10月28日 08:47:33
#作者：DMaple
#功能：爬取漫画堆漫画-鬼灭之刃
#版本1.0
#
'''

断断续续写了一周,
涉及功能：
request 获取网页代码
json & execjs   python调用js代码
os 文件的读写
re 正则表达式的应用

'''

import requests
import json
import time
import os
import re
import execjs


host='https://mhcdn.manhuazj.com/'
l_url = "https://www.manhuadui.com"
url = "https://www.manhuadui.com/manhua/guimiezhiren/"
headers = {  # 模拟浏览器访问网页
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
response = requests.get(url=url, headers=headers)

def main():
    #获取章节地址
    list_source = dir()
    get_chapters(list_source)


'''
功能：查找所有章节网址
返回值：字符串：包含每个章节的url以及章节名称
'''
def dir():
    #正则，匹配章节url以及章节名称
    pattern = re.compile('href=\"\/manhua\/.+\.html.+title=.+\"')
    print("dir 正则过滤-----------------------------")
    print("正在查找该漫画所有章节的url以及名称")
    list_source=pattern.findall(response.text)
    #print(list_source)
    return list_source


'''
功能：获得章节的url以及名称
心得：正则表达式的写法以及python正则表达式的使用
'''
def get_chapters(list_source):
    #遍历所有章节的url
    i=0
    for chapter in list_source:
        if(i<170):
            i+=1
            continue

        #print(chapter)
        r_url = re.search('\/manhua\/.+\.html', chapter).group()
        # 章节url
        chapter_url = l_url + r_url
        print(chapter_url)
        chapter_name = re.search('title=\".+\" ', chapter).group()
        chapter_name = chapter_name[7:-2]
        print(chapter_name)

        #获取具体章节网页的静态代码
        res = requests.get(chapter_url, headers)

        chapter_image_list = get_js_chapterImage(res)
        chapter_path = get_chapter_Path(res)

        print("down_url:")
        chapter_root='gmzr//'+chapter_name
        count=1
        for chapter_image in chapter_image_list:
            if (chapter_path == -1):
                down_url = chapter_image
                download_image(down_url,chapter_root,'',count)
            else:
                down_url = host+chapter_path+chapter_image
                print(down_url)
                download_image(down_url,chapter_root,chapter_image,count)
            count+=1

        # 降低服务器压力，每爬取一个章节的所有图片，延时10秒
        # 每爬取5个章节，再延时20秒
        print('延时20秒')
        time.sleep(20)
        i += 1
        if (i % 5 == 0):
            print('延时60秒')
            time.sleep(20)
#这里从网页的script标签里，找数据,chapterImage被后台加密，放到script标签里
'''
参数：章节url
ex:https://www.manhuadui.com/manhua/guimiezhiren/410940.html
返回值：章节所有图片的名称 [***.jpg]
返回值类型：list
'''
def get_js_chapterImage(res):

    #print(res.text)
    #正则过滤数据
    chapter_image_code = re.search('chapterImages = \".+\";var chapterPath', res.text).group()
    chapter_image_code = re.search('\".+\"', chapter_image_code).group()
    print("chapter_image_code")
    print(chapter_image_code)
    chapter_image_code = chapter_image_code[1:-1]

    #解密章节图片乱码，还原成*.jpg格式
    chapter_Image_list = get_decryptImages(chapter_image_code)
    print("正在查询当前章节的所有图片")
    print("chapter_Image_list:")
    print(chapter_Image_list)

    return chapter_Image_list

#鬼灭之刃从130话开始，网页获取的格式换了，如：
#https://mhcdn.manhuazj.com/ManHuaKu/g/guimiezhiren/132/201915413.jpg
#解析之后直接就变成了完整的url，所以需要修改
#如果chapter_path有问题，那么返回-1 执行其他代码
def get_chapter_Path(res):
    try:
        chapter_path = re.search('chapterPath = \".+\";var chapterP', res.text).group()
        chapter_path = re.search('\".+\"', chapter_path).group()
        chapter_path = chapter_path[1:-1]
        print(chapter_path)
        return chapter_path
    except:
        return -1
        #return chapter_path


def get_js():
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    f = open("decrypt20180904.js", 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    #print(htmlstr)
    return htmlstr

#解密
def get_decryptImages(chapterImages):
    #获取解密js，进行解密
    js_str = get_js()
    ctx = execjs.compile(js_str)
    print(chapterImages)
    images =  ctx.call('decrypt20180904',chapterImages)

    #过滤数据：把字符串两边的符号["........."]过滤，以中间符号","进行切分
    images_list=str(images)[2:-2].split('","')

    return images_list





#下载图片
def download_image(url,chapter_root,image_name,count):
    root = 'D://ManHua//TEST//'  #给个目录
    root = root+chapter_root+'//'
    #URL = https://mhcdn.manhuazj.com//ManHuaKu//g//guimiezhiren//136//201915493.jpg
    #url = 'https://mhcdn.manhuazj.com/images/comic/5/8412/1551394269327841209ad0db6d.jpg'
    url = url.replace('\\','')
    path = root + str(count)+'页.jpg'
    print("url:")
    print(url)
    print(path)
    try:
        if not os.path.exists(root):
            os.mkdir(root)
            # 判断根目录是否存在，os.madir()创建根目录
        if not os.path.exists(path):

            r = requests.get(url)
            # 判断文件是否存在，不存在将从get函数获取
            with open(path, 'wb')as f:
                # wb存为二进制文件
                f.write(r.content)
                # 将返回内容写入文件 r.content返回二进制形式

                f.close()
                print('文件保存成功')
        else:
            print('文件已经存在')
    except:
        print('爬取失败')


if __name__ == '__main__':
    main()

