# dbgate
The layer that between hadoop sqoop and mysql servers which used ip filter policy.

# Situation 1
In one department, that uses hadoop sqoop to import or output data to mysql, and the mysql servers use IP source filter policy. 

Just watch the situation above that does't matter, but 

if we want to scale out the hadoop cluster > we should add the all the new IPs with the server that use. 
  if we have 100 mysql dbs, how long will we get this thing done!

if we want to add new mysql, we should add all the hadoop cluster IP with the mysql ip source filter policy.

The dbgate is a method, that we have two servers that running haproxy, proxy the backend mysql db servers, open ip source filter policy that for the hadoop cluster.

# dbgate-中国

## 架构简介

为什么会产生这个系统？

```

业务在使用hadoop的时候，经常会有抽数这么一说，也就是所谓的利用集群sqoop技术，或者入口机等从外部的mysql或者mongodb里面提取数据到集群，然后做计算。 在XeEco， DBA的安全策略十分严格，除了账号和密码，对访问的IP来源也有限制。 集群会经常面临扩容， 所以每次扩容后必须对所有的DB库进行访问来源更新，费时费力， 而且DB的数量在不断的增加，因此就有了这个系统。

```

这个系统的工作原理是什么？

```

原理就是我们在访问来源（集群所有IP地址或者入口机 与 DB之间 搭建一层访问层）， 用户每次访问的时候我们的系统，我们去和DB进行交互。 

```

该系统的核心功能是啥？

```

通过haproxy软件，本地一个端口对应远端mysql服务。

```

如果采用haproxy的话，那么端口有没有一个范围呢？

```

当前端口是从8500用于第一个业务，已经增长到8530了。

```

这个系统在水平扩展方面或者容灾方面有哪些特点？

```

该系统当前有4台机器， 2台一组， 只有一组在使用，另外一组做灾难备用。 而在用的一组，当前部署有一枚KIP地址， 用户通过访问 dbgate.bigdata.xe.com 进行访问。

```

听说该系统在进行日常操作的时候还具有自动化的一些动能？

```

该系统设计本来就是为了方便 OPS、业务人员、DBA 的日常工作，所以在增强后段稳定性之后，我们又做了一个简单的前端，用于日常OPS快速操作， 其实也可以给用户使用，只是暂时我们想内部试验一些时间。

申请可以使用 http://xxx/scripts/dbgate.php

```

## 部署到的IP地址

所有地址

```

192.168.164.88,192.168.164.87,192.168.60.168,192.168.60.169

```

第一组地址\(主用组\)：

| IP地址 | 架构中的地位 | KIP |
| --- | --- | --- |
| 192.142.164.87 | 第一组-主 | 192.142.108.254 |
| 192.142.164.88 | 第一组-备 | 192.142.108.254 |

第二组（备份组）:

| IP地址 | 架构中的地位 | KIP |
| --- | --- | --- |
| 192.140.60.168 | 第二组-主 | 192.140.60.243 |
| 192.140.60.169 | 第二组-备 | 192.140.60.243 |

## 节点资格审查

* 软件是否部署

* 日志输出是否配置

* 脚本是否部署

## 配置文件

| 文件名称 | 文件描述 |
| --- | --- |
| common.cfg | 根据数据库中的记录生成的common.cfg这个haproxy配置文件 |
| common.cfg.bak | 每次生成common.cfg之前，先备份之前的为bak |
| config | 暂时没有用处 |
| dbgate.cn.allupdate.py | 不管任何条件，运行就根据dbgate表中的记录生成所有带有dbgate\_port记录的haproxy配置。主要用于重启，或者手工进行运行 |
| dbgate.cn.allupdate.sh | 是一个wrapper，py文件运行后，把common.cfg推到所有4个节点的/etc/haproxy/common.cfg |
| dbgate.cn.shencha.1.py | 审查文件，定时5分钟执行一次，针对dbgate表中没有dbgate\_port的条目，进行审查，看看是不是可以访问远程数据库，可以的话就更新为1，否则默认为0，仅此而已，而且4个机器对应dbgate\_port表中不同的column（字段） |
| dbgate.cn.shengxiao.py | 读取dbgate表中4个审查通过但是没有给出dbgate\_port的条目，分配port并且生成配置， |
| dbgate.cn.shengxiao.sh | 出发相似py文件，并且分发到所有节点的/etc/haproxy/common.cfg。 |
| dbgate.cn.txt | 4个节点的IP地址列表。 |
| update.sh | 更新/usr/local/scripts/下面的所有资料到4个节点。 |

