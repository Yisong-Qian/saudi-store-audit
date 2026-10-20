# 当天列组回写与复核

只写本次实际日期（默认Asia/Shanghai，用户已指定的日期时区优先）对应的唯一列组。历史日期组与基础产品列只读。开始前先读daily-columns.md定位当天组。

## 字段决策

| 本次证据 | 当天MSRP | 当天售价 | 当天buy box | 当天Note |
|---|---|---|---|---|
| 在售，有划线价与售价 | 填本次划线价 | 填主商品数字价 | 按Amazon主体 | 仅实际非平台卖家填sold by名称，否则空白 |
| 在售，完整页面确认无划线价 | 留空 | 填本次售价 | 按实际主体 | 同上 |
| 明确缺货，包括仍残留数字售价 | 可核实划线价或空白 | 文本OOS | 无当前可售报价则0 | 仅实际非平台卖家已核实时填sold by名称，否则空白 |
| Noon显示This product is not available且Status=EOL | 空白 | 空白 | 不适用 | 空白；优先于OOS和卖家规则 |
| Noon显示上述不可用提示但Status无法读取/定位 | 暂不写入 | 暂不写入，不猜OOS | 不适用 | 暂不写入，报告状态核验失败 |
| 无默认报价，购买选项有新品 | 该报价对应划线价或空白 | 最低含运费总价对应的商品价 | 0 | 仅实际非平台卖家填sold by名称 |
| 只有二手报价 | 该报价对应划线价或空白 | 二手当前价 | 无默认报价则0；否则按主体，Amazon Resale=0 | 仅实际非平台卖家填sold by名称；成色记报告 |
| 缺少商品链接 | 新格留空；旧值仅保留为未核实 | 新格留空，不写OOS；旧值仅保留为未核实 | 新格留空；旧值仅保留为未核实 | 留空；当天已确认由巡店生成的旧Note精确清空，人工/公式冲突保留并报告 |
| 访问失败、身份不符、未完成加载 | 新格留空 | 新格留空，不写OOS | 新格留空 | 新格留空，失败行及原因只记报告；同日已有值按归属规则处理 |
| 卖家/发货方无法确认 | 已核实价格可填 | 已核实价格或OOS可填 | 已知一方非Amazon或无可售/默认报价则0，否则新格留空 | 仅非平台卖家已核实时填，否则新格留空，未核实项记报告 |

Noon的Status按字段表头定位，不固定列号；同日回写前重读。EOL留空例外要求同款页面的指定不可用提示和该行EOL状态同时成立，EOL但仍在售的商品正常查价。

Amazon先确认Riyadh；currently unavailable且无当前可售报价才写OOS，购买选项仍有在售报价不能误标。存在默认报价且Shipper / Seller均为Amazon.sa才填1；明确有非Amazon.sa主体或无当前可售报价/默认Buy Box则填0；仍未知不能猜0。

“本次未核实”不能变成0、OOS、确认不存在或历史值。本次生成的Note只允许 `sold by 实际非平台卖家名` 或空白，平台卖家/没有实际卖家信息时不造名称；不写缺货、OOS、失败说明、发货方、运费、成色或日期。上述详细证据和失败原因另存报告。商品价不包含另列运费。

## 同日重跑和人工备注

上述“留空”对本日新组天然成立，不需要清空其他日期的数据。若重跑当天唯一已有组：

