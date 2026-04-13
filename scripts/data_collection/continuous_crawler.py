#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续网络爬虫 - 自动化数据挖掘系统
支持持续爬取、智能调度、增量更新
"""

import os
import json
import time
import threading
import queue
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import re

class ContinuousCrawler:
    """持续网络爬虫系统"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'continuous_crawled')
        self.log_file = os.path.join(base_dir, 'data', 'continuous_crawler_log.json')
        self.stats_file = os.path.join(base_dir, 'data', 'crawler_stats.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 爬取队列
        self.url_queue = queue.PriorityQueue()
        self.crawled_urls = set()
        self.results = []
        self.stats = {
            'total_urls': 0,
            'crawled': 0,
            'failed': 0,
            'data_size': 0,
            'start_time': None,
            'last_update': None
        }
        
        # 扩展数据源列表
        self.expanded_sources = {
            # 核心统计类
            'stats_gov_province': {
                'name': '各省市统计局',
                'urls': [
                    'http://tjj.beijing.gov.cn/',
                    'http://tjj.sh.gov.cn/',
                    'http://stats.gd.gov.cn/',
                    'http://tjj.jiangsu.gov.cn/',
                    'http://tjj.zhejiang.gov.cn/',
                ],
                'priority': 1,
                'keywords': ['统计', '年鉴', '中医药', '医院']
            },
            
            # 卫生健康类
            'health_commission_province': {
                'name': '各省卫健委',
                'urls': [
                    'http://wjw.beijing.gov.cn/',
                    'http://wsjkw.sh.gov.cn/',
                    'http://wsjkw.gd.gov.cn/',
                    'http://wjw.jiangsu.gov.cn/',
                    'http://wsjkw.zj.gov.cn/',
                ],
                'priority': 1,
                'keywords': ['中医', '医院', '统计', '健康']
            },
            
            # 中医药专项
            'tcm_universities': {
                'name': '中医药大学',
                'urls': [
                    'http://www.bucm.edu.cn/',
                    'http://www.shutcm.edu.cn/',
                    'http://www.gztcm.edu.cn/',
                    'http://www.njucm.edu.cn/',
                    'http://www.czy.edu.cn/',
                ],
                'priority': 2,
                'keywords': ['中医药', '研究', '统计', '发展']
            },
            
            # 医疗机构
            'tcm_hospitals': {
                'name': '中医医院',
                'urls': [
                    'http://www.bucmh.com/',
                    'http://www.shutcmhospital.com/',
                    'http://www.gztcmhospital.com.cn/',
                    'http://www.njzyyy.com/',
                ],
                'priority': 2,
                'keywords': ['中医', '医疗', '统计', '服务']
            },
            
            # 学术资源
            'academic_journals': {
                'name': '学术期刊',
                'urls': [
                    'http://www.cjtcms.cn/',
                    'http://www.zgykdj.com/',
                    'http://www.cjam.whlib.cas.cn/',
                ],
                'priority': 2,
                'keywords': ['中医药', '统计', '研究', '分析']
            },
            
            # 政策法规
            'policy_sources': {
                'name': '政策法规',
                'urls': [
                    'http://www.npc.gov.cn/',
                    'http://www.gov.cn/zhengce/',
                    'http://www.satcm.gov.cn/hudongjiaoliu/',
                ],
                'priority': 1,
                'keywords': ['中医药', '政策', '规划', '发展']
            },
            
            # 数据平台
            'data_platforms': {
                'name': '数据平台',
                'urls': [
                    'https://data.stats.gov.cn/',
                    'http://www.hshw.gov.cn/',
                    'https://www.medidata.cn/',
                ],
                'priority': 1,
                'keywords': ['统计', '数据', '中医药', '医疗']
            },
            
            # 新闻媒体
            'news_media': {
                'name': '新闻媒体',
                'urls': [
                    'http://www.cntcm.com.cn/',
                    'http://www.cntcmnews.com/',
                    'http://www.zhzyw.org.cn/',
                ],
                'priority': 3,
                'keywords': ['中医药', '发展', '统计', '新闻']
            }
        }
    
    def add_urls_to_queue(self):
        """将所有URL加入队列"""
        print("\n📋 准备爬取队列...")
        
        for source_key, source_config in self.expanded_sources.items():
            for url in source_config['urls']:
                if url not in self.crawled_urls:
                    self.url_queue.put((
                        source_config['priority'],
                        url,
                        source_key,
                        source_config['keywords']
                    ))
                    self.stats['total_urls'] += 1
        
        print(f"   队列中的URL数量: {self.stats['total_urls']}")
    
    def fetch_page(self, url, retry_count=0):
        """获取页面内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                content = response.read()
                
                # 尝试解码
                for encoding in ['utf-8', 'gbk', 'gb2312']:
                    try:
                        decoded_content = content.decode(encoding)
                        break
                    except:
                        continue
                else:
                    decoded_content = content.decode('utf-8', errors='ignore')
                
                return {
                    'status': 'success',
                    'url': url,
                    'content': decoded_content,
                    'size': len(content),
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            if retry_count < 3:
                time.sleep(2)
                return self.fetch_page(url, retry_count + 1)
            
            return {
                'status': 'error',
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def extract_data(self, content, keywords):
        """提取数据"""
        extracted = []
        
        # 提取包含关键词的段落
        for keyword in keywords:
            pattern = r'[^<]*' + re.escape(keyword) + r'[^<]*'
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches[:5]:  # 只取前5个匹配
                cleaned = match.strip()
                if len(cleaned) > 20 and len(cleaned) < 500:
                    extracted.append({
                        'keyword': keyword,
                        'text': cleaned
                    })
        
        # 提取链接
        link_pattern = r'href=["\']([^"\']*(?:pdf|xls|xlsx|csv|doc)["\']([^"\']*))["\']'
        links = re.findall(link_pattern, content, re.IGNORECASE)
        
        if links:
            extracted.append({
                'type': 'download_links',
                'links': links[:10]  # 只取前10个链接
            })
        
        return extracted
    
    def crawl_url(self, priority, url, source_key, keywords):
        """爬取单个URL"""
        if url in self.crawled_urls:
            return None
        
        print(f"  📄 爬取: {url[:60]}...")
        
        result = self.fetch_page(url)
        
        crawl_result = {
            'source': source_key,
            'url': url,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'status': result['status']
        }
        
        if result['status'] == 'success':
            self.crawled_urls.add(url)
            self.stats['crawled'] += 1
            self.stats['data_size'] += result['size']
            
            # 提取数据
            extracted = self.extract_data(result['content'], keywords)
            
            crawl_result['size'] = result['size']
            crawl_result['extracted_count'] = len(extracted)
            crawl_result['extracted_data'] = extracted
            
            # 保存原始内容
            source_dir = os.path.join(self.data_dir, source_key)
            os.makedirs(source_dir, exist_ok=True)
            
            filename = f"{datetime.now().strftime('%H%M%S')}_{url.replace('/', '_')[:50]}.html"
            filepath = os.path.join(source_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            
            print(f"     ✅ 成功 ({result['size']} 字节, {len(extracted)} 个数据片段)")
        
        else:
            self.stats['failed'] += 1
            crawl_result['error'] = result.get('error', 'Unknown error')
            print(f"     ❌ 失败: {crawl_result['error']}")
        
        self.results.append(crawl_result)
        return crawl_result
    
    def save_progress(self):
        """保存进度"""
        self.stats['last_update'] = datetime.now().isoformat()
        
        # 保存统计信息
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        # 保存爬取日志
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': self.results[-100:]  # 只保存最近100条
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self):
        """生成报告"""
        if self.stats['crawled'] == 0:
            return "暂无爬取数据"
        
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        report_lines = [
            "=" * 70,
            "🔄 持续网络爬虫 - 实时报告",
            "=" * 70,
            f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"持续时间: {elapsed:.1f}秒",
            "",
            "📊 爬取统计:",
            f"  总URL数: {self.stats['total_urls']}",
            f"  已爬取: {self.stats['crawled']}",
            f"  失败: {self.stats['failed']}",
            f"  成功率: {self.stats['crawled']/(self.stats['crawled']+self.stats['failed'])*100:.1f}%",
            f"  数据量: {self.stats['data_size']:,}字节 ({self.stats['data_size']/1024/1024:.2f}MB)",
            "",
            "📈 性能指标:",
            f"  平均速度: {self.stats['crawled']/elapsed:.2f} 页/秒" if elapsed > 0 else "  平均速度: 计算中...",
            f"  数据吞吐: {self.stats['data_size']/elapsed/1024:.2f} KB/秒" if elapsed > 0 else "  数据吞吐: 计算中...",
            "",
            "📂 数据分布:",
        ]
        
        # 按数据源统计
        source_stats = {}
        for result in self.results:
            source = result.get('source', 'unknown')
            if source not in source_stats:
                source_stats[source] = {'count': 0, 'size': 0, 'success': 0}
            
            source_stats[source]['count'] += 1
            if result['status'] == 'success':
                source_stats[source]['success'] += 1
                source_stats[source]['size'] += result.get('size', 0)
        
        for source, stats in sorted(source_stats.items(), key=lambda x: x[1]['success'], reverse=True):
            success_rate = stats['success'] / stats['count'] * 100 if stats['count'] > 0 else 0
            report_lines.append(f"  {source}: {stats['success']}/{stats['count']} ({success_rate:.0f}%), {stats['size']/1024:.1f}KB")
        
        report_lines.extend([
            "",
            "✅ 爬取完成!",
            f"📁 数据已保存至: {self.data_dir}",
            f"📊 统计信息: {self.stats_file}",
            "=" * 70
        ])
        
        return "\n".join(report_lines)
    
    def run(self, max_urls=50):
        """运行持续爬虫"""
        print("=" * 70)
        print("🔄 持续网络爬虫系统启动")
        print("=" * 70)
        
        self.stats['start_time'] = datetime.now().isoformat()
        
        # 准备队列
        self.add_urls_to_queue()
        
        # 开始爬取
        print("\n🚀 开始爬取...")
        
        crawled_count = 0
        while not self.url_queue.empty() and crawled_count < max_urls:
            priority, url, source_key, keywords = self.url_queue.get()
            
            self.crawl_url(priority, url, source_key, keywords)
            crawled_count += 1
            
            # 定期保存进度
            if crawled_count % 10 == 0:
                self.save_progress()
                print(f"\n📊 进度: {crawled_count}/{max_urls}")
            
            # 礼貌延迟
            time.sleep(1)
        
        # 最终保存
        self.save_progress()
        
        # 生成报告
        report = self.generate_report()
        print("\n" + report)
        
        return report

def main():
    """主函数"""
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = ContinuousCrawler(base_dir)
    
    # 运行爬虫（最多爬取50个URL）
    report = crawler.run(max_urls=50)
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'continuous_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存至: {report_file}")

if __name__ == '__main__':
    main()