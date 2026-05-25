# Cracked Star Jar Lategame Trajectory Dataset

## 目标

围绕上一轮 `cracked-star-jar` 300 秒 0% 胜率，追加最终图 120-300 秒定向规则 Bot 轨迹。

## 参数

- Bot：`kite`
- 地图：`cracked-star-jar`
- Seed 起点：37000
- Seeds：10
- 时长：300 秒
- Tick rate：30
- Observation：v2，长度 145
- Sample stride：10
- Sample start：120 秒

## 数据

- 总 sample：4807
- Episode：10
- 胜利：6
- 跳过升级样本：75
- 样本时间范围：120.3318 秒到 299.6817 秒
- 文件大小：约 6.9 MiB

## 结论

该数据集只用于最终图定向修复实验，不应单独训练成跨地图 policy。