- 确认无划线价，可精确清空当天由巡店写入的旧MSRP。确认缺货的售价改为OOS，不因没有数字而清空；恢复有货时将当天OOS替换为本次数字售价。
- Noon指定不可用提示且Status=EOL：当天MSRP、Price、Note均应空白；逐格清理本日巡店自动写入内容，历史和基础列不变。新空格不需清空请求；无法证明归属或遇到人工/公式内容时保留并报告冲突，不能宣称已全部留空。
- 缺链接时，当天Note必须留空：写前重读链接元数据和Note原值；只有GO!文字且无实际URL/超链接/公式链接，或确认为缺少商品链接，并且Note有巡店前缀或与本日自动写入日志精确匹配时，逐格清空该自动Note。保留原值、归属和缺链接证据即可，不要求商品页证据。人工、公式或归属不明的Note保留并报告冲突；不能把自动Note保留规则当成缺链接留空规则的例外。
- 其他查证失败保留本日旧值，在报告标记本次未核实；缺链接行价格/Buy Box也仅保留为未核实。不能把保留值算进新查价或新写入数，不往Note写失败说明。
- 本次卖家核实为平台自营或完整页面确认无卖家信息时，当天Note应空白；已核实非平台卖家则为sold by名称。卖家仅暂未核实不能据此清掉已有卖家Note，保留但在报告标明本次未核实。
- 当天旧“缺货”、OOS备注、长句或失败说明，归属明确且本次证据充分时，清理或替换为本次实际非平台卖家；缺链接清理按上条的链接与归属证据执行。历史Note原样保留，不批量修订旧日期。
- 清理或替换必须有本日前次写入记录、明确巡店前缀等归属证据；不能只因文字恰为“缺货”就推定为自动备注。人工内容、公式与归属不明的值/Note保留，列为冲突。

## 精确单元格操作

依据当天日期组实时计算零基列号，不使用固定F/H/J目标。数字价格和buy box用numberValue，OOS和卖家Note用stringValue，普通数据写入fields只用userEnteredValue；对齐与列宽使用下节独立的精确格式请求。保留售价列原有数字/货币格式，文本OOS仍需读回确认其文本类型与右对齐；验证约束若拒绝文本则报告具体格，不擅自移除验证。

例如某次Noon当天组已定位为L:N：L=MSRP、M=Price、N=Note。该行第3行页面售价89，则只写M3（列索引12）：

```json
{
  "updateCells": {
    "range": {
      "sheetId": 0, "startRowIndex": 2, "endRowIndex": 3,
      "startColumnIndex": 12, "endColumnIndex": 13
    },
    "rows": [{"values": [{"userEnteredValue": {"numberValue": 89}}]}],
    "fields": "userEnteredValue"
  }
}
```

同一位置确认缺货且不属于Noon EOL例外时，M3改用文本，不写数值或Note状态：

```json
{
  "updateCells": {
    "range": {
      "sheetId": 0, "startRowIndex": 2, "endRowIndex": 3,
      "startColumnIndex": 12, "endColumnIndex": 13
    },
    "rows": [{"values": [{"userEnteredValue": {"stringValue": "OOS"}}]}],
    "fields": "userEnteredValue"
  }
}
```

若同日重跑确认本行指定不可用提示且Status=EOL，并已证明M3是当天巡店写入，应记录“M3：原值→空白，EOL例外及归属证据”，再精确清空M3：

```json
{
  "updateCells": {
    "range": {
      "sheetId": 0, "startRowIndex": 2, "endRowIndex": 3,
      "startColumnIndex": 12, "endColumnIndex": 13
    },
    "rows": [{"values": [{}]}],
    "fields": "userEnteredValue"
  }
}
```

这个清空请求没有覆盖L3/N3；EOL例外仍须分别检查并精确处理当天L3/N3，不能因只清空Price就宣称三项均为空。其他日期组不动。只有当天格、归属和页内证据充分且旧值重读一致时才允许清空；新空白格、未知字段或人工内容不执行清空。日期组与行号均是示例，不能直接用作实时批次。

## 当天组显示格式

新建组、同日重跑和失败恢复都执行；实时定位当天列，不把某次运行的G/H/J列号写死。数据类型和格式分别处理：OOS仍是文本，数字售价仍是数值。

