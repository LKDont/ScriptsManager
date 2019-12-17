#!/usr/bin/env python
"""
脚本管理器
"""
import os
import shutil
import sys
import sqlite3
import time
from prettytable import PrettyTable

# 版本号
VERSION = "1.0.0"

USER_HOME = os.path.expanduser('~')
SCRIPTS_MAN_DIR = os.path.join(USER_HOME, ".scripts-man")


def exit_app():
    """
    退出程序
    """
    sys.exit()


"""
--------------------------------数据库操作--------------------------------
"""

# 数据库文件
SCRIPTS_DB_PATH = os.path.join(SCRIPTS_MAN_DIR, ".scripts")
# 数据库表名
SCRIPTS_TABLE = "scripts"


def init_db(db_path):
    """
    初始化数据库
    """
    if not os.path.exists(SCRIPTS_MAN_DIR):
        # 创建文件夹
        os.mkdir(SCRIPTS_MAN_DIR)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS %s "
                       "(id INTEGER PRIMARY KEY AUTOINCREMENT, name, path, info, time)" % SCRIPTS_TABLE)
        cursor.close()
        conn.commit()


def insert_script_to_db(db_path, script_name, script_path, script_info):
    """
    插入脚本
    """
    cur_time = time.time()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO %s (name, path, info, time) VALUES (?, ?, ?, ?)" % SCRIPTS_TABLE,
                       (script_name, script_path, script_info, cur_time))
        result = [
            cursor.lastrowid,
            script_name,
            script_path,
            script_info,
            cur_time
        ]
        cursor.close()
        conn.commit()
    return result


def query_scripts_from_db(db_path, where=None):
    """
    获取脚本列表
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        if where is None or len(where) <= 0:
            cursor.execute("SELECT id, name, path, info, time FROM %s" % SCRIPTS_TABLE)
        else:
            cursor.execute("SELECT id, name, path, info, time FROM %s WHERE %s" % (SCRIPTS_TABLE, where))
        values = cursor.fetchall()
        cursor.close()
        conn.commit()
    return values


def delete_scripts_from_db(db_path, where):
    """
    删除脚本
    """
    if where is None or len(where) <= 0:
        print_err_msg("删除脚本命令的where不能为空")
        exit_app()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM %s WHERE %s" % (SCRIPTS_TABLE, where))
        cursor.close()
        conn.commit()


"""
--------------------------------输出信息--------------------------------
"""


def get_colored_text(color, content):
    """
    获取带有颜色的字符串
    """
    if color == "black":
        c = "30"
    elif color == "red":
        c = "31"
    elif color == "green":
        c = "32"
    elif color == "yellow":
        c = "33"
    elif color == "blue":
        c = "34"
    elif color == "magenta":
        # 洋红
        c = "35"
    elif color == "cyan":
        # 青色
        c = "36"
    else:
        # 白色
        c = "37"
    return "\033[%sm%s\033[0m" % (c, str(content))


def print_err_msg(msg):
    """
    打印错误信息
    """
    print(get_colored_text("red", msg))


def print_help():
    """
    打印帮助信息
    """
    print("脚本管理器")
    print("  -v, -version 版本号")
    print("  -h, -help 帮助信息")
    print("  -l, list 列出全部脚本")
    print("  add [-cp] <script_path> 添加脚本，如果带有-cp参数脚本文件会被复制到~/.scripts-man")
    print("  rm <script_name> 删除脚本")
    print("  autoremove 自动删除无效脚本")
    print("  run <script_name> 运行脚本")


def print_version():
    """
    打印版本号
    """
    print("脚本管理器 : ver" + VERSION)


def format_time(t):
    """
    格式化时间
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def print_scripts(scripts):
    """
    输出脚本信息，这个版本不输出Info字段
    """

    # try:
    #     from prettytable import PrettyTable
    # except ModuleNotFoundError:
    #     print_err_msg("ScriptManager需要prettytable模块，请执行以下命令安装：")
    #     print(get_colored_text("green", "pip3 install prettytable"))
    #     exit_app()
    #     return

    out_table = PrettyTable(
        ["Index",
         "Name",
         "Path",
         # "Info",
         "Time"
         ])
    out_table.align["Name"] = "l"
    out_table.align["Path"] = "l"
    # out_table.align["Info"] = "l"
    out_table.padding_width = 1

    for script in scripts:
        script_id = script[0]
        script_name = script[1]
        script_path = script[2]
        # script_info = script[3]
        script_time = format_time(script[4])
        if os.path.exists(script_path):
            txt_color = "green"
        else:
            txt_color = "red"
            script_name = "(missed)" + script_name
        out_table.add_row([
            get_colored_text(txt_color, script_id),
            get_colored_text(txt_color, script_name),
            get_colored_text(txt_color, script_path),
            # get_colored_text(txt_color, script_info),
            get_colored_text(txt_color, script_time)
        ])

    print(out_table)


"""
--------------------------------脚本管理--------------------------------
"""


def get_scripts(db_path, filter_path=False):
    """
    获取全部脚本
    """
    scripts = query_scripts_from_db(db_path)
    if filter_path:
        # 过滤脚本
        result = []
        for script in scripts:
            script_path = script[2]
            if os.path.exists(script_path):
                result.append(script)
    else:
        result = scripts

    return result


