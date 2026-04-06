# 通用机场签到
基于Python的playwright方案实现的自动化签到，目前测试了一个`Powered by SSPANEL`机场。

## 功能
每日凌晨6点执行定时签到（程序会自动添加随机延时），获取额外的流量奖励。

## 推送方式
采用<a href = 'https://sct.ftqq.com/'>Server酱</a>的推送方式。如果不需要推送，action的仓库密钥SENDKEY参数的值留空或者不创建密钥变量就行。

## 部署过程
1. 右上角Fork此仓库
2. 然后到`Settings`->`Secrets and variables`->`Actions`->`Repository secrets`，新建以下环境变量：
3. 到`Actions`中创建一个workflow，运行一次，以后每天项目都会自动运行。

| 参数   | 是否必须  | 内容  |
| ------------ | ------------ | ------------ |
| URL | 是  | 机场网站的URL地址 <br> 例如`https://example.com`，尾部不要加`/`  |
| CONFIG | 是  | 账号密码，支持同网站下多账号<br>一行帐号一行密码  |
| SENDKEY  | 否  | Server酱秘钥  |

## 查看签到结果
可以到action执行结果中的Run checkin查看签到情况，同时结果也会通过Server酱推送。
