#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术数据库专用爬虫
专门收集知网、万方、维普等学术平台的研究数据
"""

import os
import json
import time
import urllib.request
import urllib.error
import urllib.parse
import re
from datetime import datetime

class AcademicDatabaseCrawler:
    """学术数据库专用爬虫"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'academic_data')
        self.log_file = os.path.join(base_dir, 'data', 'academic_crawler_log.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'papers'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'statistics'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'datasets'), exist_ok=True)
        
        self.stats = {
            'total_sources': 0,
            'successful': 0,
            'failed': 0,
            'data_size': 0,
            'papers_found': 0,
            'datasets_found': 0,
            'start_time': None
        }
        
        # 学术数据库搜索关键词
        self.keywords = [
            '中医药统计',
            '中医医院数据分析',
            '中医药服务评价',
            '中医药医保支付',
            '中医药发展报告',
            '中医药服务利用',
            '中医医院运营',
            '中医药人才培养',
            '中医药资源配置',
            '中医药统计分析',
        ]
        
        # 学术数据源
        self.sources = [
            # 学术数据库
            {
                'name': '中国知网-中医药研究',
                'url': 'https://www.cnki.net/',
                'type': 'database',
                'priority': 1,
                'description': '中国学术期刊全文数据库',
                'search_enabled': True,
            },
            {
                'name': '万方数据-中医药统计',
                'url': 'https://www.wanfangdata.com.cn/',
                'type': 'database',
                'priority': 1,
                'description': '学术期刊、学位论文数据库',
                'search_enabled': True,
            },
            {
                'name': '维普数据-中医药',
                'url': 'https://www.cqvip.com/',
                'type': 'database',
                'priority': 1,
                'description': '中文科技期刊数据库',
                'search_enabled': True,
            },
            
            # 学术机构
            {
                'name': '中国中医科学院',
                'url': 'http://www.cacms.ac.cn/',
                'type': 'institution',
                'priority': 2,
                'description': '中医药研究机构',
                'search_enabled': False,
            },
            {
                'name': '北京中医药大学学术库',
                'url': 'http://www.bucm.edu.cn/',
                'type': 'institution',
                'priority': 2,
                'description': '中医药大学学术资源',
                'search_enabled': False,
            },
            {
                'name': '上海中医药大学学术库',
                'url': 'http://www.shutcm.edu.cn/',
                'type': 'institution',
                'priority': 2,
                'description': '中医药大学学术资源',
                'search_enabled': False,
            },
            
            # 统计数据平台
            {
                'name': '国家数据-中医药',
                'url': 'https://data.stats.gov.cn/',
                'type': 'statistics',
                'priority': 1,
                'description': '国家统计数据平台',
                'search_enabled': False,
            },
            {
                'name': '卫生健康统计',
                'url': 'http://www.nhc.gov.cn/wjw/index.shtml',
                'type': 'statistics',
                'priority': 1,
                'description': '卫生健康统计数据',
                'search_enabled': False,
            },
        ]
    
    def build_search_url(self, base_url, keyword):
        """构建搜索URL"""
        # 根据不同平台构建搜索URL
        if 'cnki.net' in base_url:
            return f"https://www.cnki.net/search?q={urllib.parse.quote(keyword)}"
        elif 'wanfangdata.com.cn' in base_url:
            return f"https://www.wanfangdata.com.cn/search?q={urllib.parse.quote(keyword)}"
        elif 'cqvip.com' in base_url:
            return f"https://www.cqvip.com/qikan/search?q={urllib.parse.quote(keyword)}"
        else:
            return base_url
    
    def fetch_page(self, url, name, source_type):
        """获取页面"""
        print(f"  📚 {name}")
        print(f"     类型: {source_type}")
        print(f"     URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
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
                
                # 提取论文信息
                titles = re.findall(r'<a[^>]*title=["\']([^"\']+)["\']', decoded)
                authors = re.findall(r'作者[：:]\s*([^\n<>]+)', decoded)
                abstracts = re.findall(r'摘要[：:]\s*([^\n<>]+)', decoded)
                keywords_list = re.findall(r'关键词[：:]\s*([^\n<>]+)', decoded)
                
                # 提取下载链接
                pdf_links = re.findall(r'href=["\']([^"\']*\.pdf)["\']', decoded, re.IGNORECASE)
                doc_links = re.findall(r'href=["\']([^"\']*\.(?:doc|docx))["\']', decoded, re.IGNORECASE)
                
                # 提取引用信息
                citations = re.findall(r'被引[：:]\s*(\d+)', decoded)
                downloads = re.findall(r'下载[：:]\s*(\d+)', decoded)
                
                # 提取年份
                years = re.findall(r'(20\d{2})', decoded)
                unique_years = list(set(years))[:10]
                
                print(f"     ✅ 成功: {len(content)}字节")
                print(f"     📄 论文标题: {len(titles)}个")
                if authors:
                    print(f"     👤 作者: {len(authors)}个")
                if pdf_links:
                    print(f"     📥 PDF下载: {len(pdf_links)}个")
                if citations:
                    print(f"     📊 引用: {citations[0] if citations else 0}次")
                if downloads:
                    print(f"     📥 下载: {downloads[0] if downloads else 0}次")
                if unique_years:
                    print(f"     📅 年份: {', '.join(unique_years[:5])}")
                
                return {
                    'status': 'success',
                    'name': name,
                    'url': url,
                    'type': source_type,
                    'size': len(content),
                    'paper_count': len(titles),
                    'authors_count': len(authors),
                    'pdf_count': len(pdf_links),
                    'years': unique_years,
                    'citations': citations[0] if citations else 0,
                    'downloads': downloads[0] if downloads else 0,
                    'content': decoded[:5000],
                    'pdf_links': pdf_links[:10],
                    'doc_links': doc_links[:10],
                    'titles': titles[:20],
                    'authors': authors[:10],
                    'keywords_list': keywords_list[:10],
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
            
            if result['paper_count']:
                f.write(f"论文数量: {result['paper_count']}个\n")
            if result['pdf_count']:
                f.write(f"PDF文件: {result['pdf_count']}个\n")
            if result['years']:
                f.write(f"年份: {', '.join(result['years'])}\n")
            if result['citations']:
                f.write(f"引用次数: {result['citations']}\n")
            if result['downloads']:
                f.write(f"下载次数: {result['downloads']}\n")
            
            f.write("=" * 80 + "\n\n")
            f.write(result['content'])
    
    def run(self):
        """运行爬虫"""
        print("=" * 80)
        print("📚 学术数据库专用爬虫启动")
        print("=" * 80)
        print(f"目标数据源: {len(self.sources)}个")
        print(f"搜索关键词: {len(self.keywords)}个")
        print(f"数据类型: 学术数据库({sum(1 for s in self.sources if s['type']=='database')}个)")
        print(f"          学术机构({sum(1 for s in self.sources if s['type']=='institution')}个)")
        print(f"          统计数据({sum(1 for s in self.sources if s['type']=='statistics')}个)")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        results = []
        
        # 按优先级排序
        sorted_sources = sorted(self.sources, key=lambda x: x['priority'])
        
        for i, source in enumerate(sorted_sources, 1):
            print(f"\n[{i}/{len(self.sources)}]")
            
            # 如果支持搜索，使用关键词搜索
            if source.get('search_enabled') and self.keywords:
                # 只搜索前3个关键词，避免过多请求
                for keyword in self.keywords[:3]:
                    search_url = self.build_search_url(source['url'], keyword)
                    result = self.fetch_page(search_url, f"{source['name']}-{keyword}", source['type'])
                    results.append(result)
                    
                    if result['status'] == 'success':
                        self.stats['successful'] += 1
                        self.stats['data_size'] += result['size']
                        self.stats['papers_found'] += result.get('paper_count', 0)
                        self.stats['datasets_found'] += result.get('pdf_count', 0)
                        self.save_result(result)
                    else:
                        self.stats['failed'] += 1
                    
                    self.stats['total_sources'] += 1
                    time.sleep(2)
            else:
                # 直接访问主页
                result = self.fetch_page(source['url'], source['name'], source['type'])
                results.append(result)
                
                if result['status'] == 'success':
                    self.stats['successful'] += 1
                    self.stats['data_size'] += result['size']
                    self.stats['papers_found'] += result.get('paper_count', 0)
                    self.stats['datasets_found'] += result.get('pdf_count', 0)
                    self.save_result(result)
                else:
                    self.stats['failed'] += 1
                
                self.stats['total_sources'] += 1
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
            'keywords_used': self.keywords[:3],
            'results': [
                {
                    'name': r['name'],
                    'type': r.get('type', 'unknown'),
                    'url': r['url'],
                    'status': r['status'],
                    'size': r.get('size', 0),
                    'paper_count': r.get('paper_count', 0),
                    'pdf_count': r.get('pdf_count', 0),
                    'years': r.get('years', []),
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
            "📚 学术数据库爬取完成报告",
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
            f"  发现论文: {self.stats['papers_found']}篇",
            f"  发现数据: {self.stats['datasets_found']}个",
            "",
            "📊 分类统计:",
        ]
        
        # 按类型统计
        type_stats = {}
        for r in results:
            r_type = r.get('type', 'unknown')
            if r_type not in type_stats:
                type_stats[r_type] = {'success': 0, 'failed': 0, 'size': 0, 'papers': 0, 'pdfs': 0}
            
            if r['status'] == 'success':
                type_stats[r_type]['success'] += 1
                type_stats[r_type]['size'] += r.get('size', 0)
                type_stats[r_type]['papers'] += r.get('paper_count', 0)
                type_stats[r_type]['pdfs'] += r.get('pdf_count', 0)
            else:
                type_stats[r_type]['failed'] += 1
        
        type_names = {
            'database': '学术数据库',
            'institution': '学术机构',
            'statistics': '统计数据'
        }
        
        for t_type, stats in type_stats.items():
            lines.append(f"  {type_names.get(t_type, t_type)}:")
            lines.append(f"    成功: {stats['success']}个")
            lines.append(f"    失败: {stats['failed']}个")
            lines.append(f"    数据: {stats['size']/1024:.1f}KB")
            lines.append(f"    论文: {stats['papers']}篇")
            lines.append(f"    PDF: {stats['pdfs']}个")
        
        lines.extend([
            "",
            "✅ 成功的数据源:",
        ])
        
        for r in results:
            if r['status'] == 'success':
                lines.append(f"  ✅ {r['name']} ({type_names.get(r['type'], r['type'])})")
                lines.append(f"     大小: {r['size']}字节")
                if r.get('paper_count'):
                    lines.append(f"     论文: {r['paper_count']}篇")
                if r.get('pdf_count'):
                    lines.append(f"     PDF: {r['pdf_count']}个")
                if r.get('years'):
                    lines.append(f"     年份: {', '.join(r['years'][:5])}")
        
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
            "  1. 检查发现的PDF和论文",
            "  2. 整理论文元数据",
            "  3. 提取统计方法和数据",
            "=" * 80
        ])
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = AcademicDatabaseCrawler(base_dir)
    
    report = crawler.run()
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'academic_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()