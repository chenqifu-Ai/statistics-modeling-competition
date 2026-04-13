#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展版网络爬虫 - 收集更多数据源
"""

import os
import json
import time
import urllib.request
import urllib.error
import re
from datetime import datetime

class ExpandedCrawler:
    """扩展版网络爬虫 - 更多数据源"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'expanded_crawled')
        self.log_file = os.path.join(base_dir, 'data', 'expanded_crawler_log.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.stats = {
            'crawled': 0,
            'failed': 0,
            'data_size': 0,
            'start_time': None,
            'sources': {}
        }
        
        # 扩展数据源列表
        self.sources = [
            # 医疗健康类
            ('http://www.nhc.gov.cn/', '国家卫健委官网', 1, ['健康', '统计', '医疗']),
            ('http://www.nhc.gov.cn/wjw/jktnr/list.shtml', '卫健委统计年鉴', 1, ['统计', '年鉴', '健康']),
            ('http://www.satcm.gov.cn/', '中医药管理局', 1, ['中医', '统计', '发展']),
            
            # 学术研究类
            ('https://www.cnki.net/', '中国知网', 1, ['中医药', '统计', '研究']),
            ('https://www.wanfangdata.com.cn/', '万方数据', 1, ['中医药', '统计']),
            ('https://www.cqvip.com/', '维普数据', 2, ['中医药', '统计']),
            
            # 统计数据类
            ('https://data.stats.gov.cn/', '国家数据', 1, ['统计', '数据']),
            ('http://www.stats.gov.cn/sj/', '统计数据', 1, ['统计', '数据']),
            ('http://www.stats.gov.cn/sj/ndsj/', '统计年鉴', 1, ['年鉴', '统计']),
            
            # 政府机构类
            ('http://www.gov.cn/', '中国政府网', 1, ['政策', '健康']),
            ('http://www.gov.cn/zhengce/', '政策文件', 1, ['政策', '中医药']),
            
            # 中医药机构类
            ('http://www.bucm.edu.cn/', '北京中医药大学', 2, ['中医', '研究']),
            ('http://www.shutcm.edu.cn/', '上海中医药大学', 2, ['中医', '研究']),
            ('http://www.gztcm.edu.cn/', '广州中医药大学', 2, ['中医', '研究']),
            ('http://www.njucm.edu.cn/', '南京中医药大学', 2, ['中医', '研究']),
            ('http://www.cdutcm.edu.cn/', '成都中医药大学', 2, ['中医', '研究']),
            
            # 医疗机构类
            ('http://www.bucmh.com/', '北京中医医院', 2, ['中医', '医疗']),
            ('http://www.gztcm.com.cn/', '广东省中医院', 2, ['中医', '医疗']),
            
            # 新闻媒体类
            ('http://www.cntcm.com.cn/', '中国中医药报', 2, ['中医', '新闻']),
            ('http://www.cntcmnews.com/', '中医药新闻', 2, ['中医', '新闻']),
            
            # 数据平台类
            ('https://data.stats.gov.cn/easyquery.htm', '统计数据查询', 1, ['统计', '查询']),
            ('http://data.stats.gov.cn/', '数据中心', 1, ['数据', '统计']),
        ]
    
    def fetch_page(self, url, name, keywords):
        """获取页面"""
        print(f"  📄 正在爬取: {name}")
        print(f"     URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                content = response.read()
                
                # 解码
                decoded = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']:
                    try:
                        decoded = content.decode(encoding)
                        break
                    except:
                        continue
                
                if not decoded:
                    decoded = content.decode('utf-8', errors='ignore')
                
                # 提取关键词
                found_keywords = []
                for keyword in keywords:
                    if keyword.lower() in decoded.lower():
                        found_keywords.append(keyword)
                
                # 提取链接
                links = []
                link_pattern = r'href=["\']([^"\']*(?:pdf|xls|xlsx|csv|doc)["\']([^"\']*))["\']'
                matches = re.findall(link_pattern, decoded, re.IGNORECASE)
                for match in matches[:5]:
                    links.append(match[0] if isinstance(match, tuple) else match)
                
                print(f"     ✅ 成功 ({len(content)} 字节, {len(found_keywords)} 关键词, {len(links)} 下载链接)")
                
                return {
                    'status': 'success',
                    'url': url,
                    'name': name,
                    'size': len(content),
                    'keywords_found': found_keywords,
                    'download_links': links,
                    'content': decoded[:5000],
                    'timestamp': datetime.now().isoformat()
                }
        
        except urllib.error.HTTPError as e:
            print(f"     ❌ HTTP错误: {e.code}")
            return {
                'status': 'error',
                'url': url,
                'name': name,
                'error': f'HTTP {e.code}',
                'timestamp': datetime.now().isoformat()
            }
        
        except urllib.error.URLError as e:
            print(f"     ❌ URL错误: {str(e.reason)[:50]}")
            return {
                'status': 'error',
                'url': url,
                'name': name,
                'error': str(e.reason),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"     ❌ 错误: {str(e)[:50]}")
            return {
                'status': 'error',
                'url': url,
                'name': name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run(self):
        """运行爬虫"""
        print("=" * 70)
        print("🚀 扩展版网络爬虫启动")
        print("=" * 70)
        print(f"目标: 爬取 {len(self.sources)} 个网站")
        print(f"按优先级排序: 优先级1 ({sum(1 for _, _, p, _ in self.sources if p == 1)}个)")
        print(f"               优先级2 ({sum(1 for _, _, p, _ in self.sources if p == 2)}个)")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        results = []
        
        # 按优先级排序
        sorted_sources = sorted(self.sources, key=lambda x: x[2])
        
        for i, (url, name, priority, keywords) in enumerate(sorted_sources, 1):
            print(f"\n[{i}/{len(self.sources)}] 优先级{priority}")
            
            result = self.fetch_page(url, name, keywords)
            results.append(result)
            
            if result['status'] == 'success':
                self.stats['crawled'] += 1
                self.stats['data_size'] += result['size']
                self.stats['sources'][name] = {
                    'status': 'success',
                    'size': result['size'],
                    'keywords': result['keywords_found'],
                    'links': result['download_links']
                }
            else:
                self.stats['failed'] += 1
                self.stats['sources'][name] = {
                    'status': 'error',
                    'error': result['error']
                }
            
            # 礼貌延迟
            time.sleep(2)
        
        # 保存结果
        self.save_results(results)
        
        # 生成报告
        report = self.generate_report(results)
        print(report)
        
        return report
    
    def save_results(self, results):
        """保存结果"""
        # 保存日志
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': [
                {
                    'name': r['name'],
                    'url': r['url'],
                    'status': r['status'],
                    'size': r.get('size', 0),
                    'keywords': r.get('keywords_found', []),
                    'timestamp': r['timestamp']
                }
                for r in results
            ]
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        # 保存成功的内容
        for result in results:
            if result['status'] == 'success':
                filename = f"{result['name']}_{datetime.now().strftime('%H%M%S')}.txt"
                filepath = os.path.join(self.data_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"来源: {result['name']}\n")
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"时间: {result['timestamp']}\n")
                    f.write(f"大小: {result['size']} 字节\n")
                    f.write(f"关键词: {', '.join(result['keywords_found'])}\n")
                    if result['download_links']:
                        f.write(f"下载链接: {len(result['download_links'])}个\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(result['content'])
    
    def generate_report(self, results):
        """生成报告"""
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        lines = [
            "=" * 70,
            "📊 扩展爬虫完成报告",
            "=" * 70,
            f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"持续时间: {elapsed:.1f}秒",
            "",
            "📈 统计信息:",
            f"  爬取成功: {self.stats['crawled']}个",
            f"  爬取失败: {self.stats['failed']}个",
            f"  成功率: {self.stats['crawled']/(self.stats['crawled']+self.stats['failed'])*100:.1f}%",
            f"  数据量: {self.stats['data_size']:,}字节 ({self.stats['data_size']/1024:.1f}KB)",
            f"  平均速度: {(self.stats['crawled']+self.stats['failed'])/elapsed:.2f} 页/秒" if elapsed > 0 else "",
            "",
            "📊 数据源分类:",
            "",
            "优先级1 (核心数据源):",
        ]
        
        # 优先级1结果
        for r in results:
            if r.get('status') == 'success' and '优先级1' in f"[{results.index(r)+1}/{len(results)}]":
                lines.append(f"  ✅ {r['name']}: {r['size']}字节, {len(r['keywords_found'])}关键词")
        
        lines.append("\n优先级2 (补充数据源):")
        
        # 优先级2结果
        for r in results:
            if r.get('status') == 'success' and '优先级2' in f"[{results.index(r)+1}/{len(results)}]":
                lines.append(f"  ✅ {r['name']}: {r['size']}字节, {len(r['keywords_found'])}关键词")
        
        lines.extend([
            "",
            "❌ 失败的数据源:",
        ])
        
        # 失败的结果
        for r in results:
            if r['status'] == 'error':
                lines.append(f"  ❌ {r['name']}: {r['error'][:50]}")
        
        lines.extend([
            "",
            "=" * 70,
            "✅ 爬取完成！",
            f"📁 数据保存: {self.data_dir}",
            f"📊 日志文件: {self.log_file}",
            "",
            "💡 发现的关键词:",
        ])
        
        # 汇总关键词
        all_keywords = []
        for r in results:
            if r['status'] == 'success':
                all_keywords.extend(r['keywords_found'])
        
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        for keyword, count in keyword_counts.most_common(10):
            lines.append(f"   {keyword}: {count}次")
        
        lines.extend([
            "",
            "🔗 发现的下载链接:",
            f"   共发现 {sum(len(r.get('download_links', [])) for r in results if r['status'] == 'success')} 个下载链接",
        ])
        
        lines.append("=" * 70)
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = ExpandedCrawler(base_dir)
    
    report = crawler.run()
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'expanded_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()