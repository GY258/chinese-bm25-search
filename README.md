# 🇨🇳 中文BM25文档检索服务

专为中文文档优化的BM25检索系统，使用jieba分词和HMM算法，为您的来菜餐厅文档提供智能搜索功能。

## 🎯 功能特点

- **🔍 智能中文分词**: 使用jieba + HMM算法，精确处理中文文本
- **📊 BM25算法**: 针对中文特点优化的评分参数 (k1=1.5, b=0.6)
- **🚀 高性能搜索**: 平均文档长度703词，词汇量2,111个
- **📱 多种接口**: 命令行工具、API服务、CLI管理工具
- **🎨 中文优化**: 109个中文停用词，支持词性标注过滤

## 📊 已索引文档

您的来菜餐厅文档已成功索引：
- **15秒火爆猪肝SOP20241228.txt** - 猪肝制作标准
- **BJSZ橄榄油炒六种超级食物SOP20250603.txt** - 健康菜品制作
- **BJSZ藕粉甜酒汤圆sop20250605.txt** - 汤圆制作工艺
- **儿童套餐SOP20241230.txt** - 儿童餐标准
- **利川蒜香凤爪 20250415.txt** - 凤爪制作方法
- **来菜人事制度20250612.txt** - 人事管理制度
- **来菜消防安全、人身安全标准（杨）.txt** - 安全标准
- **桂花发糕sop20241203.txt** - 发糕制作工艺
- **汽水肉蒸蛋SOP20250415.txt** - 蒸蛋制作标准
- **铫子筒骨煨藕汤产品标准.txt** - 汤品制作标准

## 🚀 快速开始

### 1. 简单搜索（推荐）
```bash
# 搜索菜品制作方法
python search.py "猪肝"

# 搜索儿童餐相关
python search.py "儿童套餐" 3

# 搜索安全标准
python search.py "安全标准"

# 搜索汤品制作
python search.py "汤圆"
```

### 2. 命令行工具
```bash
# 搜索文档
python chinese_cli.py search "人事制度" --limit 5 --snippets

# 查看词汇统计
python chinese_cli.py term-stats "安全"

# 查看系统统计
python chinese_cli.py stats

# 查找相似文档
python chinese_cli.py similar 0 --limit 3

# 分析查询词
python chinese_cli.py analyze "猪肝制作"
```

### 3. API服务
```bash
# 启动API服务
python test_service.py

# 然后在浏览器访问：
# http://localhost:5002/
# http://localhost:5002/search?query=猪肝&limit=3
# http://localhost:5002/health
```

## 📋 搜索示例

### 菜品制作相关
```bash
python search.py "猪肝制作"      # 火爆猪肝制作方法
python search.py "汤圆做法"      # 藕粉甜酒汤圆制作
python search.py "凤爪"          # 蒜香凤爪制作
python search.py "蒸蛋"          # 汽水肉蒸蛋制作
```

### 管理制度相关
```bash
python search.py "人事制度"      # 员工管理制度
python search.py "安全标准"      # 消防和人身安全
python search.py "产品标准"      # 各类产品制作标准
```

### 特色菜品相关
```bash
python search.py "儿童"          # 儿童套餐相关
python search.py "超级食物"      # 健康菜品制作
python search.py "发糕"          # 桂花发糕制作
```

## 🔧 技术特点

### 中文处理优化
- **分词算法**: jieba精确模式 + HMM
- **词性过滤**: 保留名词、动词、形容词等有意义词汇
- **停用词**: 109个中文常用停用词
- **编码支持**: UTF-8, GBK, GB2312, Big5

### BM25参数优化
- **K1=1.5**: 适合中文词频特点
- **B=0.6**: 较低的文档长度惩罚
- **自定义词典**: 从文档中自动提取585个专业术语

### 性能统计
- **文档数量**: 10个餐厅标准文档
- **总字符数**: 22,904个中文字符
- **词汇量**: 2,111个唯一词汇
- **平均文档长度**: 703.7个词

## 📁 文件结构

```
chinese_bm25_retrieval/
├── search.py                 # 🔍 简单搜索工具（推荐）
├── chinese_cli.py           # 📋 完整CLI工具
├── test_service.py          # 🚀 API服务
├── chinese_processor.py     # 🔧 中文文档处理器
├── chinese_bm25_search.py   # 🎯 BM25搜索引擎
├── config.py                # ⚙️ 配置文件
├── requirements.txt         # 📦 依赖包
├── run_chinese_service.sh   # 🚀 服务启动脚本
├── README.md               # 📖 使用说明
└── chinese_index/          # 💾 索引文件目录
    ├── chinese_documents.json
    ├── chinese_inverted_index.pkl
    └── custom_dict.txt
```

## 🎮 使用技巧

### 1. 搜索技巧
- 使用具体的菜品名：`"猪肝"` 比 `"肉类"` 更精确
- 组合关键词：`"儿童 营养"` 搜索儿童营养相关
- 工艺术语：`"SOP"`, `"标准"`, `"制作"`

### 2. 高级功能
```bash
# 查看某个词在哪些文档中出现
python chinese_cli.py term-stats "制作"

# 查找与某个文档相似的其他文档
python chinese_cli.py similar 0

# 分析复杂查询
python chinese_cli.py analyze "儿童营养套餐制作标准"
```

### 3. API使用
```bash
# 健康检查
curl http://localhost:5002/health

# 搜索API
curl "http://localhost:5002/search?query=猪肝&limit=2"

# 查看API文档
curl http://localhost:5002/
```

## 🔍 搜索质量

基于BM25算法的评分系统：
- **高相关性** (>5.0分): 直接匹配核心词汇
- **中等相关性** (2.0-5.0分): 部分匹配或相关词汇
- **低相关性** (<2.0分): 间接相关

示例搜索结果评分：
- `"儿童套餐"` → 6.81分 (高)
- `"猪肝"` → 4.27分 (中)
- `"安全标准"` → 4.04分 (中)

## 🛠️ 维护和扩展

### 添加新文档
1. 将新的.txt文档放入 `/Users/yuanan/Downloads/laicai_document/`
2. 运行 `python chinese_cli.py build-index` 重建索引

### 优化搜索
- 编辑 `config.py` 调整BM25参数
- 修改 `chinese_processor.py` 中的停用词列表
- 添加专业术语到自定义词典

## 📈 性能监控

查看详细统计信息：
```bash
python chinese_cli.py stats
```

输出包括：
- 文档数量和词汇分布
- 最常见词汇TOP10
- 文档长度分布统计
- BM25参数设置

---

**🎉 您的中文BM25检索服务已成功部署！**

现在您可以快速搜索来菜餐厅的所有标准文档，包括菜品制作SOP、安全标准、人事制度等内容。
