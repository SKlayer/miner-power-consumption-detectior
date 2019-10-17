# 用于矿机的机架功耗收集服务器
```
#
#
#      +------------------+
#      | IN MATH WE TRUST |
#      +------------------+
#   ___        S9          ___
#   |挖|                   |卖|
#   |矿|                   |币|
#   |马|   S17      T17    |立|
#   |上|        L3+        |刻|
#   |回|        T9+        |赚|
#   |本|   T15      S15    |钱|
#   --------------------------
#
#
#
```

## 如何部署？
    ```shell
    git clone https://github.com/SKlayer/miner-power-consumption-detectior.git
    cd miner-power-consumption-detectior/
    # 这里修改config.csv为你自己的配置文件
    if 是docker部署:
        chmod +x init.sh
    else:
        python ./init.py
    ```
## 配置在哪，怎么改？
    端口，listen IP 在init.py 里面改
    电力表相关在config.csv里面改
    格式是：IP, 表的SN ，COM口
## 憋说话， 打钱
    BTC 33Mq3MaPCo8qCHVbCFLFaAxDRVWZR2e8SP
    BCH qqjg2kjjqxyttmvvenr7ad9yklsjswpjyyatdkxpyw
    