## 基本软件安装

```
export http_proxy="http://192.180.86.30:3128"
yum install -y haproxy
cd /etc/haproxy && touch common.cfg && touch special.cfg
```

## 配置文件修改

### /etc/haproxy/haproxy.cfg

```
global
    log 127.0.0.1 local3
    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    maxconn     4000
    user        haproxy
    group       haproxy
    daemon
    # turn on stats unix socket
    stats socket /var/lib/haproxy/stats
defaults
    mode                    http
    log                     global
    option                  httplog
    option                  dontlognull
    option http-server-close
    #option forwardfor       except 127.0.0.0/8
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          1m
    timeout server          1m
    timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 3000
```

### /etc/sysconfig/haproxy

```
OPTIONS="-f /etc/haproxy/special.cfg -f /etc/haproxy/common.cfg"
```

### /etc/rsyslog.conf

```
echo '
$IncludeConfig /etc/rsyslog.d/*.conf 
' >> /etc/rsyslog.conf
```

### /etc/rsyslog.d/haproxy.conf

```
echo '
$ModLoad imudp
$UDPServerRun 514
local3.*     /var/log/haproxy.log
&~ 
' > /etc/rsyslog.d/haproxy.conf
```

### /etc/haproxy/haproxy.conf

```
# global配置中需要加入如下
    log 127.0.0.1 local3
```

## 定时任务部署

* 这个地方有些特别，因为涉及逻辑的时候，4台机器都是独立无二的，并且彼此之间紧密配合，这个地方只写如何部署，原理在其他地方进行详细介绍。

### 192.142.164.87 部署

```
# dbgate 审查通用脚本
*/5 * * * * /usr/local/scripts/dbgate.cn.shencha.1.py >> /var/log/dbgate.log

# dbgate对没有进行分配dbgate_port并且资格审查通过的case进行分配端口并生成配置
5,25,50 * * * * cd /usr/local/scripts/ && bash dbgate.cn.shengxiao.sh
```

### 192.142.164.87 部署

```
# dbgate 审查通用脚本
*/5 * * * * /usr/local/scripts/dbgate.cn.shencha.2.py >> /var/log/dbgate.log

# dbgate对没有进行分配dbgate_port并且资格审查通过的case进行分配端口并生成配置
10,35,55 * * * * cd /usr/local/scripts/ && bash dbgate.cn.shengxiao.sh
```

### 192.140.60.168 部署

```
# dbgate 审查通用脚本
*/5 * * * * /usr/local/scripts/dbgate.cn.shencha.3.py >> /var/log/dbgate.log

# dbgate对没有进行分配dbgate_port并且资格审查通过的case进行分配端口并生成配置
15,40 * * * * cd /usr/local/scripts/ && bash dbgate.cn.shengxiao.sh

```

### 192.140.60.169 部署

```
192.142.60.169部署如下

# dbgate 审查通用脚本
*/5 * * * * /usr/local/scripts/dbgate.cn.shencha.4.py >> /var/log/dbgate.log

# dbgate对没有进行分配dbgate_port并且资格审查通过的case进行分配端口并生成配置
20,45 * * * * cd /usr/local/scripts/ && bash dbgate.cn.shengxiao.sh

重启服务
service rsyslog restart
service haproxy restart
```

## 节点间相互访问

* 部署key

  ```
  http://ci.bigdata.xe.com/view/日常运维/job/deploy%20keys%20(1%20-%20create%20and%20rsync%20to%20server)/
  http://ci.bigdata.xe.com/view/日常运维/job/deploy%20keys%20(2%20-%20depoy%20keys)/
  http://ci.bigdata.xe.com/view/日常运维/job/deploy%20keys%20(3%20-%20test%20keys)/
  ```

* SSH白名单部署 使用 lingshu-pre.letv.cn 部署4节点白名单

## 运行维护

* 重启后，需要运行 dbgate.cn.allupdate.sh

## 遗留问题

* 目前我们采用的是restart，而不是reload，因为可能节点并没有启动。这样容易造成在restart的时候，如果haproxy在被使用，那么正在运行的程序就可能会完蛋。对了，可以采用service xx reload \|\| service xx restart

## 参考资料

* [http://www.shencan.net/index.php/2013/06/26/haproxy-%E6%97%A5%E5%BF%97%E8%AF%A6%E8%A7%A3/](http://www.shencan.net/index.php/2013/06/26/haproxy-%E6%97%A5%E5%BF%97%E8%AF%A6%E8%A7%A3/)

