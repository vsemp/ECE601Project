#阿里云ECS操作文档
###基础知识
本文档主要描述如何使用api接口来操作阿里云弹性计算服务(ECS)。操作之前，假设你对ECS的基本概念已经有一定了解，如果没有的话，建议花几分钟阅读一下阿里云[官方文档](https://help.aliyun.com/document_detail/25484.html?spm=5176.doc25502.6.231.8XlGQo)

###基本流程

如果仅仅是开通一个可用的阿里云服务器，需要的步骤不多，简介如下：

1. 需要提供阿里云ECS的**access_key**和**access\_key\_secret**，access_key用于每次api请求时候标明请求者身份，access\_key\_secret用作加密秘钥。(向运维申请这两个key)
2. 基本流程于相关api：CreateInstance->(AllocatePublicIpAddress)->StartInstance.当然如果中间某个步骤操作失误，也不要紧，可以通过其他操作来补救。
3. 需要重点说明的是，在CreateInstance的时候一定不要忘记设置password，不然没法在后续登陆机器。(当然，万一忘了设置，也可以通过ModifyInstanceAttribute来重新设置)。

###常见操作的API参数
下面是常见操作的参数，仅供参考，更多内容请参见阿里云官方文档。


```
		#创建
		create_params = {
		                        'Action': 'CreateInstance',
		                        'RegionId': 'cn-hangzhou',
		                        "ImageId": "ubuntu1404_64_20G_aliaegis_20150325.vhd",#找一个可用的镜像
		                        'InstanceType': 'ecs.t1.small',
		                        'SecurityGroupId': 'G1471546637380890',
		                        'InstanceName': 'data-new-crawler10',
		                        'Description': 'anti-toutiao block ip',
		                        'InternetChargeType': 'PayByTraffic',
		                        'InternetMaxBandwidthOut': '5',
		                        'Password': 'CooTek-bigdata',#必须设置，否则创建后没法登录
        }
        #查询
		 query_params = {
            'Action': 'DescribeInstanceStatus',
            'RegionId': 'cn-hangzhou',
        }
		 #查询详细状态
        query_all_params = {
            'Action': 'DescribeInstances',
            'RegionId': 'cn-hangzhou',
        }
        
		 #修改参数
        modify_params = {
            'Action': 'ModifyInstanceAttribute',
            'InstanceId': 'i-bp16w4fwm1sxsgws5m40',
            'Password': 'CooTek-bigdata'
        }
		
```

###调用方式

```
#下面是调用的一个实例，在其他类或者函数中调用原理同下
#!/usr/bin/env python
#coding: utf-8
if __name__ == '__main__':
    access_key_id = '***'
    access_key_secret = '***' 
    ali = AliECS(access_key_id, access_key_secret)
    query_params = {
            'Action': 'DescribeInstanceStatus',
            'RegionId': 'cn-hangzhou',
        }
    result = ali.make_request(query_params)
```