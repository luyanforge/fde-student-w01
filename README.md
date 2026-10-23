# FDE W01 · 标准会员运营 Agent（个人工程记录）

本仓库是 FDE 课程第一周的完整工作记录：从课程下发的标准产品 `0.2.0-w1` 出发，在本机跑通真实模型与标签 API，完成客户访谈与立项判断，并把中途不得不做的适配改动留在明处。

仓库只有一个目的——**让"改了什么、为什么改、凭什么说它跑通了"可以被逐条核对。**

- 产品版本：`0.2.0-w1`　能力矩阵：`w1-capabilities-0.2.0`
- fit-gap 契约：`w01-0.2.1`（兼容 `w01-0.2.0`）　其余三份 JSON：`w01-0.2.0`
- 课程原始 README 完整保留在 [`docs/course-readme-original.md`](docs/course-readme-original.md)，或 `git show 543dd9b:README.md`

## 1. 两个提交的关系

| 提交 | 内容 | 说明 |
| --- | --- | --- |
| `543dd9b` | import: 0.2.0-w1 原始基线（未修改） | 课程原样副本，48 个文件。逐文件比对 `MANIFEST.json` 的 SHA-256，**46/46 字节一致**，0 不匹配、0 缺失 |
| `e73e60c` | feat(w01): 适配器补齐类型 + W01 交付 | 业务代码只改 **2 个文件**，其余为新增工具脚本与交付产物 |

只看代码改了什么：

```sh
git diff 543dd9b HEAD -- platform/ evals/
```

基线提交为保证"原样"额外带了一个 `.gitattributes`（内容 `* -text`）。它只关闭 Git 的行尾自动转换，不参与产品运行、不改变任何文件内容。原因见第 5 节。

## 2. 改了什么，为什么改

### 2.1 `platform/fde_product/models.py`（+50 / −1）

新增 `normalized_tools()`，在发请求前补齐工具 schema 里缺失的 JSON Schema `type`。

**现象**：首次真模型验证 11 项中 8 项通过，`http_action`、`idempotency`、`undo`、`reject_change` 4 项全部返回 `MODEL_HTTP_400`。

**根因**：产品自己的工具定义里，`prepare_tag` 的参数 `tag` 只写了 `{"enum": [...]}`，没有 `type`。严格端点（Moonshot）拒绝这种 schema：

```
properties.tag: type is not defined
```

**改法**：按 `enum` 的取值推断类型（全字符串 → `string`，全整数 → `integer` 等），递归遍历 `properties` / `items` / `anyOf` 等结构。改动压在适配器层——工具契约、名称、描述、必填项与业务语义均未变，`agent.py` 业务代码零改动。依据是任务书第 54 行"不同模型的接口不兼容时修改适配器并保留证据"。

**对照**：补 `type` 后同一请求返回 200，4 项全部转为通过。

### 2.2 `evals/promptfooconfig.yaml`（+1 / −1）

`pythonExecutable` 由 Unix 相对路径 `../.venv/bin/python` 改为 Windows 解释器路径。

### 2.3 新增工具脚本（`tools/`）

| 脚本 | 作用 |
| --- | --- |
| `with_env.py` | 从 `.model.env` 注入模型环境变量，密钥不进命令行、不进日志 |
| `probe_model.py` | 单条最小请求预检端点连通性，5 秒判断通不通 |
| `patch_uuid_utils_fallback.py` | `uuid_utils` 原生扩展被安全策略拦截时，在两个调用点改用纯 Python 实现 |
| `run_eval.py` | Promptfoo 评估的一键封装（走 npmmirror，Windows 下用 `cmd /c npx`） |
| `07_fit_gap_to_json.py` | fit-gap 表格转契约 JSON |

> `patch_uuid_utils_fallback.py` **重装依赖后必须重跑一次**，否则 `langchain_core` 导入会失败。

## 3. 怎么跑起来（Windows）

