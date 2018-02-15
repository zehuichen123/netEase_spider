# 网易云用户爬虫

## 简介

本爬虫不利用任何框架（因为不会😂）通过使用网易云提供的api进行爬取网易云音乐用户的uid，等级，性别，昵称和听歌量，并放入本地的mysql中进行保存，同时支持爬取成功和爬取中断的邮件提醒。  

## 使用说明

- 只需要下载netEase.py和temp.py  
- 登陆上你的mysql,在终端输入:   
```
mysql -uroot -p(here is your password)
```
进入mysql后输入如下命令新建数据库netEase:  
```
CREATE DATABASE netEase;
```
- 运行temp.py前请修改如下几处：
	- line6: mysql本地账号密码
- cd到temp.py目录下运行`./temp.py`(可能需要先`chmod +x temp.py`一下)  
- 运行netEase.py前请修改如下几处：  
	- line24-26: 邮件的发送者和接收者
	- line28: mysql本地账号密码  
	- line172: 初始爬取账号(uid) 
	- line56,137: 爬取用户数目(当前值为20)  
- 接着在netEase.py下输入`./netEase.py`即可运行爬虫  

## 运行结果  

**命令行实时显示**  
<img src="https://view.moezx.cc/images/2018/02/14/1.png">

**mysql数据库**
<img src="https://view.moezx.cc/images/2018/02/14/2.png">

**邮件通知**
<img src="https://view.moezx.cc/images/2018/02/14/3.png">

## to-do list

1. 增加爬取的信息，比如following，follower，听歌排行以及音乐评论
2. 增加多线程以加快爬取速度
3. 增加注释  
4. 增加实现说明  
5. 爬取用户分析表