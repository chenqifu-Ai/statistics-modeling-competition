#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版网络爬虫 - 深度数据挖掘
支持深度爬取、智能解析、数据提取
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class EnhancedWebCrawler:
    """增强版网络爬虫 - 深度数据挖掘"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.cache_dir = os.path.join(base_dir, 'data', 'cache')
        self.raw_dir = os.path.join(base_dir, 'data', 'raw', 'web_crawled')
        self.log_file = os.path.join(base_dir, 'data', 'crawler_log.json')
        self.lock = threading.Lock()
        
        # 创建目录
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        
        # 爬虫配置
        self.config = {
            'max_workers': 8,
            'timeout': 30,
            'retry_times': 5,
            'retry_delay': 3,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
            ],
            'cache_enabled': True,
            'cache_expire': 86400,
            'delay_range': (1, 3)
        }
        
        # 数据源配置 - 扩展更多来源
        self.target_sources = {
            'stats_gov_main': {
                'name': '国家统计局主站',
                'url': 'https://www.stats.gov.cn/',
                'priority': 1,
                'depth': 2,
                'patterns': ['统计年鉴', '卫生健康', '社会服务', '中医药']
            },
            'stats_gov_yearbook': {
                'name': '统计年鉴页面',
                'url': 'https://www.stats.gov.cn/sj/ndsj/',
                'priority': 1,
                'depth': 3,
                'patterns': ['2024', '2023', '卫生', '中医']
            },
            'stats_gov_health': {
                'name': '卫生健康统计',
                'url': 'https://www.stats.gov.cn/sj/zxfb/',
                'priority': 1,
                'depth': 2,
                'patterns': ['卫生', '健康', '医疗', '医院']
            },
            'cnki': {
                'name': '中国知网',
                'url': 'https://www.cnki.net/',
                'priority': 2,
                'depth': 1,
                'patterns': ['中医药', '统计', '医院']
            },
            'wanfang': {
                'name': '万方数据',
                'url': 'https://www.wanfangdata.com.cn/',
                'priority': 2,
                'depth': 1,
                'patterns': ['中医药', '统计年鉴']
            },
            'gov_cn': {
                'name': '中国政府网',
                'url': 'https://www.gov.cn/',
                'priority': 1,
                'depth': 2,
                'patterns': ['中医药', '卫生健康', '政策']
            },
            'nhfpc_archive': {
                'name': '卫健委历史数据',
                'url': 'http://www.nhc.gov.cn/wjw/jktnr/list.shtml',
                'priority': 2,
                'depth': 2,
                'patterns': ['统计', '年鉴', '中医药']
            },
            'satcm_main': {
                'name': '中医药管理局主站',
                'url': 'http://www.satcm.gov.cn/',
                'priority': 3,
                'depth': 2,
                'patterns': ['发展报告', '统计', '规划']
            },
            'people_health': {
                'name': '人民网健康频道',
                'url': 'http://health.people.com.cn/',
                'priority': 2,
                'depth': 2,
                'patterns': ['中医药', '医院', '统计']
            },
            'xinhua_health': {
                'name': '新华网健康',
                'url': 'http://www.xinhuanet.com/health/',
                'priority': 2,
                'depth': 2,
                'patterns': ['中医药', '健康', '医院']
            }
        }
    
    def get_random_user_agent(self):
        """获取随机User-Agent"""
        import random
        return random.choice(self.config['user_agents'])
    
    def smart_delay(self):
        """智能延迟"""
        import random
        delay = random.uniform(*self.config['delay_range'])
        time.sleep(delay)
    
    def fetch_page(self, url, retry_count=0):
        """智能页面抓取"""
        # 设置请求头
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=self.config['timeout']) as response:
                content = response.read()
                
                # 尝试多种编码
                encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
                decoded_content = None
                
                for encoding in encodings:
                    try:
                        decoded_content = content.decode(encoding)
                        break
                    except (UnicodeDecodeError, AttributeError):
                        continue
                
                if decoded_content is None:
                    decoded_content = content.decode('utf-8', errors='ignore')
                
                return {
                    'status': 'success',
                    'url': url,
                    'content': decoded_content,
                    'size': len(content),
                    'encoding': encoding,
                    'timestamp': datetime.now().isoformat()
                }
                
        except urllib.error.HTTPError as e:
            if retry_count < self.config['retry_times']:
                print(f"    ⚠️ HTTP {e.code} 错误，重试中... ({retry_count+1}/{self.config['retry_times']})")
                time.sleep(self.config['retry_delay'])
                return self.fetch_page(url, retry_count + 1)
            
            return {
                'status': 'error',
                'url': url,
                'error': f'HTTP Error {e.code}: {e.reason}',
                'timestamp': datetime.now().isoformat()
            }
        
        except urllib.error.URLError as e:
            if retry_count < self.config['retry_times']:
                print(f"    ⚠️ URL错误，重试中... ({retry_count+1}/{self.config['retry_times']})")
                time.sleep(self.config['retry_delay'])
                return self.fetch_page(url, retry_count + 1)
            
            return {
                'status': 'error',
                'url': url,
                'error': f'URL Error: {e.reason}',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            if retry_count < self.config['retry_times']:
                time.sleep(self.config['retry_delay'])
                return self.fetch_page(url, retry_count + 1)
            
            return {
                'status': 'error',
                'url': url,
                'error': f'Exception: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def extract_links(self, content, base_url, patterns):
        """智能链接提取"""
        links = []
        
        # 提取所有链接
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(link_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for url, text in matches:
            # 处理相对URL
            if not url.startswith('http'):
                url = urllib.parse.urljoin(base_url, url)
            
            # 清理URL
            url = url.split('#')[0]  # 移除锚点
            url = url.strip()
            
            # 过滤无效链接
            if any(skip in url for skip in ['javascript:', 'mailto:', 'tel:', 'void(']):
                continue
            
            # 检查是否匹配模式
            matched = False
            for pattern in patterns:
                if pattern.lower() in text.lower() or pattern.lower() in url.lower():
                    matched = True
                    break
            
            if matched or any(ext in url for ext in ['.pdf', '.xls', '.xlsx', '.csv', '.doc']):
                links.append({
                    'url': url,
                    'text': text.strip(),
                    'matched': matched
                })
        
        return links
    
    def extract_data(self, content, patterns):
        """智能数据提取"""
        extracted_data = []
        
        for pattern in patterns:
            # 查找包含关键词的段落
            para_pattern = r'<p[^>]*>([^<]*' + re.escape(pattern) + r'[^<]*)</p>'
            matches = re.findall(para_pattern, content, re.IGNORECASE)
            
            for match in matches:
                cleaned_text = re.sub(r'<[^>]+>', '', match).strip()
                if cleaned_text:
                    extracted_data.append({
                        'pattern': pattern,
                        'text': cleaned_text
                    })
        
        # 提取表格数据
        table_pattern = r'<table[^>]*>(.*?)</table>'
        tables = re.findall(table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if tables:
            for i, table in enumerate(tables[:5], 1):  # 只取前5个表格
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.IGNORECASE | re.DOTALL)
                table_data = []
                
                for row in rows:
                    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.IGNORECASE | re.DOTALL)
                    cleaned_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                    if any(cleaned_cells):
                        table_data.append(cleaned_cells)
                
                if table_data:
                    extracted_data.append({
                        'type': 'table',
                        'table_id': i,
                        'data': table_data
                    })
        
        return extracted_data
    
    def crawl_source(self, source_key):
        """爬取单个数据源"""
        source = self.target_sources.get(source_key)
        if not source:
            return None
        
        print(f"\n🕷️ 爬取 {source['name']}...")
        print(f"   URL: {source['url']}")
        
        result = {
            'source': source_key,
            'name': source['name'],
            'url': source['url'],
            'priority': source['priority'],
            'timestamp': datetime.now().isoformat(),
            'pages': [],
            'links': [],
            'data': [],
            'status': 'pending'
        }
        
        # 主页面爬取
        print(f"   📄 抓取主页面...")
        page_result = self.fetch_page(source['url'])
        
        if page_result['status'] == 'success':
            result['status'] = 'success'
            result['pages'].append(page_result)
            
            print(f"   ✅ 成功获取 {page_result['size']} 字节")
            
            # 提取链接
            links = self.extract_links(page_result['content'], source['url'], source['patterns'])
            result['links'] = links
            print(f"   🔗 发现 {len(links)} 个相关链接")
            
            # 提取数据
            data = self.extract_data(page_result['content'], source['patterns'])
            result['data'] = data
            print(f"   📊 提取 {len(data)} 个数据片段")
            
            # 深度爬取（如果配置了）
            if source['depth'] > 1 and links:
                print(f"   🔄 开始深度爬取（深度={source['depth']}）...")
                crawled_urls = set()
                crawled_urls.add(source['url'])
                
                depth_links = [link['url'] for link in links[:10]]  # 只爬取前10个链接
                
                for depth in range(2, source['depth'] + 1):
                    print(f"   📍 深度级别 {depth}...")
                    next_level_links = []
                    
                    for url in depth_links:
                        if url in crawled_urls:
                            continue
                        
                        self.smart_delay()
                        print(f"      抓取: {url[:60]}...")
                        sub_result = self.fetch_page(url)
                        
                        if sub_result['status'] == 'success':
                            crawled_urls.add(url)
                            result['pages'].append(sub_result)
                            
                            # 提取子链接
                            sub_links = self.extract_links(sub_result['content'], url, source['patterns'])
                            result['links'].extend(sub_links)
                            
                            # 提取子数据
                            sub_data = self.extract_data(sub_result['content'], source['patterns'])
                            result['data'].extend(sub_data)
                            
                            next_level_links.extend([link['url'] for link in sub_links[:5]])
                    
                    depth_links = list(set(next_level_links))
                    if not depth_links:
                        break
            
            print(f"   📊 总计: {len(result['pages'])} 页面, {len(result['links'])} 链接, {len(result['data'])} 数据片段")
        
        else:
            result['status'] = 'error'
            result['error'] = page_result.get('error', 'Unknown error')
            print(f"   ❌ 失败: {result['error']}")
        
        return result
    
    def crawl_all_parallel(self):
        """并行爬取所有数据源"""
        print("=" * 70)
        print("🕷️ 增强版网络爬虫 - 深度数据挖掘模式")
        print("=" * 70)
        print(f"目标数据源: {len(self.target_sources)}个")
        print(f"并发线程: {self.config['max_workers']}个")
        print(f"重试次数: {self.config['retry_times']}次")
        print()
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # 按优先级排序提交任务
            sorted_sources = sorted(
                self.target_sources.keys(),
                key=lambda k: self.target_sources[k]['priority']
            )
            
            future_to_source = {
                executor.submit(self.crawl_source, source_key): source_key
                for source_key in sorted_sources
            }
            
            # 收集结果
            for future in as_completed(future_to_source):
                source_key = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        all_results.append(result)
                except Exception as e:
                    print(f"❌ {source_key} 爬取异常: {str(e)}")
                    all_results.append({
                        'source': source_key,
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        # 保存爬取结果
        self.save_crawl_results(all_results)
        
        # 生成报告
        report = self.generate_crawl_report(all_results)
        
        return report
    
    def save_crawl_results(self, results):
        """保存爬取结果"""
        # 保存JSON日志
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'total_sources': len(results),
            'results': results
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        # 保存原始页面内容
        for result in results:
            if result.get('status') == 'success' and result.get('pages'):
                source_dir = os.path.join(self.raw_dir, result['source'])
                os.makedirs(source_dir, exist_ok=True)
                
                for i, page in enumerate(result['pages']):
                    filename = f"page_{i}_{datetime.now().strftime('%H%M%S')}.html"
                    filepath = os.path.join(source_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(page['content'])
    
    def generate_crawl_report(self, results):
        """生成爬取报告"""
        success_count = sum(1 for r in results if r.get('status') == 'success')
        error_count = len(results) - success_count
        
        total_pages = sum(len(r.get('pages', [])) for r in results)
        total_links = sum(len(r.get('links', [])) for r in results)
        total_data = sum(len(r.get('data', [])) for r in results)
        total_size = sum(sum(p.get('size', 0) for p in r.get('pages', [])) for r in results)
        
        report_lines = [
            "=" * 70,
            "🕷️ 网络爬取完成报告",
            "=" * 70,
            f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📊 总体统计:",
            f"  数据源总数: {len(results)}个",
            f"  成功爬取: {success_count}个",
            f"  失败: {error_count}个",
            f"  成功率: {success_count/len(results)*100:.1f}%",
            "",
            "📈 数据统计:",
            f"  页面总数: {total_pages}页",
            f"  链接总数: {total_links}个",
            f"  数据片段: {total_data}个",
            f"  数据总量: {total_size:,}字节 ({total_size/1024/1024:.2f}MB)",
            "",
            "📋 详细结果:",
            ""
        ]
        
        for result in sorted(results, key=lambda r: r.get('priority', 999)):
            status_emoji = "✅" if result.get('status') == 'success' else "❌"
            report_lines.append(f"{status_emoji} {result['name']} (优先级{result.get('priority', '?')})")
            
            if result.get('status') == 'success':
                report_lines.append(f"   📄 页面: {len(result.get('pages', []))}页")
                report_lines.append(f"   🔗 链接: {len(result.get('links', []))}个")
                report_lines.append(f"   📊 数据: {len(result.get('data', []))}个片段")
                
                # 显示部分链接
                for link in result.get('links', [])[:3]:
                    report_lines.append(f"      - {link.get('text', '')[:50]}")
            else:
                report_lines.append(f"   ⚠️ 错误: {result.get('error', 'Unknown')}")
            
            report_lines.append("")
        
        report_lines.extend([
            "=" * 70,
            "💡 下一步操作:",
            "1. 检查保存的原始页面内容",
            "2. 分析提取的数据片段",
            "3. 手动下载重要的PDF/Excel文件",
            "4. 整理和清洗爬取的数据",
            "",
            "📁 数据位置:",
            f"  原始页面: {self.raw_dir}",
            f"  爬取日志: {self.log_file}",
            "=" * 70
        ])
        
        return "\n".join(report_lines)

def main():
    """主函数"""
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = EnhancedWebCrawler(base_dir)
    
    # 开始爬取
    report = crawler.crawl_all_parallel()
    print(report)
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'enhanced_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存至: {report_file}")

if __name__ == '__main__':
    main()