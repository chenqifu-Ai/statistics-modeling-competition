#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级数据收集工具 - 自动化网络爬虫版
支持多数据源并行爬取、智能解析、自动验证
"""

import os
import json
import time
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class AdvancedDataCollector:
    """高级数据收集器 - 支持多源并行爬取"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.cache_dir = os.path.join(base_dir, 'data', 'cache')
        self.raw_dir = os.path.join(base_dir, 'data', 'raw', 'official')
        self.log_file = os.path.join(base_dir, 'data', 'advanced_collection_log.json')
        self.lock = threading.Lock()
        
        # 创建必要的目录
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        
        # 数据源配置
        self.data_sources = {
            'stats_gov': {
                'name': '国家统计局',
                'base_url': 'https://www.stats.gov.cn/',
                'priority': 1,
                'data_types': {
                    'yearbook': {
                        'name': '中国统计年鉴',
                        'url': 'https://www.stats.gov.cn/sj/ndsj/',
                        'format': 'PDF/Excel',
                        'priority': 1
                    },
                    'health': {
                        'name': '卫生健康统计',
                        'url': 'https://www.stats.gov.cn/sj/ndsj/2024/indexch.htm',
                        'format': 'Excel',
                        'priority': 1
                    }
                }
            },
            'nhc': {
                'name': '国家卫健委',
                'base_url': 'http://www.nhc.gov.cn/',
                'priority': 2,
                'data_types': {
                    'yearbook': {
                        'name': '卫生健康统计年鉴',
                        'url': 'http://www.nhc.gov.cn/wjw/jktnr/list.shtml',
                        'format': 'PDF/Excel',
                        'priority': 2
                    },
                    'tcm_hospital': {
                        'name': '中医医院统计',
                        'url': 'http://www.nhc.gov.cn/wjw/jktnr/list.shtml',
                        'format': 'Excel',
                        'priority': 2
                    }
                }
            },
            'satcm': {
                'name': '中医药管理局',
                'base_url': 'http://www.satcm.gov.cn/',
                'priority': 3,
                'data_types': {
                    'report': {
                        'name': '中医药事业发展报告',
                        'url': 'http://www.satcm.gov.cn/a/a3/benbugonggao/',
                        'format': 'PDF',
                        'priority': 3
                    },
                    'statistics': {
                        'name': '中医医院专项统计',
                        'url': 'http://www.satcm.gov.cn/a/a3/benbugonggao/',
                        'format': 'Excel',
                        'priority': 3
                    }
                }
            },
            'nhsa': {
                'name': '国家医保局',
                'base_url': 'http://www.nhsa.gov.cn/',
                'priority': 4,
                'data_types': {
                    'fund': {
                        'name': '医保基金运行报告',
                        'url': 'http://www.nhsa.gov.cn/col/col1854/',
                        'format': 'PDF',
                        'priority': 4
                    },
                    'tcm_payment': {
                        'name': '中医药医保支付',
                        'url': 'http://www.nhsa.gov.cn/col/col1854/',
                        'format': 'Excel',
                        'priority': 4
                    }
                }
            }
        }
        
        # 爬取配置
        self.config = {
            'max_workers': 4,
            'timeout': 30,
            'retry_times': 3,
            'retry_delay': 5,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'cache_enabled': True,
            'cache_expire': 86400  # 24小时
        }
    
    def get_cache_key(self, url):
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def load_cache(self, cache_key):
        """加载缓存"""
        if not self.config['cache_enabled']:
            return None
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                # 检查缓存是否过期
                if time.time() - cache_data['timestamp'] < self.config['cache_expire']:
                    return cache_data['data']
        return None
    
    def save_cache(self, cache_key, data):
        """保存缓存"""
        if not self.config['cache_enabled']:
            return
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def fetch_url(self, url, retry_count=0):
        """获取URL内容"""
        cache_key = self.get_cache_key(url)
        
        # 尝试从缓存加载
        cached_data = self.load_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 设置请求头
        headers = {
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=self.config['timeout']) as response:
                content = response.read()
                
                # 尝试解码
                try:
                    decoded_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        decoded_content = content.decode('gbk')
                    except UnicodeDecodeError:
                        decoded_content = content.decode('gb2312', errors='ignore')
                
                result = {
                    'status': 'success',
                    'url': url,
                    'content': decoded_content,
                    'size': len(content),
                    'timestamp': datetime.now().isoformat()
                }
                
                # 保存到缓存
                self.save_cache(cache_key, result)
                
                return result
                
        except urllib.error.HTTPError as e:
            if retry_count < self.config['retry_times']:
                time.sleep(self.config['retry_delay'])
                return self.fetch_url(url, retry_count + 1)
            return {
                'status': 'error',
                'url': url,
                'error': f'HTTP Error: {e.code}',
                'timestamp': datetime.now().isoformat()
            }
        
        except urllib.error.URLError as e:
            if retry_count < self.config['retry_times']:
                time.sleep(self.config['retry_delay'])
                return self.fetch_url(url, retry_count + 1)
            return {
                'status': 'error',
                'url': url,
                'error': f'URL Error: {e.reason}',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'url': url,
                'error': f'Exception: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def parse_webpage(self, content, patterns):
        """解析网页内容"""
        # 简单的文本解析（不依赖第三方库）
        results = []
        
        for pattern in patterns:
            if pattern['type'] == 'text':
                # 文本搜索
                if pattern['keyword'] in content:
                    results.append({
                        'type': 'text_match',
                        'keyword': pattern['keyword'],
                        'found': True
                    })
            
            elif pattern['type'] == 'link':
                # 链接提取（简单正则替代）
                import re
                links = re.findall(r'href=["\']([^"\']*' + pattern['keyword'] + r'[^"\']*)["\']', content)
                for link in links:
                    results.append({
                        'type': 'link',
                        'url': link,
                        'keyword': pattern['keyword']
                    })
        
        return results
    
    def collect_source(self, source_key, data_type_key=None):
        """收集单个数据源"""
        source = self.data_sources.get(source_key)
        if not source:
            return None
        
        results = {
            'source': source_key,
            'name': source['name'],
            'timestamp': datetime.now().isoformat(),
            'data_types': []
        }
        
        # 如果指定了数据类型，只收集该类型
        if data_type_key:
            data_types_to_collect = {data_type_key: source['data_types'].get(data_type_key)}
        else:
            data_types_to_collect = source['data_types']
        
        for dtype_key, dtype_config in data_types_to_collect.items():
            if not dtype_config:
                continue
            
            print(f"  📊 收集 {source['name']} - {dtype_config['name']}...")
            
            # 获取网页内容
            result = self.fetch_url(dtype_config['url'])
            
            if result['status'] == 'success':
                # 解析内容
                patterns = [
                    {'type': 'text', 'keyword': '统计'},
                    {'type': 'text', 'keyword': '年鉴'},
                    {'type': 'text', 'keyword': '数据'},
                    {'type': 'link', 'keyword': '.pdf'},
                    {'type': 'link', 'keyword': '.xls'}
                ]
                
                parsed_results = self.parse_webpage(result['content'], patterns)
                
                dtype_result = {
                    'type': dtype_key,
                    'name': dtype_config['name'],
                    'status': 'success',
                    'url': dtype_config['url'],
                    'size': result['size'],
                    'parsed_items': len(parsed_results),
                    'download_links': [r for r in parsed_results if r['type'] == 'link']
                }
            else:
                dtype_result = {
                    'type': dtype_key,
                    'name': dtype_config['name'],
                    'status': 'error',
                    'url': dtype_config['url'],
                    'error': result.get('error', 'Unknown error')
                }
            
            results['data_types'].append(dtype_result)
            time.sleep(1)  # 避免频繁请求
        
        return results
    
    def collect_all_parallel(self):
        """并行收集所有数据源"""
        print("=" * 70)
        print("🚀 高级数据收集器 - 并行爬取模式")
        print("=" * 70)
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # 提交所有任务
            future_to_source = {
                executor.submit(self.collect_source, source_key): source_key
                for source_key in self.data_sources.keys()
            }
            
            # 收集结果
            for future in as_completed(future_to_source):
                source_key = future_to_source[future]
                try:
                    result = future.result()
                    if result:
                        all_results.append(result)
                        print(f"✅ {result['name']} 收集完成")
                except Exception as e:
                    print(f"❌ {source_key} 收集失败: {str(e)}")
        
        # 保存收集日志
        self.save_collection_log(all_results)
        
        # 生成报告
        report = self.generate_report(all_results)
        
        return report
    
    def save_collection_log(self, results):
        """保存收集日志"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'total_sources': len(results),
            'results': results
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self, results):
        """生成收集报告"""
        report_lines = [
            "=" * 70,
            "📊 高级数据收集报告",
            "=" * 70,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"数据源数量: {len(results)}个",
            ""
        ]
        
        success_count = 0
        error_count = 0
        
        for result in results:
            status_emoji = "✅" if any(dt['status'] == 'success' for dt in result['data_types']) else "❌"
            
            report_lines.append(f"{status_emoji} {result['name']}:")
            
            for dtype in result['data_types']:
                status = "成功" if dtype['status'] == 'success' else "失败"
                status_icon = "✅" if dtype['status'] == 'success' else "❌"
                
                report_lines.append(f"  {status_icon} {dtype['name']}: {status}")
                
                if dtype['status'] == 'success':
                    success_count += 1
                    report_lines.append(f"     📦 数据大小: {dtype['size']} 字节")
                    if dtype.get('download_links'):
                        report_lines.append(f"     🔗 发现链接: {len(dtype['download_links'])}个")
                else:
                    error_count += 1
                    report_lines.append(f"     ⚠️ 错误: {dtype.get('error', 'Unknown')}")
            
            report_lines.append("")
        
        report_lines.extend([
            "=" * 70,
            "📊 收集统计:",
            f"  成功: {success_count}个",
            f"  失败: {error_count}个",
            f"  成功率: {success_count/(success_count+error_count)*100:.1f}%",
            "",
            "💡 下一步操作:",
            "1. 检查收集结果日志",
            "2. 手动下载无法自动获取的数据",
            "3. 使用离线数据获取指南补充数据",
            "4. 进行数据验证和整理",
            "=" * 70
        ])
        
        return "\n".join(report_lines)

def main():
    """主函数"""
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    collector = AdvancedDataCollector(base_dir)
    
    # 并行收集所有数据源
    report = collector.collect_all_parallel()
    print(report)
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'advanced_collection_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存至: {report_file}")

if __name__ == '__main__':
    main()