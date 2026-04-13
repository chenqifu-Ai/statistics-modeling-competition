#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计数据下载器 - 专门下载可直接用于建模的数据文件
只收集CSV、Excel、统计年鉴PDF等真实数据
"""

import os
import json
import time
import urllib.request
import urllib.error
import re
from datetime import datetime

class StatisticalDataDownloader:
    """统计数据下载器 - 只下载真实数据文件"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data', 'statistical_data')
        self.download_dir = os.path.join(self.data_dir, 'downloads')
        self.log_file = os.path.join(self.data_dir, 'download_log.json')
        
        # 创建目录
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(os.path.join(self.download_dir, 'yearbooks'), exist_ok=True)
        os.makedirs(os.path.join(self.download_dir, 'reports'), exist_ok=True)
        os.makedirs(os.path.join(self.download_dir, 'datasets'), exist_ok=True)
        
        self.stats = {
            'total_attempts': 0,
            'downloads_success': 0,
            'downloads_failed': 0,
            'data_size': 0,
            'files_downloaded': [],
            'start_time': None
        }
        
        # 真实统计数据源 - 优先级从高到低
        self.data_sources = [
            # ===== 第一优先级：官方统计年鉴（直接数据） =====
            {
                'name': '中国统计年鉴',
                'type': 'yearbook',
                'priority': 1,
                'urls': [
                    'http://www.stats.gov.cn/sj/ndsj/2023/indexeh.htm',
                    'http://www.stats.gov.cn/sj/ndsj/2022/indexeh.htm',
                    'http://www.stats.gov.cn/sj/ndsj/2021/indexeh.htm',
                ],
                'description': '国家统计局年度统计年鉴',
                'data_type': '年度统计',
                'keywords': ['统计年鉴', '年度数据', '国民经济'],
            },
            {
                'name': '卫生健康统计年鉴',
                'type': 'yearbook',
                'priority': 1,
                'urls': [
                    'http://www.nhc.gov.cn/wjweb/njbg.shtml',
                ],
                'description': '卫生健康委员会统计年鉴',
                'data_type': '卫生统计',
                'keywords': ['卫生健康', '统计年鉴', '医疗'],
            },
            
            # ===== 第二优先级：官方数据平台（可下载数据） =====
            {
                'name': '国家数据平台',
                'type': 'platform',
                'priority': 2,
                'urls': [
                    'https://data.stats.gov.cn/',
                ],
                'description': '国家统计局官方数据平台',
                'data_type': '在线数据',
                'keywords': ['统计数据', '国民经济', '社会统计'],
                'api_endpoint': 'https://data.stats.gov.cn/api.htm',
            },
            {
                'name': '中医药管理局数据',
                'type': 'platform',
                'priority': 2,
                'urls': [
                    'http://www.satcm.gov.cn/',
                ],
                'description': '中医药管理局统计数据',
                'data_type': '中医药统计',
                'keywords': ['中医药', '统计', '发展'],
            },
            
            # ===== 第三优先级：省市统计局（地方数据） =====
            {
                'name': '北京市统计局',
                'type': 'regional',
                'priority': 3,
                'urls': [
                    'http://tjj.beijing.gov.cn/',
                ],
                'description': '北京市统计年鉴',
                'data_type': '地方统计',
                'keywords': ['北京', '统计年鉴'],
            },
            {
                'name': '上海市统计局',
                'type': 'regional',
                'priority': 3,
                'urls': [
                    'http://tjj.sh.gov.cn/',
                ],
                'description': '上海市统计年鉴',
                'data_type': '地方统计',
                'keywords': ['上海', '统计年鉴'],
            },
            {
                'name': '广东省统计局',
                'type': 'regional',
                'priority': 3,
                'urls': [
                    'http://stats.gd.gov.cn/',
                ],
                'description': '广东省统计年鉴',
                'data_type': '地方统计',
                'keywords': ['广东', '统计年鉴'],
            },
        ]
    
    def download_file(self, url, filename, source_name):
        """下载文件"""
        print(f"  📥 下载: {filename}")
        print(f"     URL: {url}")
        
        filepath = os.path.join(self.download_dir, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read()
                
                # 检查文件大小
                if len(content) < 1000:  # 小于1KB可能是错误页面
                    print(f"     ⚠️ 文件太小 ({len(content)}字节)，可能不是真实数据")
                    return None
                
                # 保存文件
                with open(filepath, 'wb') as f:
                    f.write(content)
                
                print(f"     ✅ 成功下载: {len(content)}字节")
                
                return {
                    'status': 'success',
                    'filename': filename,
                    'url': url,
                    'source': source_name,
                    'size': len(content),
                    'filepath': filepath,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"     ❌ 下载失败: {str(e)[:50]}")
            return None
    
    def extract_download_links(self, url, source_name):
        """从网页提取下载链接"""
        print(f"  🔍 扫描下载链接: {source_name}")
        print(f"     URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        request = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
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
                
                # 提取下载链接
                pdf_links = re.findall(r'href=["\']([^"\']*\.pdf)["\']', decoded, re.IGNORECASE)
                excel_links = re.findall(r'href=["\']([^"\']*\.(?:xls|xlsx|csv))["\']', decoded, re.IGNORECASE)
                data_links = re.findall(r'href=["\']([^"\']*(?:download|data|file|dataset)[^"\']*)["\']', decoded, re.IGNORECASE)
                
                # 转换为绝对URL
                base_url = '/'.join(url.split('/')[:3])
                
                absolute_links = {
                    'pdf': [link if link.startswith('http') else base_url + link for link in pdf_links[:10]],
                    'excel': [link if link.startswith('http') else base_url + link for link in excel_links[:10]],
                    'data': [link if link.startswith('http') else base_url + link for link in data_links[:10]],
                }
                
                print(f"     发现: {len(absolute_links['pdf'])}个PDF, {len(absolute_links['excel'])}个Excel, {len(absolute_links['data'])}个数据链接")
                
                return absolute_links
        
        except Exception as e:
            print(f"     ❌ 扫描失败: {str(e)[:50]}")
            return {'pdf': [], 'excel': [], 'data': []}
    
    def run(self):
        """运行下载器"""
        print("=" * 80)
        print("📊 统计数据下载器启动")
        print("=" * 80)
        print("目标: 下载真实数据文件（PDF、Excel、CSV等）")
        print(f"数据源: {len(self.data_sources)}个")
        print()
        
        self.stats['start_time'] = datetime.now().isoformat()
        
        # 按优先级处理
        for priority in [1, 2, 3]:
            sources = [s for s in self.data_sources if s['priority'] == priority]
            
            if not sources:
                continue
            
            print(f"\n{'='*80}")
            print(f"优先级 {priority} - {', '.join(set(s['type'] for s in sources))}")
            print(f"{'='*80}")
            
            for source in sources:
                print(f"\n📂 {source['name']} ({source['data_type']})")
                print(f"   描述: {source['description']}")
                print(f"   关键词: {', '.join(source['keywords'])}")
                
                # 扫描每个URL
                for url in source['urls']:
                    self.stats['total_attempts'] += 1
                    
                    # 提取下载链接
                    links = self.extract_download_links(url, source['name'])
                    
                    # 尝试下载Excel文件（优先）
                    for excel_url in links['excel'][:3]:  # 只下载前3个
                        filename = os.path.basename(excel_url.split('?')[0])
                        if not filename:
                            filename = f"{source['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        
                        result = self.download_file(excel_url, filename, source['name'])
                        
                        if result:
                            self.stats['downloads_success'] += 1
                            self.stats['data_size'] += result['size']
                            self.stats['files_downloaded'].append(result)
                        else:
                            self.stats['downloads_failed'] += 1
                        
                        time.sleep(1)
                    
                    # 尝试下载PDF文件
                    for pdf_url in links['pdf'][:2]:  # 只下载前2个
                        filename = os.path.basename(pdf_url.split('?')[0])
                        if not filename:
                            filename = f"{source['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        
                        result = self.download_file(pdf_url, filename, source['name'])
                        
                        if result:
                            self.stats['downloads_success'] += 1
                            self.stats['data_size'] += result['size']
                            self.stats['files_downloaded'].append(result)
                        else:
                            self.stats['downloads_failed'] += 1
                        
                        time.sleep(1)
        
        # 保存日志
        self.save_log()
        
        # 生成报告
        report = self.generate_report()
        print(report)
        
        return report
    
    def save_log(self):
        """保存日志"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self):
        """生成报告"""
        elapsed = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        lines = [
            "=" * 80,
            "📊 统计数据下载报告",
            "=" * 80,
            f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"持续时间: {elapsed:.1f}秒",
            "",
            "📈 下载统计:",
            f"  尝试次数: {self.stats['total_attempts']}次",
            f"  成功下载: {self.stats['downloads_success']}个文件",
            f"  下载失败: {self.stats['downloads_failed']}个文件",
            f"  总数据量: {self.stats['data_size']:,}字节 ({self.stats['data_size']/1024/1024:.2f}MB)",
            "",
            "📥 已下载文件:",
        ]
        
        for file_info in self.stats['files_downloaded']:
            lines.append(f"  ✅ {file_info['filename']}")
            lines.append(f"     来源: {file_info['source']}")
            lines.append(f"     大小: {file_info['size']:,}字节")
        
        lines.extend([
            "",
            "=" * 80,
            "✅ 下载完成！",
            f"📁 文件保存在: {self.download_dir}",
            f"📊 日志文件: {self.log_file}",
            "",
            "💡 重要提示:",
            "  1. 这些是真实的数据文件，可直接用于建模",
            "  2. Excel文件可能包含表格数据",
            "  3. PDF文件可能需要手动提取表格",
            "  4. 建议优先使用Excel/CSV文件",
            "=" * 80
        ])
        
        return "\n".join(lines)

def main():
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    downloader = StatisticalDataDownloader(base_dir)
    
    report = downloader.run()
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'statistical_data_download_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存: {report_file}")

if __name__ == '__main__':
    main()