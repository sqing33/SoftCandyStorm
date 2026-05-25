# Behavior Clone Danger-Weighted Training

## 目标

验证 `--sample-weighting danger` 是否能在组合轨迹数据上提高低血量和中后期危险状态的学习权重，同时保持 action 分布可审查。

## 数据集

- 数据源：expanded 0-60 秒三图轨迹、60-300 秒三图 lategame 轨迹、`cracked-star-jar` 120-300 秒定向轨迹
- movement samples：19909
- episodes：40
- skipped upgrade samples：245
- observation len：145
- 地图分布：`soda-creek` 5389，`caramel-workshop` 4879，`cracked-star-jar` 9641
- health ratio average：0.8466

## 训练结果

- 门禁结论：`behavior_clone_smoke_only_not_policy_gate`
- sample weighting：`danger`
- class weighting：`none`
- epochs：20
- batch size：256
- train accuracy：0.9229
- validation accuracy：0.8998
- sample weight：min 1.0，max 3.903015，mean 1.574706

## 结论

危险状态重采样训练链路可用，且离线准确率保持稳定；但该报告只证明 supervised training 完成，不是 RL policy gate。模型必须继续通过 Gym 60/300 秒 high-pressure 多图对比审查。
