import pandas as pd

df = pd.read_csv('data.csv')
print(df.head())

print(df["月工资收入"])
print(df.loc[:,"月工资收入"])
print(df.iloc[:,3])

df.loc[4] = ["赵一平", "男", 34, 7000, "研发"]
print(df)

print(df["姓名"] == "张三")
df.loc[df["姓名"] == "张三", "月工资收入"] = 8000
print(df)

df.drop(1, axis=0, inplace=True)
print(df)

# 筛选
print(df["月工资收入"] >= 8000)
print(df[df["月工资收入"] >= 8000])

# 描述性分析
print(df["月工资收入"].describe())

print(df["年龄"].max())
print(df["年龄"].min())
print(df["年龄"].mean())
print(df["月工资收入"].max())
print(df["月工资收入"].min())
print(df["月工资收入"].mean())

print(df)

print(df.groupby("性别").agg(min))
print(df.groupby("性别").agg({"月工资收入": ["min", "max", "mean"]}))

print(df.pivot_table(index="性别", values="月工资收入", aggfunc="mean"))

print(df.pivot_table(index="性别", columns="部门", values="年龄", aggfunc=min))

# 部门的平均工资、平均年龄
import numpy as np
print(df.groupby("部门").agg({"年龄": np.mean, "月工资收入": np.mean}))

print(df.pct_table(index="部门", values="年龄", aggfunc=np.mean))
print(df.pct_table(index="部门", columns="性别", values="年龄", aggfunc=np.mean))