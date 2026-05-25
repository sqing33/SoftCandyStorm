# Lategame Kite Trajectory Dataset

## 目标

使用 `--sample-start-seconds 60` 导出 300 秒中后期规则 Bot 轨迹，补齐上一版 behavior clone 缺少的 Boss、升级后 Build、敌群压力和危险区状态。

## 参数

- Bot：`kite`
- 地图：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- Seed 起点：34000
- Seeds：5 / map
- 时长：300 秒
- Tick rate：30
- Observation：v2，长度 145
- Sample stride：10
- Sample start：60 秒

## 数据

- 总 sample：9790
- Episode：15
- 跳过升级样本：131
- 文件大小：约 13 MiB
- 样本时间范围：60.3328 秒到 299.6817 秒

动作分布更均衡，最大动作 action `3` 占 14.42%，但仍没有 action `0` 原地样本。
