# 脚本管理器

* 版本：1.0.1

在使用linux系统的时候，经常会编写脚本用来执行一些简单重复的工作。长此以往，会积累很多零散的脚本，从而导致忘记脚本的位置和作用。这个脚本管理器就是为了管理这些零散的脚本，将它们集中一起管理。只需要你还记得scripts-man的命令，就能轻松管理那些零散的脚本。



## 打包和安装

首先请确保你的系统已经安装了python3，然后安装pyinstaller模块用于打包。

```bash
pip3 install https://github.com/pyinstaller/pyinstaller/archive/develop.tar.gz
```

然后在工程根目录执行打包命令：

```bash
pyinstaller -F scripts-man.py
```

在当前目录下的dist文件夹中可以找到可执行文件，将该文件复制到/usr/local/bin，请确保/usr/local/bin路径已经在你的环境变量PATH中。这样就完成了scripts-man的安装，你能在系统的其它位置使用scripts-man命令。



## 使用

脚本管理器
  -v, -version 版本号
  -h, -help 帮助信息
  -l, list 列出全部脚本
  add [-cp] <script_path> 添加脚本，如果带有-cp参数脚本文件会被复制到~/.scripts-man
  rm <script_name> 删除脚本
  autoremove 自动删除无效脚本
  run <script_name> 运行脚本