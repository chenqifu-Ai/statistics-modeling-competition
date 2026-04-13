#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
省级数据收集爬虫 - 收集全国各省统计数据
"""

import os
import json
import time
import urllib.request
from datetime import datetime

class ProvinceDataCrawler:
    """省级数据收集爬虫"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'province_crawled')
        self.log_file = os.path.join(base_dir, 'data', 'province_crawler_log.json')
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.stats = {
            'crawled': 0,
            'failed': 0,
            'data_size': 0,
            'start_time': None
        }
        
        # 全国31个省市统计局和卫健委
        self.provinces = [
            # 直辖市
            ('北京', 'http://tjj.beijing.gov.cn/', 'http://wjw.beijing.gov.cn/'),
            ('上海', 'http://tjj.sh.gov.cn/', 'http://wsjkw.sh.gov.cn/'),
            ('天津', 'http://stats.tj.gov.cn/', 'http://wjw.tj.gov.cn/'),
            ('重庆', 'http://tjj.cq.gov.cn/', 'http://wsjkw.cq.gov.cn/'),
            
            # 省份
            ('广东', 'http://stats.gd.gov.cn/', 'http://wsjkw.gd.gov.cn/'),
            ('江苏', 'http://tjj.jiangsu.gov.cn/', 'http://wjw.jiangsu.gov.cn/'),
            ('浙江', 'http://tjj.zj.gov.cn/', 'http://wsjkw.zj.gov.cn/'),
            ('山东', 'http://tjj.shandong.gov.cn/', 'http://wsjkw.shandong.gov.cn/'),
            ('河南', 'http://tjj.henan.gov.cn/', 'http://wsjkw.henan.gov.cn/'),
            ('四川', 'http://tjj.sc.gov.cn/', 'http://wsjkw.sc.gov.cn/'),
            ('湖北', 'http://tjj.hubei.gov.cn/', 'http://wsjkw.hubei.gov.cn/'),
            ('湖南', 'http://tjj.hunan.gov.cn/', 'http://wsjkw.hunan.gov.cn/'),
            ('福建', 'http://tjj.fj.gov.cn/', 'http://wsjkw.fj.gov.cn/'),
            ('安徽', 'http://tjj.ah.gov.cn/', 'http://wjw.ah.gov.cn/'),
            ('河北', 'http://tjj.hebei.gov.cn/', 'http://wsjkw.hebei.gov.cn/'),
            ('陕西', 'http://tjj.shaanxi.gov.cn/', 'http://wsjkw.shaanxi.gov.cn/'),
            ('辽宁', 'http://tjj.ln.gov.cn/', 'http://wsjkw.ln.gov.cn/'),
            ('江西', 'http://tjj.jx.gov.cn/', 'http://wsjkw.jx.gov.cn/'),
            ('云南', 'http://tjj.yn.gov.cn/', 'http://wsjkw.yn.gov.cn/'),
            ('广西', 'http://tjj.gxzf.gov.cn/', 'http://wsjkw.gxzf.gov.cn/'),
            ('山西', 'http://tjj.shanxi.gov.cn/', 'http://wjw.shanxi.gov.cn/'),
            ('贵州', 'http://tjj.guizhou.gov.cn/', 'http://wsjkw.guizhou.gov.cn/'),
            ('黑龙江', 'http://tjj.hlj.gov.cn/', 'http://wsjkw.hlj.gov.cn/'),
            ('吉林', 'http://tjj.jl.gov.cn/', 'http://wsjkw.jl.gov.cn/'),
            ('甘肃', 'http://tjj.gansu.gov.cn/', 'http://wsjkw.gansu.gov.cn/'),
            ('内蒙古', 'http://tjj.nm.gov.cn/', 'http://wsjkw.nm.gov.cn/'),
            ('新疆', 'http://tjj.xinjiang.gov.cn/', 'http://wjw.xinjiang.gov.cn/'),
            ('宁夏', 'http://tjj.nx.gov.cn/', 'http://wsjkw.nx.gov.cn/'),
            ('青海', 'http://tjj.qh.gov.cn/', 'http://wsjkw.qh.gov.cn/'),
            ('西藏', 'http://tjj.xizang.gov.cn/', 'http://wsjkw.xizang.gov.cn/'),
            ('海南', 'http://tjj.hainan.gov.cn/', 'http://wsjkw.hainan.gov.cn/'),
        ]
    
    def fetch_page(self, url, name):
        """获取页面"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                content = response.read()
                
                # 解码
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
                    'name': name,
                    'url': url,
                    'size': len(content),
                    'content': decoded[:3000],
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"     ❌ 失败: {str(e)[:50]}")
            
            return {
                'status': 'error',
                'name': name,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run(self):
        """运行爬虫"""
        print("=" * 70)
        print("🗺️ 省级数据收集爬虫启动")
        print("=" * 70)
        print(f"目标: 收集 {len(self.provinces)} 个省市的统计局和卫健委数据")
        print(f"数据源: {len(self.provinces) * 2} 个网站")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        results = []
        
        for i, (province, stats_url, health_url) in enumerate(self.provinces, 1):
            print(f"\n[{i}/{len(self.provinces)}] {province}")
            
            # 爬取统计局
            print(f"  📊 {province}统计局")
            stats_result = self.fetch_page(stats_url, f"{province}统计局")
            results.append(stats_result)
            
            if stats_result['status'] == 'success':
                self.stats['crawled'] += 1
                self.stats['data_size'] += stats_result['size']
            else:
                self.stats['failed'] += 1
            
            time.sleep(1.5)
            
            # 爬取卫健委
            print(f"  🏥 {province}卫健委")
            health_result = self.fetch_page(health_url, f"{province}卫健委")
            results.append(health_result)
            
            if health_result['status'] == 'success':
                self.stats['crawled'] += 1
                self.stats['data_size'] += health_result['size']
            else:
                self.stats['failed'] += 1
            
            time.sleep(1.5)
        
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
                    'size': r.get('size', 0)
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
            "📊 省级数据收集完成报告",
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
            "📊 成功的省市:",
        ]
        
        # 成功的省市
        for r in results:
            if r['status'] == 'success':
                lines.append(f"  ✅ {r['name']}: {r['size']}字节")
        
        lines.extend([
            "",
            "❌ 失败的省市:",
        ])
        
        # 失败的省市
        for r in results:
            if r['status'] == 'error':
                lines.append(f"  ❌ {r['name']}: {r['error'][:40]}")
        
        lines.extend([
            "",
            "=" * 70,
            "✅ 爬取完成！",
            f"📁 数据保存在: {self.data_dir}",
            f"📊 日志文件: {self.log_file}",
            "=" * 70
        ])
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    crawler = ProvinceDataCrawler(base_dir)
    
    report = crawler.run()
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'province_crawl_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()