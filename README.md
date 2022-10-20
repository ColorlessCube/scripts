## 背景

日常工作、生活中，有许多工作可以交给脚本完成，无需自己手动操作。对于这些工作，本人秉持自动化优先的理念，将其交给脚本完成。

很多工作是重复性的，需要定时周期性执行。在薅羊毛的过程中，发现青龙面板是很好的定时任务工具，因此将其作为脚本的管理工具。

## 脚本说明

### blog.py

Typecho 是我的博客系统，但是在网页编辑文章再发布十分麻烦，本人习惯使用 Typora 本地编辑再上传网页端。但是，有时候厌烦文章的发布和更新，需要手动编辑，十分麻烦。

博客系统的本质无非是将数据库里的数据呈现在网页端，那么使用脚本检测本机的 Markdown 文档与 Typecho 数据库中的文章是否存在或一致。如果不存在该文章，则向数据库中添加，否则更新，不涉及删除。

主要流程：

1. 读取本地的 Markdown 文档数据并解析，本地的文档数据以一定规范书写；
2. Query Typecho 数据库中的文档数据；
3. 两者以 uuid 作为唯一标识符关联，比较文档数据，检查文章主体、文章便签、文章分类等数据是否发生变化，是否需要更新或创建。

### clash.py

本人在小米 AX3600 路由器中使用 shellclash 代理家中的流量数据。但是由于使用的是购买的 VPN 服务，因此有时候服务器厂商的节点会由于用户数量的变化产生波动。因此希望能够定时让 shellclash 去 ping 服务节点，并随时进行节点的更换。

### home_device_controller.py

最近天气冷了，本人体质不好，要使用暖脚宝来给足部供热。但是呢，暖脚宝比较垃圾，利用电阻发热，也没有提供很好的温度控制开关。因此，有时候暖脚宝太烫了得手动关闭，冷了又得手动开启，十分的麻烦。因此，利用家里闲置的智能开关，该开关已经接入 Home Assistant 中，一个智能家居管理平台。但是该平台也是开源项目，自动化需要写 yaml 脚本以及一系列复杂的配置项，学习成本较高。好在该平台提供了 RESTful API，详情见[官网](https://developers.home-assistant.io/docs/api/rest/)，所以就可以通过写简单的脚本来实现设备的控制，配合青龙面板实现定时任务。一般只需要获取设备的状态，设置设备的状态两个 API 即可完成大部分操作。

- 获取状态：/api/states/<entity_id>；
- 设置状态：/api/services/<domain>/<service>，其中 domain 为设备类型，例如 switch，service 为该设备类型的操作，如 turn_off。

## 版本

### V 0.1.1.221013

- 优化 `blog.py` 自动更新，增加 `uuid` 字段识别唯一文章，即使该 Markdown 文档的文件名称或文章标题发生变化，也不会影响文章内容的更新。

### V 0.1.2.221018

- 优化 `clash_check.py` 代理检查脚本，使用线程池的方式去测试代理的延迟，因为网络 I/O 大部分时间都是处于 pending 状态，使用多线程的方式测试网络代理，替代原来的队列的模式，能够节约大量网络 I/O 的时间。

### V 0.1.2.221020

- 增加 `home_device_controller.py` home assistant 设备控制脚本，通过 home assistant 提供的 api 来实现对家庭设备的控制，配合青龙面板实现定时任务。此次更新，原始脚本包含获取设备状态功能和设置设备状态功能。
