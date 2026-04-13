#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计年鉴专用爬虫
专门收集统计年鉴、年度报告等官方数据
"""

import os
import json
import time
import urllib.request
import urllib.error
import re
from datetime import datetime

class StatisticalYearbookCrawler:
    """统计年鉴专用爬虫"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'yearbook_data')
        self.log_file = os.path.join(base_dir, 'data', 'yearbook_crawler_log.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'yearbooks'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'reports'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'statistics'), exist_ok=True)
        
        self.stats = {
            'total_sources': 0,
            'successful': 0,
            'failed': 0,
            'data_size': 0,
            'files_found': 0,
            'start_time': None
        }
        
        # 统计年鉴数据源
        self.sources = [
            # 国家级统计年鉴
            {
                'name': '中国统计年鉴',
                'url': 'http://www.stats.gov.cn/sj/ndsj/',
                'type': 'yearbook',
                'priority': 1,
                'description': '国家统计局年度数据',
                'keywords': ['统计年鉴', '年度数据', '国民经济'],
            },
            {
                'name': '中国卫生健康统计年鉴',
                'url': 'http://www.nhc.gov.cn/wjw/index.shtml',
                'type': 'yearbook',
                'priority': 1,
                'description': '卫生健康年度统计',
                'keywords': ['卫生统计', '医疗', '中医药'],
            },
            {
                'name': '中国中医药统计年鉴',
                'url': 'http://www.satcm.gov.cn/',
                'type': 'yearbook',
                'priority': 1,
                'description': '中医药年度发展数据',
                'keywords': ['中医药', '统计', '发展'],
            },
            {
                'name': '中国医保统计年鉴',
                'url': 'http://www.nhsa.gov.cn/',
                'type': 'yearbook',
                'priority': 1,
                'description': '医疗保险年度数据',
                'keywords': ['医保', '统计', '基金'],
            },
            
            # 省级统计年鉴
            {
                'name': '北京统计年鉴',
                'url': 'http://tjj.beijing.gov.cn/',
                'type': 'yearbook',
                'priority': 2,
                'description': '北京市年度统计',
                'keywords': ['统计年鉴', '北京', '经济'],
            },
            {
                'name': '上海统计年鉴',
                'url': 'http://tjj.sh.gov.cn/',
                'type': 'yearbook',
                'priority': 2,
                'description': '上海市年度统计',
                'keywords': ['统计年鉴', '上海', '经济'],
            },
            {
                'name': '广东统计年鉴',
                'url': 'http://stats.gd.gov.cn/',
                'type': 'yearbook',
                'priority': 2,
                'description': '广东省年度统计',
                'keywords': ['统计年鉴', '广东', '经济'],
            },
            
            # 行业报告
            {
                'name': '中医药事业发展报告',
                'url': 'http://www.satcm.gov.cn/',
                'type': 'report',
                'priority': 2,
                'description': '中医药年度发展报告',
                'keywords': ['中医药', '发展报告', '年度'],
            },
            {
                'name': '卫生健康事业发展报告',
                'url': 'http://www.nhc.gov.cn/',
                'type': 'report',
                'priority': 2,
                'description': '卫生健康年度报告',
                'keywords': ['卫生健康', '发展', '报告'],
            },
            
            # 专项统计
            {
                'name': '中医医院统计',
                'url': 'http://www.satcm.gov.cn/',
                'type': 'statistics',
                'priority': 3,
                'description': '中医医院专项统计',
                'keywords': ['中医医院', '统计', '床位'],
            },
            {
                'name': '中医药人员统计',
                'url': 'http://www.satcm.gov.cn/',
                'type': 'statistics',
                'priority': 3,
                'description': '中医药人员统计数据',
                'keywords': ['中医药人员', '统计', '培养'],
            },
        ]
    
    def fetch_page(self, url, name, source_type):
        """获取页面"""
        print(f"  📊 {name}")
        print(f"     类型: {source_type}")
        print(f"     URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                content = response.read()
                
                # 智能解码
                decoded = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
                    try:
                        decoded = content.decode(encoding)
                        break
                    except:
                        continue
                
                if not decoded:
                    decoded = content.decode('utf-8', errors='ignore')
                
                # 提取关键信息
                keywords_found = []
                description = ''
                year_pattern = re.findall(r'20\d{2}', decoded)
                years = list(set(year_pattern))[:5] if year_pattern else []
                
                # 提取下载链接
                pdf_links = re.findall(r'href=["\']([^"\']*\.pdf)["\']', decoded, re.IGNORECASE)
                excel_links = re.findall(r'href=["\']([^"\']*\.(?:xls|xlsx))["\']', decoded, re.IGNORECASE)
                
                # 提取表格
                tables = re.findall(r'<table[^>]*>(.*?)</table>', decoded, re.DOTALL | re.IGNORECASE)
                
                print(f"     ✅ 成功: {len(content)}字节")
                print(f"     📅 年份: {', '.join(years) if years else '未发现'}")
                if pdf_links:
                    print(f"     📄 PDF文件: {len(pdf_links)}个")
                if excel_links:
                    print(f"     📊 Excel文件: {len(excel_links)}个")
                if tables:
                    print(f"     📊 表格: {len(tables)}个")
                
                return {
                    'status': 'success',
                    'name': name,
                    'url': url,
                    'type': source_type,
                    'size': len(content),
                    'years': years,
                    'pdf_count': len(pdf_links),
                    'excel_count': len(excel_links),
                    'table_count': len(tables),
                    'content': decoded[:5000],
                    'pdf_links': pdf_links[:10],
                    'excel_links': excel_links[:10],
                    'timestamp': datetime.now().isoformat()
                }
        
        except urllib.error.HTTPError as e:
            print(f"     ❌ HTTP错误: {e.code}")
            return {
                'status': 'error',
                'name': name,
                'url': url,
                'error': f'HTTP {e.code}',
                'timestamp': datetime.now().isoformat()
            }
        
        except urllib.error.URLError as e:
            print(f"     ❌ URL错误: {str(e.reason)[:50]}")
            return {
                'status': 'error',
                'name': name,
                'url': url,
                'error': str(e.reason),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"     ❌ 错误: {str(e)[:50]}")
            return {
                'status': 'error',
                'name': name,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def save_result(self, result):
        """保存结果"""
        if result['status'] != 'success':
            return
        
        # 确定保存目录
        save_dir = os.path.join(self.data_dir, f"{result['type']}s")
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存文件
        filename = f"{result['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"来源: {result['name']}\n")
            f.write(f"类型: {result['type']}\n")
            f.write(f"URL: {result['url']}\n")
            f.write(f"时间: {result['timestamp']}\n")
            f.write(f"大小: {result['size']} 字节\n")
            if result['years']:
                f.write(f"年份: {', '.join(result['years'])}\n")
            if result['pdf_count']:
                f.write(f"PDF文件: {result['pdf_count']}个\n")
            if result['excel_count']:
                f.write(f"Excel文件: {result['excel_count']}个\n")
            if result['table_count']:
                f.write(f"表格: {result['table_count']}个\n")
            f.write("=" * 80 + "\n\n")
            f.write(result['content'])
    
    def run(self):
        """运行爬虫"""
        print("=" * 80)
        print("📚 统计年鉴专用爬虫启动")
        print("=" * 80)
        print(f"目标数据源: {len(self.sources)}个")
        print(f"数据类型: 统计年鉴({sum(1 for s in self.sources if s['type']=='yearbook')}个)")
        print(f"          行业报告({sum(1 for s in self.sources if s['type']=='report')}个)")
        print(f"          专项统计({sum(1 for s in self.sources if s['type']=='statistics')}个)")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        results = []
        
        # 按优先级排序
        sorted_sources = sorted(self.sources, key=lambda x: x['priority'])
        
        for i, source in enumerate(sorted_sources, 1):
            print(f"\n[{i}/{len(self.sources)}]")
            
            result = self.fetch_page(source['url'], source['name'], source['type'])
            results.append(result)
            
            if result['status'] == 'success':
                self.stats['successful'] += 1
                self.stats['data_size'] += result['size']
                self.stats['files_found'] += result.get('pdf_count', 0) + result.get('excel_count', 0)
                
                # 保存结果
                self.save_result(result)
            else:
                self.stats['failed'] += 1
            
            self.stats['total_sources'] += 1
            
            # 礼貌延迟
            time.sleep(2)
        
        # 保存日志
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
            'results': [
                {
                    'name': r['name'],
                    'type': r.get('type', 'unknown'),
                    'url': r['url'],
                    'status': r['status'],
                    'size': r.get('size', 0),
                    'years': r.get('years', []),
                    'pdf_count': r.get('pdf_count', 0),
                    'excel_count': r.get('excel_count', 0),
                    'table_count': r.get('table_count', 0),
                }
                for r in results
            ]
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self, results):
        """生成报告"""
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        lines = [
            "=" * 80,
            "📊 统计年鉴爬取完成报告",
            "=" * 80,
            f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"持续时间: {elapsed:.1f}秒",
            "",
            "📈 统计信息:",
            f"  数据源总数: {self.stats['total_sources']}个",
            f"  成功爬取: {self.stats['successful']}个",
            f"  爬取失败: {self.stats['failed']}个",
            f"  成功率: {self.stats['successful']/(self.stats['total_sources'] or 1)*100:.1f}%",
            f"  数据量: {self.stats['data_size']:,}字节 ({self.stats['data_size']/1024:.1f}KB)",
            f"  发现文件: {self.stats['files_found']}个",
            "",
            "📊 分类统计:",
        ]
        
        # 按类型统计
        type_stats = {}
        for r in results:
            r_type = r.get('type', 'unknown')
            if r_type not in type_stats:
                type_stats[r_type] = {'success': 0, 'failed': 0, 'size': 0}
            
            if r['status'] == 'success':
                type_stats[r_type]['success'] += 1
                type_stats[r_type]['size'] += r.get('size', 0)
            else:
                type_stats[r_type]['failed'] += 1
        
        type_names = {
            'yearbook': '统计年鉴',
            'report': '行业报告',
            'statistics': '专项统计'
        }
        
        for t_type, stats in type_stats.items():
            lines.append(f"  {type_names.get(t_type, t_type)}:")
            lines.append(f"    成功: {stats['success']}个")
            lines.append(f"    失败: {stats['failed']}个")
            lines.append(f"    数据: {stats['size']/1024:.1f}KB")
        
        lines.extend([
            "",
            "✅ 成功的数据源:",
        ])
        
        for r in results:
            if r['status'] == 'success':
                lines.append(f"  ✅ {r['name']} ({type_names.get(r['type'], r['type'])})")
                lines.append(f"     大小: {r['size']}字节")
                if r['years']:
                    lines.append(f"     年份: {', '.join(r['years'])}")
                if r['pdf_count']:
                    lines.append(f"     PDF: {r['pdf_count']}个")
                if r['excel_count']:
                    lines.append(f"     Excel: {r['excel_count']}个")
                if r['table_count']:
                    lines.append(f"     表格: {r['table_count']}个")
        
        lines.extend([
            "",
            "❌ 失败的数据源:",
        ])
        
        for r in results:
            if r['status'] != 'success':
                lines.append(f"  ❌ {r['name']}: {r['error'][:50]}")
        
        lines.extend([
            "",
            "=" * 80,
            "✅ 爬取完成！",
            f"📁 数据保存在: {self.data_dir}",
            f"📊 日志文件: {self.log_file}",
            "",
            "💡 下一步建议:",
            "  1. 检查PDF和Excel文件下载链接",
            "  2. 提取表格数据到CSV",
            "  3. 整合多年份数据",
            "=" * 80
        ])
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = StatisticalYearbookCrawler(base_dir)
    
    report = crawler.run()
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'yearbook_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()