前置：Python 3.11+、Node 22.22.0+（评估用）。Node 默认从 `PATH` 查找，也可以用 `FDE_NODE_DIR` 指向 node 所在目录；`tools/run_eval.py --check` 可先自检。

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe tools/patch_uuid_utils_fallback.py   # 安全策略拦截原生扩展时必需
.venv/Scripts/python.exe tools/product.py init
.venv/Scripts/python.exe tools/check_product.py --dry-run
```

配置模型：复制 `.model.env.example` 为 `.model.env`，填三行。

```ini
FDE_MODEL_URL=https://<host>/v1/chat/completions
FDE_MODEL_NAME=<模型名>
FDE_MODEL_KEY=<密钥>
FDE_MODEL_PROFILE=compatible
```

不想让密钥进环境变量，可以只写 `FDE_MODEL_KEY_FILE=<密钥文件路径>`，程序就地读取。`.model.env` 与 `*.key` 已在 `.gitignore` 中。

验证与评估：

```bash
.venv/Scripts/python.exe tools/with_env.py -- .venv/Scripts/python.exe tools/probe_model.py
.venv/Scripts/python.exe tools/with_env.py -- .venv/Scripts/python.exe tools/verify_product.py --live
.venv/Scripts/python.exe tools/run_eval.py --check            # 先确认 Node 环境，不跑评估
.venv/Scripts/python.exe tools/with_env.py -- .venv/Scripts/python.exe tools/run_eval.py
.venv/Scripts/python.exe tools/finalize_evaluation.py
.venv/Scripts/python.exe tools/check_product.py --root .
```

## 4. 验证结果

| 检查 | 结果 |
| --- | --- |
| `verify_product.py --live` | **11/11 通过**（约 4 分 30 秒） |
| 环境检查 `environment_check` | 9/9 `pass`，`model_mode=live` |
| 模型基线 `model_baseline` | 9 次带 trace 的运行，失败 0 |
| 运行证据 `runtime_evidence` | 11 个用例全部通过，12 个哈希文件 |
| Promptfoo 0.122.2 | **7/7 通过**，0 失败、0 错误，53,349 token |
| 回归测试 | 38 passed |
| `check_product.py --root .` | `status: pass`，`errors: []` |

本轮模型：Kimi Code / `k3-256k`，`profile=compatible`，端点 `https://api.kimi.com/coding/v1/chat/completions`。

> 这些数字说明"标准产品在本机真实模型下按契约跑通"，**不说明**它能解决青禾的复购问题。前者是工程事实，后者是立项判断，两者在 `docs/w01/project_assessment.md` 里分开写。

## 5. 一个已记录的环境坑

本机 `core.autocrlf=true`。第一次提交基线时，Git 把 `sample_data/` 下 4 个 **CRLF** 换行的 CSV 在内部 blob 里改写成了 LF（`members.csv` 350B → 340B），内容不变但字节不等，"原样基线"就不成立了。

对策是仓库根加 `.gitattributes`（`* -text`）关闭行尾转换，然后重建历史重新提交。

**判据**：校验基线必须比对 `git show <commit>:<path>` 的 blob 字节，不能只比对工作区文件——在 autocrlf 下工作区仍是 CRLF，看着一致其实是误判。

## 6. 目录导航

| 路径 | 内容 |
| --- | --- |
| `docs/w01/project_assessment.md` | **立项判断报告**（本周作业主体） |
| `docs/w01/访谈实录_沈总.md` | 12 轮访谈逐轮记录，含 `reported` / `unknown` / `conflicting` 标注与修订过程 |
| `docs/w01/沈总首轮访谈问题清单*.md` | 30 问题库与 12 问执行版 |
| `docs/w01/一页判断_给沈总.md` | 给客户的决策页，含三个待拍板点 |
| `docs/w01/范围与验收确认备忘.md` | 把口头共识落成文字的范围与验收确认 |
| `artifacts/w01/*.json` | 四份契约 JSON |
| `artifacts/w01/evidence/` | 11 个用例的运行证据与哈希 |
| `docs/course-readme-original.md` | 课程原始 README（未修改） |

## 7. 后续节奏

每周一个 W0x 目录，产物按周保存，不覆盖上一周的证据。改动前先备份 `artifacts/w0x/`。

提交规范见 [`.github/pull_request_template.md`](.github/pull_request_template.md)——里面把"改没改契约、留没留下适配证据、fit-gap 要不要联动修订、有没有越界承诺"做成了勾选项，提 PR 时逐条过一遍。

一条持续约束：**适配器层可以改，业务语义和承诺边界不能悄悄改。** 任何一次把 `reported` 写成 `verified`、把"暂不承诺"改回"产品已有"的动作，都必须在 PR 描述里单独说明理由。

## 8. 边界

本产品只绑定本机地址，用于单人教学。基础角色是主机配置，不是生产认证或多租户隔离。客户数据、客户连接器与生产治理均未接入；W1 全周只开放发起人一个角色，因此流程与数据类诉求最多到 `reported` / `unknown`。
