# Behavior Clone Context3 Danger-Weighted Training

## 目标

验证 3 帧 observation 拼接的 behavior clone 训练链路是否可用，并与上一轮 danger-weighted 单帧模型保持相同数据来源和采样权重。

## 数据集

- 数据源：expanded 0-60 秒三图轨迹、60-300 秒三图 lategame 轨迹、`cracked-star-jar` 120-300 秒定向轨迹
- movement samples：19909
- episodes：40
- base observation len：145
- context frames：3
- input observation len：435
- sample weighting：`danger`
- sample weight：min 1.0，max 3.903015，mean 1.574706

## 训练结果

- 门禁结论：`behavior_clone_smoke_only_not_policy_gate`
- epochs：20
- batch size：256
- train accuracy：0.9135
- validation accuracy：0.8687
- 模型：`python/train/models/behavior_clone_kite_high_pressure_context3_danger_weighted_smoke.pt`

## 评估状态

60 秒和 300 秒 high-pressure Gym 对比未完成。当前本机新生成 Rust 可执行文件出现启动阻塞：`spctl -a -vv target/debug/game_harness` 和最小 `rustc` hello binary 均返回 `rejected`，进程采样停在 `_dyld_start`，导致 `game_harness gym-bridge` 无法可靠响应。

## 结论

3 帧序列上下文训练链路已完成，但该模型没有通过 Gym 对比门禁，不能作为 RL 测试 Bot 候选。恢复 Rust binary 启动环境后，必须重新运行 60/300 秒 high-pressure 多图对比，再决定是否推进或记录新的 policy failure case。
