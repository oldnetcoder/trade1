import sqlite3

# 连接数据库
conn = sqlite3.connect('td.db')

# 创建游标
cursor = conn.cursor()

# 查询表中所有数据
cursor.execute('SELECT * FROM trades')
rows = cursor.fetchall()

# 打印数据
for row in rows:
    print(row)

# 关闭游标和连接
cursor.close()
conn.close()
