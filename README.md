# tb-auto-sign-up

百度贴吧自动签到

克隆本项目：

```ba
https://github.com/SodiumNya/tb-auto-sign-up.git

```

#### 在scrpit.py中做如下修改：

1. 在myCookies中填入你的**cookie** ：

   ![image-20240226023609549](C:\Users\wang\AppData\Roaming\Typora\typora-user-images\image-20240226023609549.png)

2. 将**邮箱地址、授权码、host** 修改为真实的**邮箱地址、授权码、host**

![image-20240226030104011](C:\Users\wang\AppData\Roaming\Typora\typora-user-images\image-20240226030104011.png)

3. 将要接收签到报告的邮箱填入**email_to**， 这是一个list， 你可以添加多个， 或仅保留一个：

   ![image-20240226030327746](C:\Users\wang\AppData\Roaming\Typora\typora-user-images\image-20240226030327746.png)

#### 完成以上步骤之后， 你需要让它定时执行， 方式有很多，可以自行研究

#### 我的实现方式是在linux云服务器上使用定时任务

#### 如果和我一样，那么这是一个实现参考：

1. 将本项目放到你的云服务器的某个文件夹下，如: **/root/python-project/**

2. 在云服务器的某个位置编写一个脚本文件，用来执行本项目，脚本内容可参考：

```bas
#!/bin/bash

# 生成 0 到 59 之间的随机数作为等待时间
random_seconds=$((RANDOM % 3600))

# 等待随机秒数
sleep $random_seconds

# 执行 贴吧签到项目的 main.py 文件, 签到
python3 /root/tb-auto-sign-up/main.py
```

你可以直接复制到你的bash脚本文件中

3. 创建好脚本文件后，在云服务器的命令行中以此输入以下命令:

   确保之前新建的脚本文件有执行权限(注意把/root/bash/tb-auto-sign-up.sh换位你自己的脚本路径)：

   ```bash
   chmod +x /root/bash/tb-auto-sign-up.sh
   ```

   编辑crontab文件，新建一个定时任务：

   ```bash
   crontab -e
   ```

   在编辑器中添加一行，指定任务的执行时间和要运行的脚本(vim 不知道如何操作请自行百度)：

   ```bash
   0 6 * * * /root/bash/tb-auto-sign-up.sh
   ```

   保存并退出后， 若命令没有输入错误，那么cron将会在每天早上6点执行脚本，而脚本会在六点的某个随机时间点执行签到操作

4. 完成以上步骤后，就能实现百度贴吧自动签到。

如果遇到任何问题，可以联系我sodiumnya@gmail.con或者提出issue





​	

