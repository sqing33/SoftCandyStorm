# Expanded Kite Trajectory Dataset

## 目标

扩大规则 Bot 轨迹覆盖，验证数据侧扩展是否比单纯 loss 加权更能缓解 behavior clone deterministic 动作塌缩。

## 参数

- Bot：`kite`
- 地图：`soda-creek`、`caramel-workshop`、`cracked-star-jar`
- Seed 起点：31000
- Seeds：5 / map
- 时长：60 秒
- Tick rate：30
- Observation：v2，长度 145
- Sample stride：5

## 数据

- 总 sample：5312
- Episode：15
- 跳过升级样本：39
- 文件大小：约 5.5 MiB

动作分布：

- action `1`：596，11.22%
- action `2`：315，5.93%
- action `3`：2127，40.04%
- action `4`：316，5.95%
- action `5`：602，11.33%
- action `6`：473，8.90%
- action `7`：486，9.15%
- action `8`：397，7.47%

action `0` 不存在，说明当前 KiteBot 轨迹没有原地动作样本。
