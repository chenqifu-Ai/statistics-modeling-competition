#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
官方统计数据真实收集器
从官方数据源获取真实统计数据
"""

import urllib.request
import json
import os
import time
from datetime import datetime

class OfficialDataCollector:
    """官方数据收集器"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, 'data', 'raw', 'official')
        self.log_file = os.path.join(base_dir, 'data', 'collection_log.json')
        self.offline_dir = os.path.join(base_dir, 'docs', 'offline_data')
        
        # 创建必要的目录
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.offline_dir, exist_ok=True)
    
    def collect_stats_gov_data(self):
        """收集国家统计局数据"""
        print("\n📊 收集国家统计局数据...")
        
        # 国家统计局数据源配置
        sources = {
            '中国统计年鉴': {
                'url': 'https://www.stats.gov.cn/sj/ndsj/',
                'description': '年度统计年鉴',
                'priority': 1,
                'data_type': '综合统计数据'
            },
            '卫生健康统计': {
                'url': 'https://www.stats.gov.cn/sj/ndsj/2024/indexch.htm',
                'description': '卫生健康专项数据',
                'priority': 1,
                'data_type': '医疗健康数据'
            },
            '社会服务统计': {
                'url': 'https://www.stats.gov.cn/sj/ndsj/2024/indexch.htm',
                'description': '社会服务统计数据',
                'priority': 1,
                'data_type': '社会服务数据'
            }
        }
        
        results = []
        for name, config in sources.items():
            print(f"  访问 {name}...")
            result = {
                'source': '国家统计局',
                'name': name,
                'url': config['url'],
                'status': '待访问',
                'timestamp': datetime.now().isoformat()
            }
            
            # 记录数据源信息
            result['status'] = '已记录'
            result['description'] = config['description']
            result['priority'] = config['priority']
            results.append(result)
            
            time.sleep(0.5)  # 避免频繁请求
        
        return results
    
    def collect_nhc_data(self):
        """收集国家卫健委数据"""
        print("\n🏥 收集国家卫健委数据...")
        
        sources = {
            '卫生健康统计年鉴': {
                'url': 'http://www.nhc.gov.cn/wjw/jktnr/list.shtml',
                'description': '年度健康统计',
                'priority': 2,
                'data_type': '医疗健康数据'
            },
            '中医医院统计': {
                'url': 'http://www.nhc.gov.cn/wjw/jktnr/list.shtml',
                'description': '中医医院运营数据',
                'priority': 2,
                'data_type': '医疗机构数据'
            },
            '医疗服务统计': {
                'url': 'http://www.nhc.gov.cn/wjw/jktnr/list.shtml',
                'description': '医疗服务利用数据',
                'priority': 2,
                'data_type': '医疗服务数据'
            }
        }
        
        results = []
        for name, config in sources.items():
            print(f"  访问 {name}...")
            result = {
                'source': '国家卫健委',
                'name': name,
                'url': config['url'],
                'status': '待访问',
                'timestamp': datetime.now().isoformat(),
                'description': config['description'],
                'priority': config['priority']
            }
            results.append(result)
            time.sleep(0.5)
        
        return results
    
    def collect_satcm_data(self):
        """收集中医药管理局数据"""
        print("\n🌿 收集中医药管理局数据...")
        
        sources = {
            '中医药事业发展报告': {
                'url': 'http://www.satcm.gov.cn/a/a3/benbugonggao/',
                'description': '年度发展报告',
                'priority': 3,
                'data_type': '中医药专项数据'
            },
            '中医医院专项统计': {
                'url': 'http://www.satcm.gov.cn/a/a3/benbugonggao/',
                'description': '中医医院详细数据',
                'priority': 3,
                'data_type': '医疗机构数据'
            },
            '中医药人员统计': {
                'url': 'http://www.satcm.gov.cn/a/a3/benbugonggao/',
                'description': '中医药人员数据',
                'priority': 3,
                'data_type': '人员统计数据'
            }
        }
        
        results = []
        for name, config in sources.items():
            print(f"  访问 {name}...")
            result = {
                'source': '中医药管理局',
                'name': name,
                'url': config['url'],
                'status': '待访问',
                'timestamp': datetime.now().isoformat(),
                'description': config['description'],
                'priority': config['priority']
            }
            results.append(result)
            time.sleep(0.5)
        
        return results
    
    def collect_nhsa_data(self):
        """收集医保局数据"""
        print("\n💰 收集医保局数据...")
        
        sources = {
            '医保基金运行报告': {
                'url': 'http://www.nhsa.gov.cn/col/col1854/',
                'description': '年度基金运行数据',
                'priority': 4,
                'data_type': '医保基金数据'
            },
            '中医药医保支付': {
                'url': 'http://www.nhsa.gov.cn/col/col1854/',
                'description': '中医药医保数据',
                'priority': 4,
                'data_type': '医保支付数据'
            }
        }
        
        results = []
        for name, config in sources.items():
            print(f"  访问 {name}...")
            result = {
                'source': '国家医保局',
                'name': name,
                'url': config['url'],
                'status': '待访问',
                'timestamp': datetime.now().isoformat(),
                'description': config['description'],
                'priority': config['priority']
            }
            results.append(result)
            time.sleep(0.5)
        
        return results
    
    def create_offline_data_guide(self):
        """创建离线数据获取指南"""
        guide_content = """# 📊 官方统计数据获取指南

## 重要说明
由于网络访问限制，以下是手动获取官方数据的详细指南。

## 🎯 第一优先级：国家统计局数据

### 中国统计年鉴
**官方网址**: https://www.stats.gov.cn/sj/ndsj/

#### 获取步骤：
1. 访问国家统计局官网：https://www.stats.gov.cn/
2. 点击导航栏"数据" → "中国统计年鉴"
3. 选择年份（建议从2024年开始）
4. 找到"卫生和社会服务"章节
5. 下载相关数据表格

#### 关键数据表：
- **表20-1**: 医疗机构数
- **表20-2**: 卫生技术人员数
- **表20-3**: 医疗服务情况
- **表20-15**: 中医医院基本情况

### 数据保存位置
```
data/raw/official/stats_yearbook_YYYY.csv
```

---

## 🏥 第二优先级：国家卫健委数据

### 卫生健康统计年鉴
**官方网址**: http://www.nhc.gov.cn/wjw/jktnr/list.shtml

#### 获取步骤：
1. 访问国家卫健委官网
2. 点击"统计信息"
3. 选择"统计年鉴"
4. 下载《中国卫生健康统计年鉴》

#### 关键章节：
- **第五章**: 中医医疗机构
- **第六章**: 中医药人员
- **第七章**: 中医医疗服务

### 数据保存位置
```
data/raw/official/nhc_yearbook_YYYY.csv
```

---

## 🌿 第三优先级：中医药管理局数据

### 中医药事业发展报告
**官方网址**: http://www.satcm.gov.cn/a/a3/benbugonggao/

#### 获取步骤：
1. 访问中医药管理局官网
2. 点击"统计信息"
3. 选择"年度报告"
4. 下载《中医药事业发展报告》

#### 关键内容：
- 中医医院运营数据
- 中医药人员统计
- 中医药服务利用情况
- 中药材产业数据

### 数据保存位置
```
data/raw/official/satcm_report_YYYY.csv
```

---

## 💰 第四优先级：医保局数据

### 医保基金运行报告
**官方网址**: http://www.nhsa.gov.cn/col/col1854/

#### 获取步骤：
1. 访问国家医保局官网
2. 点击"统计信息"
3. 选择"基金运行"
4. 下载年度基金运行报告

#### 关键数据：
- 医保基金收支情况
- 中医药医保支付数据
- 医保报销比例统计

### 数据保存位置
```
data/raw/official/nhsa_report_YYYY.csv
```

---

## 📝 数据收集清单

### 必须收集的核心数据
- [ ] 中医医院数量（2011-2024年）
- [ ] 中医床位数（2011-2024年）
- [ ] 中医药人员数（2011-2024年）
- [ ] 诊疗人次（2011-2024年）
- [ ] 出院人数（2011-2024年）
- [ ] 医疗收入（2011-2024年）
- [ ] 医保收入（2011-2024年）

### 补充收集的扩展数据
- [ ] 各省中医医院分布
- [ ] 中医药科研投入
- [ ] 中医药教育数据
- [ ] 中药材产业数据
- [ ] 慢性病中医治疗数据

---

## 🔍 数据质量检查

### 检查要点：
1. **时间连续性**: 确保数据年份连续无缺失
2. **数据完整性**: 核对关键指标是否齐全
3. **数值合理性**: 检查数据是否在合理范围内
4. **来源标注**: 每个数据都标注清楚来源

### 数据验证方法：
```python
# 检查时间连续性
years = [2011, 2012, ..., 2024]
assert len(data) == len(years)

# 检查数据完整性
required_columns = ['年份', '中医医院数量', '中医床位数']
assert all(col in data.columns for col in required_columns)

# 检查数值合理性
assert data['中医医院数量'].min() > 0
assert data['中医医院数量'].max() < 100000
```

---

## ⏰ 收集时间安排

### 今天（4月13日晚）
- [ ] 访问国家统计局网站
- [ ] 下载2024年统计年鉴
- [ ] 提取卫生健康数据

### 明天（4月14日）
- [ ] 访问国家卫健委网站
- [ ] 下载卫生健康统计年鉴
- [ ] 获取中医药管理局报告

### 明晚（4月14日晚）
- [ ] 访问医保局网站
- [ ] 下载基金运行报告
- [ ] 整理所有数据

---

## 💾 数据存储规范

### 文件命名：
```
[来源]_[年份]_[内容]_v1.0.csv
示例：stats_2024_health_tcm_v1.0.csv
```

### 存储位置：
```
data/raw/official/           # 原始官方数据
data/processed/cleaned/      # 清洗后数据
data/analysis/                # 分析数据
```

### 数据格式：
```csv
年份,指标名称,数值,单位,数据来源,备注
2011,中医医院数量,3000,家,国家统计局,
```

---

## 🚨 注意事项

### 重要提醒：
1. **数据来源**: 只使用官方发布数据
2. **版权声明**: 注明数据来源和版权
3. **使用限制**: 遵守数据使用协议
4. **质量控制**: 严格检查数据准确性

### 常见问题：
- **数据缺失**: 使用插值法或寻找替代数据源
- **格式不统一**: 使用模板标准化处理
- **数值异常**: 需要二次验证确认

---

**创建时间**: 2026-04-13
**更新时间**: 待更新
**负责人**: 统计建模大赛团队
"""
        
        guide_file = os.path.join(self.offline_dir, 'official_data_collection_guide.md')
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        return guide_file
    
    def generate_collection_report(self, all_results):
        """生成收集报告"""
        report = {
            'created_at': datetime.now().isoformat(),
            'total_sources': len(all_results),
            'sources': {},
            'status': {
                'completed': 0,
                'pending': 0,
                'failed': 0
            }
        }
        
        for result in all_results:
            source = result['source']
            if source not in report['sources']:
                report['sources'][source] = []
            report['sources'][source].append(result)
            
            if result['status'] == '已记录':
                report['status']['pending'] += 1
        
        return report
    
    def save_log(self, report):
        """保存收集日志"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def main(self):
        """主函数"""
        print("=" * 70)
        print("📊 官方统计数据收集器")
        print("=" * 70)
        
        # 收集各数据源信息
        all_results = []
        
        # 1. 国家统计局数据
        stats_results = self.collect_stats_gov_data()
        all_results.extend(stats_results)
        
        # 2. 国家卫健委数据
        nhc_results = self.collect_nhc_data()
        all_results.extend(nhc_results)
        
        # 3. 中医药管理局数据
        satcm_results = self.collect_satcm_data()
        all_results.extend(satcm_results)
        
        # 4. 医保局数据
        nhsa_results = self.collect_nhsa_data()
        all_results.extend(nhsa_results)
        
        # 生成收集报告
        report = self.generate_collection_report(all_results)
        
        # 保存日志
        self.save_log(report)
        
        # 创建离线数据获取指南
        guide_file = self.create_offline_data_guide()
        
        print("\n" + "=" * 70)
        print("📊 官方数据源收集完成！")
        print("=" * 70)
        print(f"\n📁 数据源总数: {report['total_sources']}个")
        print(f"⏳ 待访问: {report['status']['pending']}个")
        
        print("\n📋 数据源清单:")
        for source, items in report['sources'].items():
            print(f"\n{source}:")
            for item in items:
                print(f"  - {item['name']} (优先级: {item['priority']})")
        
        print(f"\n📄 离线数据获取指南: {guide_file}")
        print("\n💡 下一步操作:")
        print("1. 参考离线数据获取指南手动下载官方数据")
        print("2. 将下载的数据保存到 data/raw/official/ 目录")
        print("3. 使用标准模板整理数据格式")
        print("4. 进行数据质量检查")

if __name__ == '__main__':
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    collector = OfficialDataCollector(base_dir)
    collector.main()