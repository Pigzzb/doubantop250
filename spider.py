# -*- codeing = utf-8 -*-
# @Time: 2020/6/19 21:05
# @Author: coderzb
# @File: spider.py
# @Software: PyCharm


from bs4 import BeautifulSoup     # 网页解析，获取数据
import xlwt   # 进行 excel 操作
import re   # 正则表达式，进行文字匹配
import sqlite3  # 进行 sqlite 数据库操作
import urllib.request, urllib.error   # 指定 url，获取网页数据
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 影片详情链接
findLink = re.compile(r'<a href="(.*?)">')   # 创建正则表达式对象，表示规则（字符串的模式）
# 影片图片链接
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)
# 影片的名字
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片的评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 影片评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 影片概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 影片的相关信息
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


def main():
  baseURL = "https://movie.douban.com/top250?start="
  # 1.爬取网页获取数据
  dataList = getData(baseURL)

  # 3.保存数据
  savePath = "豆瓣Top250.xls"
  saveData(dataList, savePath)



# 根据url 爬取网页 获取数据
def getData(baseURL):
  dataList = []
  for i in range(0, 10):   # 调用 10 次，发出 10 次请求
    url = baseURL + str(i * 25)
    html = askURL(url)   # 保存每次获取到的网页源码
    # 2.逐一解析数据
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.find_all('div', class_="item"):   # 查找符合要求的字符串，形成列表
      # print(item)   # 测试 电影 item 全部信息
      data = []   # 保存一部电影的所有信息
      item = str(item)

      link = re.findall(findLink, item)[0]   # re 通过 正则表达式查找指定的字符串
      data.append(link)     # 添加详情链接

      imgSrc = re.findall(findImgSrc, item)[0]
      data.append(imgSrc)   # 添加图片

      titles = re.findall(findTitle, item)  # 片名可能有中文，可能有外文
      if(len(titles) == 2):
        cTitle = titles[0]   # 添加中文名
        data.append(cTitle)
        oTitle = titles[1].replace("/", "")
        oTitle = oTitle.replace("\xa0", "")
        data.append(oTitle)  # 添加外文名
      else:
        data.append(titles[0])
        data.append(" ")  # 没有外文名留空

      rating = re.findall(findRating, item)[0]
      data.append(rating)   # 添加评分

      judgeNum = re.findall(findJudge, item)[0]
      data.append(judgeNum)  # 添加评价人数

      inq = re.findall(findInq, item)
      if len(inq) != 0:
        inq = inq[0].replace("。", "") # 去掉句号
        data.append(inq)   # 添加一句话概述
      else:
        data.append(" ")    # 没有概述，留空

      bd = re.findall(findBd, item)[0]
      bd = re.sub('<br(\s+)?/>(\s+)?', " ", bd)  # 去掉 br
      bd = re.sub('/', " ", bd)   # 替换 /
      bd = bd.replace("\xa0", "")
      data.append(bd.strip())   # 去掉前后的空格

      dataList.append(data)   # 把处理好的一部电影信息放入 dataList

  return dataList


# 得到指定 url 的 网页内容
def askURL(url):
  # 用户代理，告诉豆瓣服务器，咱们是正儿八经的浏览器，可以接受正常的网页数据
  head = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"
  }

  req = urllib.request.Request(headers=head, url=url)
  html = ""
  try:
    res = urllib.request.urlopen(req)
    html = res.read().decode('utf-8')
  except urllib.error.URLError as e:
    if hasattr(e, "code"):
      print("发生了一些错误...", e.code)
    if hasattr(e, "reason"):
      print("原因：", e.reason)

  return html


# 保存数据
def saveData(dataList, savePath):
  print("Saving data......")
  workBook = xlwt.Workbook(encoding='utf-8')  # 创建 workBook 对象
  workSheet = workBook.add_sheet('豆瓣Top250', cell_overwrite_ok=True)  # 创建工作表
  col = ('详情链接', '电影封面','中文名','外文名','评分','评价人数','概况','相关信息')
  for i in range(0, 8):
    workSheet.write(0, i, col[i])   # 写入列名

  for i in range(0, 250):
    print("正在写入第%d条。。。" % (i+1))
    data = dataList[i]
    for j in range(0, 8):
      workSheet.write(i+1, j, data[j])  # 数据写入

  workBook.save(savePath)    # 保存
  print("保存完毕！")

if __name__ == '__main__':
    main()  # 调用函数