1. 对当天Price / Offer Price从首个产品行到本次最后产品行，用repeatCell仅设置userEnteredFormat.horizontalAlignment=RIGHT，fields仅为userEnteredFormat.horizontalAlignment。包括数字、OOS及空白正文；不覆盖字段/日期行、MSRP或buy box，不修改数字格式、字体、底色、边框、验证或值。每批后读回OOS的effectiveFormat.horizontalAlignment应为RIGHT；轮次结束复核整个售价正文。
2. 对当天Note从首个产品行到本次最后产品行，用repeatCell仅设置userEnteredFormat.textDirection=LEFT_TO_RIGHT、userEnteredFormat.horizontalAlignment=LEFT，fields仅为userEnteredFormat.textDirection,userEnteredFormat.horizontalAlignment。新建、复用及同日重跑均执行，包括空白正文，不覆盖Note表头、日期行或其他列。所有备注以英文前缀sold by开始，店铺原名随后显示；阿语店名内部保持自然阿语阅读顺序。保留字符串原文，不翻译、不反转店名字母/单词、不插入LRM/RLM或其他隐藏方向控制字符，不把整表改成从左到右。
3. 每轮回写结束、旧自动Note清理完成后，检查当天Note正文。存在文字时保持单行，若已有WRAP则只对当天Note正文把wrapStrategy改为OVERFLOW_CELL，fields只用userEnteredFormat.wrapStrategy；先完成上述Note方向/左对齐，再对该一个Note列使用autoResizeDimensions，按完整卖家名适配。保留字号、行高和字符串，不改为省略号、不靠溢出到邻列显示。
4. 当天Note正文全空时不自动缩窄：复用组保留现有宽度，新组沿用模板宽度。历史Note列和其他列不参与自动列宽，也不整表autofit。日期合并范围与表头样式不变。
5. 数值请求、售价水平对齐请求、Note方向/左对齐请求、单行显示请求和单列列宽请求分别记录；复核允许变化仅为这些字段和目标范围。列宽/格式修复不得计为新增网页核验或新查价。Google Sheets正常缩放下检查OOS、最长英文Note、阿拉伯文Note及相邻列，确认sold by在左且店名随后完整单行可见。

例如当天Noon组已定位为L:N，产品行3至55，仅统一Price正文的右对齐：

```json
{
  "repeatCell": {
    "range": {"sheetId": 0, "startRowIndex": 2, "endRowIndex": 55, "startColumnIndex": 12, "endColumnIndex": 13},
    "cell": {"userEnteredFormat": {"horizontalAlignment": "RIGHT"}},
    "fields": "userEnteredFormat.horizontalAlignment"
  }
}
```

同组Note=N，先统一Note正文的方向和左对齐：

```json
{
  "repeatCell": {
    "range": {"sheetId": 0, "startRowIndex": 2, "endRowIndex": 55, "startColumnIndex": 13, "endColumnIndex": 14},
    "cell": {"userEnteredFormat": {"textDirection": "LEFT_TO_RIGHT", "horizontalAlignment": "LEFT"}},
    "fields": "userEnteredFormat.textDirection,userEnteredFormat.horizontalAlignment"
  }
}
```

Note=N且正文有内容时，单列适配请求为：

```json
{
  "autoResizeDimensions": {
    "dimensions": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 13, "endIndex": 14}
  }
}
```

示例行列均须用实时当天组替换。自动列宽返回成功仍要检查实际渲染，不能据此宣称文字一定适配。

## 批次闭环

1. 创建或复用当天组并读回复核日期与字段，保存所有历史组和基础列基线。
2. 对每个产品保存原始/实际URL、编号、页内证据、价格显示状态、库存、seller/shipper、成色、运费和时间；Noon另存Status表头位置、行状态及EOL例外依据。
3. 5–15行一批，写前重读日期、行身份、Noon的Status和目标旧值，防止列组移动、换链接、状态变更或并发覆盖。
4. 写后逐格读回数字、文本OOS、空白及卖家Note，检查OOS与数字售价右对齐、Note从左到右/左对齐且视觉上sold by先于店名、缺链接自动Note留空及EOL行三项留空是否成立。返回成功标志不能替代数据复核；结果不明先读回再补写，不盲目重试整批。
5. 对比历史组与基础列仍一致，格式变化仅限新组创建及当天售价正文右对齐、Note从左到右、左对齐和单行显示；列宽变化仅限有内容的当天Note列。轮次结束完成单列自动适配与实际显示复核，核对未把昨日值复制到当天。
6. 分开统计新增/复用列组、完整页面核验、EOL跳过、部分字段核验、实际写入及复核成功、普通OOS缺货、缺链接、失败和人工冲突；EOL自动清理格数另报，EOL不混入普通OOS/失败数。没有变化可报告“已核验，无需改值”，不能虚增写入数。

逐行记录包含run_date/timezone、当天组范围、sheetId/row/product_id、original_url/observed_url、checked_at、字段present/absent/unknown、stock_status、Noon Status及EOL例外、before/after、归属、写入和复核状态。详细记录和失败行只进巡店记录/报告，Note仅用于实际非平台卖家。
