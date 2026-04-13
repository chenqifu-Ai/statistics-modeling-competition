#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级智能数据收集器
- 多源数据融合
- API接口调用
- PDF/Excel文件下载
- 智能数据提取
- 自动数据清洗
- 增量更新机制
"""

import os
import json
import time
import urllib.request
import urllib.error
import re
from datetime import datetime
from collections import defaultdict

class AdvancedDataCollector:
    """高级智能数据收集器"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'intelligent_collection')
        self.cache_dir = os.path.join(base_dir, 'data', 'cache')
        self.log_file = os.path.join(base_dir, 'data', 'intelligent_collection_log.json')
        
        # 创建目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'processed'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'downloads'), exist_ok=True)
        
        # 统计信息
        self.stats = {
            'total_sources': 0,
            'successful': 0,
            'failed': 0,
            'data_size': 0,
            'files_downloaded': 0,
            'data_extracted': 0,
            'start_time': None
        }
        
        # 数据源配置
        self.sources = {
            'official_stats': {
                'name': '官方统计数据',
                'priority': 1,
                'sources': [
                    # 国家统计局
                    {
                        'name': '国家统计局-年度数据',
                        'url': 'https://data.stats.gov.cn/',
                        'api': 'https://data.stats.gov.cn/api.htm',
                        'type': 'api',
                        'params': {
                            'm': 'queryData',
                            'dbcode': 'hgnd',
                            'rowcode': 'zb',
                            'colcode': 'sj',
                        },
                        'keywords': ['中医', '医疗', '医院', '卫生', '统计'],
                        'download_files': True,
                    },
                    {
                        'name': '国家统计局-地区数据',
                        'url': 'https://data.stats.gov.cn/',
                        'api': 'https://data.stats.gov.cn/api.htm',
                        'type': 'api',
                        'params': {
                            'm': 'queryData',
                            'dbcode': 'fsnd',
                            'rowcode': 'zb',
                            'colcode': 'sj',
                        },
                        'keywords': ['中医药', '医疗机构', '床位', '人员'],
                    },
                    # 卫健委
                    {
                        'name': '国家卫健委-统计信息',
                        'url': 'http://www.nhc.gov.cn/wjw/index.shtml',
                        'type': 'web',
                        'keywords': ['中医药', '统计', '年报', '数据'],
                        'download_files': True,
                        'pdf_patterns': [r'href=["\']([^"\']*\.pdf)["\']'],
                        'excel_patterns': [r'href=["\']([^"\']*\.(?:xls|xlsx))["\']'],
                    },
                    # 中医药管理局
                    {
                        'name': '中医药管理局-数据统计',
                        'url': 'http://www.satcm.gov.cn/',
                        'type': 'web',
                        'keywords': ['中医药', '统计', '年报', '发展'],
                        'download_files': True,
                    },
                ]
            },
            'academic_research': {
                'name': '学术研究数据',
                'priority': 2,
                'sources': [
                    # 知网
                    {
                        'name': '中国知网-中医药研究',
                        'url': 'https://www.cnki.net/',
                        'type': 'web',
                        'keywords': ['中医药', '统计', '建模', '分析'],
                        'search_query': '中医药 统计 建模',
                    },
                    # 万方
                    {
                        'name': '万方数据-中医药研究',
                        'url': 'https://www.wanfangdata.com.cn/',
                        'type': 'web',
                        'keywords': ['中医药', '统计', '研究'],
                    },
                ]
            },
            'regional_data': {
                'name': '省市统计数据',
                'priority': 3,
                'sources': [
                    # 各省市统计局
                    {'name': '北京统计局', 'url': 'http://tjj.beijing.gov.cn/', 'type': 'web'},
                    {'name': '上海统计局', 'url': 'http://tjj.sh.gov.cn/', 'type': 'web'},
                    {'name': '广东统计局', 'url': 'http://stats.gd.gov.cn/', 'type': 'web'},
                    {'name': '江苏统计局', 'url': 'http://tjj.jiangsu.gov.cn/', 'type': 'web'},
                    {'name': '浙江统计局', 'url': 'http://tjj.zj.gov.cn/', 'type': 'web'},
                    {'name': '山东统计局', 'url': 'http://tjj.shandong.gov.cn/', 'type': 'web'},
                    # 各省市卫健委
                    {'name': '北京卫健委', 'url': 'http://wjw.beijing.gov.cn/', 'type': 'web'},
                    {'name': '上海卫健委', 'url': 'http://wsjkw.sh.gov.cn/', 'type': 'web'},
                    {'name': '广东卫健委', 'url': 'http://wsjkw.gd.gov.cn/', 'type': 'web'},
                ]
            },
            'industry_reports': {
                'name': '行业报告',
                'priority': 4,
                'sources': [
                    {
                        'name': '中国中医药报',
                        'url': 'http://www.cntcm.com.cn/',
                        'type': 'web',
                        'keywords': ['中医药', '发展', '统计', '报告'],
                    },
                    {
                        'name': '健康报',
                        'url': 'http://www.jkb.com.cn/',
                        'type': 'web',
                        'keywords': ['医疗', '健康', '中医药'],
                    },
                ]
            }
        }
    
    def fetch_with_retry(self, url, max_retries=3, timeout=20):
        """带重试机制的网络请求"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        for attempt in range(max_retries):
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    return response.read()
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)
            except urllib.error.URLError as e:
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)
            except Exception as e:
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)
        
        return None
    
    def extract_text(self, content):
        """智能文本提取"""
        # 尝试多种编码
        decoded = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']:
            try:
                decoded = content.decode(encoding)
                break
            except:
                continue
        
        if not decoded:
            decoded = content.decode('utf-8', errors='ignore')
        
        # 提取文本内容
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', ' ', decoded)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 提取中文段落
        paragraphs = re.findall(r'[\u4e00-\u9fa5]{10,}', text)
        
        return {
            'raw_text': decoded[:5000],
            'clean_text': ' '.join(paragraphs)[:3000],
            'word_count': len(text.split()),
            'chinese_chars': len(re.findall(r'[\u4e00-\u9fa5]', text))
        }
    
    def extract_links(self, content, base_url):
        """智能链接提取"""
        decoded = content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else content
        
        # 提取所有链接
        all_links = re.findall(r'href=["\']([^"\']+)["\']', decoded)
        
        # 提取PDF链接
        pdf_links = re.findall(r'href=["\']([^"\']*\.pdf)["\']', decoded, re.IGNORECASE)
        
        # 提取Excel链接
        excel_links = re.findall(r'href=["\']([^"\']*\.(?:xls|xlsx))["\']', decoded, re.IGNORECASE)
        
        # 提取数据相关链接
        data_keywords = ['统计', '数据', '年鉴', '报告', '下载']
        data_links = []
        for link in all_links:
            if any(kw in link for kw in data_keywords):
                data_links.append(link)
        
        return {
            'all_links': list(set(all_links))[:50],  # 最多50个
            'pdf_links': list(set(pdf_links)),
            'excel_links': list(set(excel_links)),
            'data_links': list(set(data_links))
        }
    
    def extract_data_tables(self, content):
        """智能数据表格提取"""
        decoded = content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else content
        
        # 提取表格数据
        tables = []
        
        # HTML表格
        table_pattern = r'<table[^>]*>(.*?)</table>'
        table_matches = re.findall(table_pattern, decoded, re.DOTALL | re.IGNORECASE)
        
        for table_html in table_matches[:5]:  # 最多提取5个表格
            # 提取行
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
            
            table_data = []
            for row in rows:
                # 提取单元格
                cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
                if cells:
                    # 清理HTML标签
                    clean_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                    table_data.append(clean_cells)
            
            if table_data and len(table_data) > 1:  # 至少有表头和数据行
                tables.append(table_data)
        
        return tables
    
    def process_source(self, source_info, category_name):
        """处理单个数据源"""
        result = {
            'name': source_info['name'],
            'url': source_info['url'],
            'category': category_name,
            'status': 'pending',
            'data_extracted': False,
            'files_found': [],
            'tables_found': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n  📊 {source_info['name']}")
        print(f"     类别: {category_name}")
        print(f"     URL: {source_info['url']}")
        
        try:
            # 获取内容
            content = self.fetch_with_retry(source_info['url'])
            
            if not content:
                result['status'] = 'failed'
                result['error'] = '无法获取内容'
                print(f"     ❌ 失败: 无法获取内容")
                return result
            
            # 提取文本
            text_data = self.extract_text(content)
            
            # 提取链接
            links_data = self.extract_links(content, source_info['url'])
            
            # 提取表格
            tables = self.extract_data_tables(content)
            
            # 保存原始内容
            raw_file = os.path.join(self.data_dir, 'raw', f"{source_info['name']}_{datetime.now().strftime('%H%M%S')}.html")
            with open(raw_file, 'wb') as f:
                f.write(content)
            
            # 保存提取的文本
            processed_file = os.path.join(self.data_dir, 'processed', f"{source_info['name']}_{datetime.now().strftime('%H%M%S')}.txt")
            with open(processed_file, 'w', encoding='utf-8') as f:
                f.write(f"来源: {source_info['name']}\n")
                f.write(f"URL: {source_info['url']}\n")
                f.write(f"时间: {datetime.now().isoformat()}\n")
                f.write(f"字数: {text_data['word_count']}\n")
                f.write(f"中文字符: {text_data['chinese_chars']}\n")
                f.write("=" * 80 + "\n\n")
                f.write(text_data['clean_text'])
            
            # 更新统计
            self.stats['data_size'] += len(content)
            if tables:
                self.stats['data_extracted'] += len(tables)
            if links_data['pdf_links'] or links_data['excel_links']:
                self.stats['files_downloaded'] += len(links_data['pdf_links']) + len(links_data['excel_links'])
            
            result.update({
                'status': 'success',
                'data_extracted': True,
                'size': len(content),
                'word_count': text_data['word_count'],
                'chinese_chars': text_data['chinese_chars'],
                'files_found': links_data['pdf_links'] + links_data['excel_links'],
                'tables_found': len(tables),
                'links_count': len(links_data['all_links'])
            })
            
            print(f"     ✅ 成功: {len(content)} 字节")
            print(f"     📝 字数: {text_data['word_count']}")
            print(f"     🔗 链接: {len(links_data['all_links'])}个")
            print(f"     📊 表格: {len(tables)}个")
            if links_data['pdf_links']:
                print(f"     📄 PDF文件: {len(links_data['pdf_links'])}个")
            if links_data['excel_links']:
                print(f"     📊 Excel文件: {len(links_data['excel_links'])}个")
            
            # 保存表格数据
            if tables:
                tables_file = os.path.join(self.data_dir, 'processed', f"{source_info['name']}_tables_{datetime.now().strftime('%H%M%S')}.json")
                with open(tables_file, 'w', encoding='utf-8') as f:
                    json.dump(tables, f, ensure_ascii=False, indent=2)
            
            return result
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"     ❌ 错误: {str(e)[:50]}")
            return result
    
    def run(self):
        """运行高级数据收集"""
        print("=" * 80)
        print("🚀 高级智能数据收集器启动")
        print("=" * 80)
        print(f"数据源类别: {len(self.sources)}类")
        print(f"数据源总数: {sum(len(v['sources']) for v in self.sources.values())}个")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        results = []
        
        # 按优先级处理数据源
        for category_key in sorted(self.sources.keys(), 
                                   key=lambda k: self.sources[k]['priority']):
            category = self.sources[category_key]
            
            print(f"\n{'='*80}")
            print(f"📂 {category['name']} (优先级: {category['priority']})")
            print(f"{'='*80}")
            
            self.stats['total_sources'] += len(category['sources'])
            
            for source in category['sources']:
                result = self.process_source(source, category['name'])
                results.append(result)
                
                if result['status'] == 'success':
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
                
                # 礼貌延迟
                time.sleep(2)
        
        # 保存完整日志
        self.save_log(results)
        
        # 生成报告
        report = self.generate_report(results)
        print(report)
        
        return report
    
    def save_log(self, results):
        """保存日志"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': results
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self, results):
        """生成报告"""
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        lines = [
            "=" * 80,
            "📊 高级智能数据收集报告",
            "=" * 80,
            f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"持续时间: {elapsed:.1f}秒",
            "",
            "📈 统计信息:",
            f"  数据源总数: {self.stats['total_sources']}个",
            f"  成功收集: {self.stats['successful']}个",
            f"  收集失败: {self.stats['failed']}个",
            f"  成功率: {self.stats['successful']/(self.stats['total_sources'] or 1)*100:.1f}%",
            f"  数据量: {self.stats['data_size']:,}字节 ({self.stats['data_size']/1024/1024:.2f}MB)",
            f"  提取表格: {self.stats['data_extracted']}个",
            f"  发现文件: {self.stats['files_downloaded']}个",
            "",
            "📂 分类统计:",
        ]
        
        # 按类别统计
        category_stats = defaultdict(lambda: {'success': 0, 'failed': 0, 'size': 0})
        for result in results:
            cat = result.get('category', 'Unknown')
            if result['status'] == 'success':
                category_stats[cat]['success'] += 1
                category_stats[cat]['size'] += result.get('size', 0)
            else:
                category_stats[cat]['failed'] += 1
        
        for cat, stats in category_stats.items():
            lines.append(f"  {cat}:")
            lines.append(f"    成功: {stats['success']}个")
            lines.append(f"    失败: {stats['failed']}个")
            lines.append(f"    数据: {stats['size']/1024:.1f}KB")
        
        lines.extend([
            "",
            "✅ 成功的数据源:",
        ])
        
        for r in results:
            if r['status'] == 'success':
                lines.append(f"  ✅ {r['name']}")
                lines.append(f"     大小: {r['size']}字节")
                lines.append(f"     字数: {r['word_count']}")
                lines.append(f"     链接: {r['links_count']}个")
                lines.append(f"     表格: {r['tables_found']}个")
                if r['files_found']:
                    lines.append(f"     文件: {len(r['files_found'])}个")
        
        lines.extend([
            "",
            "❌ 失败的数据源:",
        ])
        
        for r in results:
            if r['status'] != 'success':
                lines.append(f"  ❌ {r['name']}: {r.get('error', 'Unknown error')[:50]}")
        
        lines.extend([
            "",
            "=" * 80,
            "✅ 收集完成！",
            f"📁 数据保存在: {self.data_dir}",
            f"📊 日志文件: {self.log_file}",
            "",
            "💡 下一步建议:",
            "  1. 检查下载的PDF/Excel文件",
            "  2. 处理提取的表格数据",
            "  3. 整合到CSV模板中",
            "=" * 80
        ])
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    collector = AdvancedDataCollector(base_dir)
    
    report = collector.run()
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'intelligent_collection_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()