def get_script(db_path, script_name):
    """
    获取脚本
    """
    if script_name is None or len(script_name) <= 0:
        return None

    scripts = query_scripts_from_db(db_path, where="name='%s'" % script_name)
    if len(scripts) > 0:
        return scripts[0]
    else:
        return None


def list_scripts(db_path):
    """
    列出全部脚本
    """
    scripts = get_scripts(db_path)
    print_scripts(scripts)


def check_duplicate_script(scripts, script_path):
    """
    检查脚本是否重复
    """
    (script_dir, script_file_name) = os.path.split(script_path)
    (script_name, script_extension) = os.path.splitext(script_file_name)
    for script in scripts:
        name = script[1]
        path = script[2]
        if script_path == path:
            print_scripts([script])
            print_err_msg("脚本已经被添加了：" + path)
            exit_app()
        if script_name == name:
            print_scripts([script])
            print_err_msg("已存在同名的脚本：" + name)
            exit_app()

    return script_name


def add_script(db_path, script_path, script_info, copy):
    """
    添加脚本
    """
    if not os.path.exists(script_path) or not os.path.isfile(script_path):
        print_err_msg("脚本路径不存在")
        exit_app()

    # 获取文件名
    (script_dir, script_file_name) = os.path.split(script_path)

    scripts = get_scripts(db_path)

    # 判断脚本是否有重复
    if copy:
        script_name = check_duplicate_script(scripts, os.path.join(SCRIPTS_MAN_DIR, script_file_name))
    else:
        script_name = check_duplicate_script(scripts, script_path)

    if copy:
        # 复制文件
        dst_path = os.path.join(SCRIPTS_MAN_DIR, script_file_name)
        shutil.copy(script_path, dst_path)
        script_path = dst_path

    # 添加脚本
    script = insert_script_to_db(db_path, script_name, script_path, script_info)
    # 打印信息
    print_scripts([script])
    print("添加脚本成功")


def auto_remove_unavailable_scripts(db_path):
    """
    自动删除不可用的脚本
    """
    scripts = get_scripts(db_path)
    del_scripts = []
    for script in scripts:
        script_id = script[0]
        script_path = script[2]
        if not os.path.exists(script_path):
            del_scripts.append(script)
            delete_scripts_from_db(db_path, "id=%d" % script_id)
    # 打印信息
    if len(del_scripts) > 0:
        print_scripts(del_scripts)
        print("删除%d个脚本" % len(del_scripts))
    else:
        print("没有需要删除脚本")


def remove_script(db_path, script_name):
    """
    删除指定的脚本
    """
    scripts = get_scripts(db_path)
    del_script = None
    for script in scripts:
        if script[1] == script_name:
            del_script = script
            break
    if del_script is not None:
        delete_scripts_from_db(db_path, "id=%d" % del_script[0])
        # 如果脚本在SCRIPTS_MAN_DIR，需要把脚本文件也删除
        path = del_script[2]
        (script_dir, script_file_name) = os.path.split(path)
        if script_dir == SCRIPTS_MAN_DIR:
            os.remove(path)
        print("删除%s成功" % script_name)
    else:
        print("找不到%s脚本" % script_name)


def run_script(db_path, script_name, params):
    """
    运行脚本
    """
    script = get_script(db_path, script_name)
    if script is None or not os.path.exists(script[2]):
        print_err_msg("找不到这个脚本：" + script_name)
        exit_app()
    script_path = script[2]
    # 运行
    status = os.system("source " + script_path + " " + " ".join(params))
    print("运行结果：" + str(status))


"""
--------------------------------主程序--------------------------------
"""


def main():
    """
    主程序
    """
    argv_len = len(sys.argv)
    if argv_len <= 1:
        print_help()
        exit_app()

    if not os.path.exists(SCRIPTS_MAN_DIR):
        # 创建文件夹
        os.mkdir(SCRIPTS_MAN_DIR)

    # 初始化数据库
    init_db(SCRIPTS_DB_PATH)

    comm = sys.argv[1]
    if comm == "-v" or comm == "-version":
        print_version()

    elif comm == "-l" or comm == "list":
        list_scripts(SCRIPTS_DB_PATH)

    elif comm == "autoremove":
        auto_remove_unavailable_scripts(SCRIPTS_DB_PATH)

    elif comm == "rm":
        if argv_len <= 2:
            print_help()
            print_err_msg("请输入要删除的脚本名字")
            exit_app()
        script_name = sys.argv[2]
        remove_script(SCRIPTS_DB_PATH, script_name)

    elif comm == "add":
        if argv_len <= 2:
            print_help()
            print_err_msg("请输入要添加的脚本路径")
            exit_app()
        cp = sys.argv[2] == "-cp"
        if cp:
            if argv_len <= 3:
                print_help()
                print_err_msg("请输入要添加的脚本路径")
                exit_app()
            path = sys.argv[3]
        else:
            path = sys.argv[2]
        add_script(SCRIPTS_DB_PATH, path, "", copy=cp)

    elif comm == "run":
        if argv_len <= 2:
            print_err_msg("请输入要运行的脚本名字")
            print_help()
            exit_app()
        name = sys.argv[2]
        run_script(SCRIPTS_DB_PATH, name, sys.argv[3:argv_len])

    else:
        print_help()


if __name__ == "__main__":
    main()
