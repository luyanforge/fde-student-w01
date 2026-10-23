## 这次改了什么

<!-- 一到三句话。写"做了什么、为了什么"，不要只写"更新了代码"。 -->

## 改动类型

- [ ] 业务代码（`platform/fde_product/`）
- [ ] 模型适配器（`platform/fde_product/models.py`）
- [ ] 工具脚本（`tools/`）
- [ ] 交付产物（`artifacts/w0x/`、`docs/w0x/`）
- [ ] 仅文档
- [ ] 纯环境适配（不影响行为，只为在本机跑通）

## 是否触碰契约

- [ ] 否，本次不改任何契约、能力矩阵或版本号
- [ ] 是 → 涉及：
  - [ ] `contracts/w0x/` 结构
  - [ ] `product/capabilities.json`
  - [ ] 版本号（`product_version` / `capability_matrix_version` / 契约版本）
  - [ ] `MANIFEST.json` 需要重新生成

> 改契约等于改验收标准，必须单独说明为什么旧契约无法表达新事实。

## 适配器改动（改了 `models.py` 必填）

- **现象**：哪一项验证失败，报什么错（贴原始错误码与错误串）
- **根因**：定位到哪一层——端点严格性、协议差异、还是自己的 schema 有缺陷
- **改法**：改在适配器层还是业务层；为什么这样切
- **是否改变工具契约**：名称 / 描述 / 必填项 / 业务语义有否变动（应为"均未变"）
- **改动前后对照**：同一请求改前的响应 与 改后的响应

<!-- 只写"修好了"不算证据。留下 400 → 200 的原始对照才有价值。 -->

## 验证

- [ ] `pytest tests/test_product_v2.py tests/test_product_interaction.py` → 38 passed
- [ ] `tools/verify_product.py --live` → 11/11 通过（真模型，非 mock）
- [ ] Promptfoo 评估 → 通过条数 / 总数，失败 0、错误 0
- [ ] `tools/check_product.py --root .` → `status: pass`，`errors: []`
- [ ] 证据已备份，未覆盖上一轮 `artifacts/` 结果

验证摘要：

| 检查 | 结果 |
| --- | --- |
| verify_product --live |  |
| environment_check |  |
| model_baseline |  |
| runtime_evidence |  |
| Promptfoo |  |

## fit-gap 联动

- [ ] 本次改动不影响任何 fit-gap 条目
- [ ] 需要修订条目：
  - 条目编号：`GAP-___`
  - 分类变化：`___` → `___`
  - 证据状态变化：`___` → `___`
  - 新增证据 `locator`：`___`

> 分类（产品已有 / 客户配置 / 系统适配 / 产品缺口 / 暂不承诺 / 待判断）与证据状态（`verified` / `reported` / `unknown` / `conflicting`）是两件事，改一个不等于改另一个。

## 承诺边界

- [ ] 未新增任何效果或时间承诺
- [ ] 未把 `reported` 写成 `verified`
- [ ] 未把"暂不承诺"改回"产品已有"
- [ ] 未把客户单方说法当作已核实事实
- [ ] 客户侧口头共识若被引用，已注明是口头还是书面确认

如果以上有任何一项无法勾选，在这里说明理由：

## 数据与密钥

- [ ] 未提交 `.model.env` / `*.key` / 任何凭据
- [ ] 未提交客户真实数据（只允许课程样例与脱敏样本）
- [ ] 未提交 `.venv/` / `.runtime/` / `__pycache__/` / `.pytest_cache/`
- [ ] 已扫描入库文件，确认无 `sk-` 前缀、`Bearer <长串>`、`apiKey` 赋值等特征

## 证据位置

<!-- 例如 artifacts/w02/evidence/、docs/w02/project_assessment.md、某次评估的 promptfoo-results.json -->

## 遗留问题

<!-- 明确写出本次没解决什么、卡在谁手里、下一步要什么。没有就写"无"。 -->
