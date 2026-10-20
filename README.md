# 沙特电商巡店 · Saudi Store Audit

一个可安装到 Codex 的 Skill：按 Google Sheets 中的商品链接巡检沙特 Noon 与 Amazon.sa，每天追加带日期的价格列组，记录划线价、当前售价、缺货与实际卖家，保留历史。

本项目提供巡店 SOP、技能资源、安装/打包工具和离线验收样例。实际巡店由 Codex 使用已连接的 Google Sheets 工具与可交互浏览器执行。

## 主要规则

| 平台 | 每天新增的字段 | 日期位置 |
|---|---|---|
| Noon | MSRP / Price / Note | 第1行字段，第2行日期跨3列合并 |
| Amazon.sa | MSRP(SAR) / Offer Price / buy box / Note | 第1行日期跨4列合并，第2行字段 |

- 当天没有列组时在全部已用列右侧新增；当天已有唯一完整组则复用。日期重复或结构不明时报告，不覆盖历史。
- MSRP 只填对应商品页面的可见划线价，没有则留空；在售时售价填数字。
- 确认缺货时，Price／Offer Price 填文本 **OOS**；页面访问失败、没有默认报价或加载未完成不能直接当成缺货。
- Note 只填写 `sold by 实际非平台卖家名`，否则留空。失败原因、运费、成色与详细证据进入巡店报告。
- Price／Offer Price正文统一右对齐，数字和文本OOS显示一致。缺链接行的当天Note留空；已有自动Note按归属证据清理，人工/公式冲突保留并报告。
- 有内容的当天Note按完整文字自动列宽、单行显示；全空Note列保持宽度，不缩小字体、不增加行高，不调整历史列。
- Noon 显示 `This product is not available` 且同行 Status=EOL 时，当天 MSRP、Price、Note 均留空。Status 按表头定位；同日重跑仅清理当天自动结果，保留人工内容和历史。
- Amazon 先设配送地区为 Riyadh, Saudi Arabia。存在默认报价且发货方与卖家均为 Amazon.sa 时 buy box=1；明确不符合或没有当前可售/默认报价时为0；证据不足留空。
- 每个商品按原表链接核实同一变体，通常5–15行一批写入，并逐格读回复核。

完整判断规则见 [SKILL.md](skills/saudi-store-audit/SKILL.md) 和 [回写规则](skills/saudi-store-audit/references/writeback.md)。

## 安装

### 在 Codex 中安装

将下面这句话发送给 Codex：

```text
使用 $skill-installer 从 https://github.com/Yisong-Qian/saudi-store-audit 安装 skills/saudi-store-audit。
```

### 从项目安装

需要 Python 3.9 或更新版本，不需要额外 Python 依赖。

```bash
git clone https://github.com/Yisong-Qian/saudi-store-audit.git
cd saudi-store-audit
python3 scripts/skill_manager.py install
```

安装器默认安装到当前用户的 `~/.agents/skills/saudi-store-audit`。Windows 可将 `python3` 换成 `python`。如果已有同名安装，安装器会保留原内容并退出；更新前自行备份原目录，或用 `--destination` 指定另一个技能目录。

安装器只复制公开技能资源，不复制本地配置、报告、截图或凭据。已安装技能未出现在列表时，重启 Codex 后再检查。

## 配置自己的表格

最简单的方式是在首次调用时提供已授权的 Google Sheets URL。也可以把已安装技能中的 `references/store-config.example.json` 复制为同目录的 `store-config.local.json`，填写自己的配置：

```json
{
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit",
  "sheets": {
    "noon": {"title": "Noon"},
    "amazon": {"title": "Amazon"}
  },
  "date_timezone": "Asia/Shanghai",
  "suggested_schedule": {"time": "09:00", "timezone": "Asia/Shanghai"},
  "amazon_delivery_location": "Riyadh, Saudi Arabia"
}
```

优先使用本次明确提供的表格和范围，其次使用技能内的本地配置。没有目标 URL 时先询问。工作表 ID、Status 位置和日期列组均从实时表格读取。

本地配置由 Codex 读取，安装/打包工具不连接表格，也不创建定时任务。仓库忽略 `store-config.local.json`；实际报告与截图建议保存到被忽略的 `reports/`、`screenshots/` 目录。

## 调用

```text
使用 $saudi-store-audit 巡检这份表格：<你的Google Sheets链接>，创建或复用今天的日期列组，保留历史，并分批回写复核。
```

配置好默认表格后，可以直接说：

```text
按沙特巡店SOP完成今日Noon和Amazon巡店，并更新原表。
```

也可以指定只查 Noon、只查 Amazon，或只复查上次失败行。仅安装或阅读技能不会发起巡店。

## 每日自动执行

安装后向 Codex 明确要求创建每日任务，例如“每天北京时间09:00使用这个Skill巡检我的已配置表格”。建议时间对应沙特时间04:00；可以按需要修改。

调度由 Codex 应用管理，配置文件里的建议时刻不会自动启用任务。涉及本机技能和浏览器时，需要电脑与应用保持运行，并保持相关连接可用。详细设置和可复制提示见 [每日自动化](docs/automation.md)。

GitHub Actions 仅校验技能包，不执行实际巡店，不持有你的 Google 授权，也不代替 Codex 定时任务。

## 检查与打包

```bash
python3 scripts/skill_manager.py validate
python3 -m unittest discover -s tests -v
python3 scripts/skill_manager.py package
```

最后一条生成 `dist/saudi-store-audit.zip`。ZIP 仅包含五个公开技能资源，不包含本地配置或仓库测试数据。测试覆盖安装保留已有目录、私有文件排除、相对引用、公开配置和可重复打包。

另有 [19个合成标注场景](docs/acceptance.md) 及预期结果，可用于独立的技能行为验收。常规 CI 不自动证明模型会正确查价，也不代表实际网页或回写已通过验证。

## 项目结构

```text
skills/saudi-store-audit/  可独立安装的技能及参考文件
scripts/skill_manager.py  校验、安装和打包工具
tests/                   工具测试及合成验收样例
docs/                    自动化和行为验收说明
.github/workflows/       安装包自动校验
```

技能中没有内置个人表格链接、账号凭据、会话信息或本机路径。只有已经明确授权的目标表格才能作为巡店回写对象。

参考：[OpenAI技能说明](https://learn.chatgpt.com/docs/build-skills)、[自动化说明](https://learn.chatgpt.com/docs/automations)。
