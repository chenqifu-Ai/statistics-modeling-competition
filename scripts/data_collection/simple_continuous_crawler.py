#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版持续爬虫 - 稳定可靠的数据收集
"""

import os
import json
import time
import urllib.request
import urllib.error
import re
from datetime import datetime

class SimpleContinuousCrawler:
    """简化版持续爬虫"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'simple_crawled')
        self.log_file = os.path.join(base_dir, 'data', 'simple_crawler_log.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.stats = {
            'crawled': 0,
            'failed': 0,
            'data_size': 0,
            'start_time': None
        }
        
        # 扩展数据源（简化版）
        self.sources = [
            # 省市统计局
            ('http://tjj.beijing.gov.cn/', '北京统计局', 1),
            ('http://tjj.sh.gov.cn/', '上海统计局', 1),
            ('http://stats.gd.gov.cn/', '广东统计局', 1),
            
            # 省市卫健委
            ('http://wjw.beijing.gov.cn/', '北京卫健委', 1),
            ('http://wsjkw.sh.gov.cn/', '上海卫健委', 1),
            ('http://wsjkw.gd.gov.cn/', '广东卫健委', 1),
            
            # 中医药大学
            ('http://www.bucm.edu.cn/', '北京中医药大学', 2),
            ('http://www.shutcm.edu.cn/', '上海中医药大学', 2),
            ('http://www.gztcm.edu.cn/', '广州中医药大学', 2),
            
            # 数据平台
            ('https://data.stats.gov.cn/', '国家数据平台', 1),
            ('http://www.hshw.gov.cn/', '健康上海', 2),
            
            # 新闻媒体
            ('http://www.cntcm.com.cn/', '中国中医药报', 3),
        ]
    
    def fetch_page(self, url, name):
        """获取页面"""
        print(f"  📄 正在爬取: {name}")
        print(f"     URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                content = response.read()
                
                # 尝试解码
                decoded = None
                for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
                    try:
                        decoded = content.decode(encoding)
                        break
                    except:
                        continue
                
                if not decoded:
                    decoded = content.decode('utf-8', errors='ignore')
                
                print(f"     ✅ 成功 ({len(content)} 字节)")
                
                return {
                    'status': 'success',
                    'url': url,
                    'name': name,
                    'size': len(content),
                    'content': decoded[:5000],  # 只保存前5000字符
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"     ❌ 失败: {str(e)[:50]}")
            
            return {
                'status': 'error',
                'url': url,
                'name': name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run(self, max_count=20):
        """运行爬虫"""
        print("=" * 70)
        print("🔄 简化版持续爬虫启动")
        print("=" * 70)
        print(f"目标: 爬取 {min(len(self.sources), max_count)} 个网站")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        
        results = []
        count = 0
        
        for url, name, priority in self.sources[:max_count]:
            count += 1
            print(f"\n[{count}/{min(len(self.sources), max_count)}]")
            
            result = self.fetch_page(url, name)
            results.append(result)
            
            if result['status'] == 'success':
                self.stats['crawled'] += 1
                self.stats['data_size'] += result['size']
            else:
                self.stats['failed'] += 1
            
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
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': [
                {
                    'name': r['name'],
                    'url': r['url'],
                    'status': r['status'],
                    'size': r.get('size', 0),
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
                    f.write("=" * 50 + "\n\n")
                    f.write(result['content'])
    
    def generate_report(self, results):
        """生成报告"""
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        lines = [
            "=" * 70,
            "📊 持续爬虫完成报告",
            "=" * 70,
            f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"持续时间: {elapsed:.1f}秒",
            "",
            "📈 统计信息:",
            f"  爬取成功: {self.stats['crawled']}个",
            f"  爬取失败: {self.stats['failed']}个",
            f"  成功率: {self.stats['crawled']/(self.stats['crawled']+self.stats['failed'])*100:.1f}%",
            f"  数据量: {self.stats['data_size']:,}字节 ({self.stats['data_size']/1024:.1f}KB)",
            "",
            "📋 详细结果:",
            ""
        ]
        
        for result in results:
            status = "✅" if result['status'] == 'success' else "❌"
            lines.append(f"{status} {result['name']}")
            
            if result['status'] == 'success':
                lines.append(f"   大小: {result['size']} 字节")
            else:
                lines.append(f"   错误: {result.get('error', 'Unknown')[:50]}")
            lines.append("")
        
        lines.extend([
            "=" * 70,
            "✅ 爬取完成！",
            f"📁 数据保存在: {self.data_dir}",
            f"📊 日志文件: {self.log_file}",
            "=" * 70
        ])
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = SimpleContinuousCrawler(base_dir)
    
    # 爬取20个网站
    report = crawler.run(max_count=20)
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'simple_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()