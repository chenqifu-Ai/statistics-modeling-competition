#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中医药统计数据生成器（基于公开信息）
为统计建模大赛提供参考数据集
"""

import csv
import os
from datetime import datetime

def generate_tcm_hospital_data():
    """生成中医医院基础数据"""
    years = list(range(2011, 2025))
    
    # 基于公开数据的合理估算（仅供参考）
    data = []
    for i, year in enumerate(years):
        # 中医医院数量（公开数据约在3000-6000家之间）
        hospitals = 3167 + i * 178  # 年均增长约178家
        
        # 中医床位数（公开数据约在50-100万张之间）
        beds = 524100 + i * 35700  # 年均增长约3.57万张
        
        # 中医药人员数（公开数据约在40-70万人之间）
        staff = 426870 + i * 21430  # 年均增长约2.14万人
        
        # 诊疗人次（公开数据约在5-10亿人次之间）
        visits = 5.30 + i * 0.35  # 年均增长约0.35亿人次
        
        # 出院人数（公开数据约在2000-4000万人之间）
        discharges = 2013 + i * 135  # 年均增长约135万人
        
        # 床位使用率（一般在85-92%之间）
        utilization = 85.7 + i * 0.4
        
        # 平均住院日（一般在8-12天之间）
        avg_stay = 10.2 - i * 0.13  # 逐年减少
        
        # 医疗收入（公开数据约在1000-3000亿元之间）
        medical_income = 1032 + i * 136  # 年均增长约136亿元
        
        # 医保收入（约占医疗收入的60-70%）
        insurance_income = medical_income * (0.62 + i * 0.01)
        
        data.append([
            year, hospitals, beds, staff, 
            round(visits, 2), discharges, 
            round(utilization, 1), round(avg_stay, 2),
            round(medical_income, 0), round(insurance_income, 0)
        ])
    
    return data

def generate_tcm_province_data():
    """生成各省中医药数据（示例）"""
    provinces = [
        '北京', '上海', '广东', '江苏', '浙江',
        '山东', '河南', '四川', '湖北', '湖南',
        '河北', '福建', '安徽', '辽宁', '陕西'
    ]
    
    # 2024年数据（示例）
    data = []
    for province in provinces:
        # 各省中医医院数量（估算）
        hospitals = {
            '北京': 185, '上海': 198, '广东': 420, '江苏': 385, '浙江': 295,
            '山东': 385, '河南': 355, '四川': 310, '湖北': 245, '湖南': 260,
            '河北': 275, '福建': 185, '安徽': 225, '辽宁': 205, '陕西': 195
        }
        
        # 床位数（估算）
        beds = hospitals[province] * 180  # 平均每院180张床位
        
        # 人员数（估算）
        staff = hospitals[province] * 125  # 平均每院125人
        
        # 诊疗人次（估算，万人次）
        visits = hospitals[province] * 85  # 平均每院85万人次
        
        data.append([province, hospitals[province], beds, staff, visits])
    
    return data

def generate_tcm_service_data():
    """生成中医药服务数据"""
    years = list(range(2011, 2025))
    
    data = []
    for i, year in enumerate(years):
        # 中医门诊服务
        outpatient = 5.2 + i * 0.35  # 亿人次
        
        # 中医住院服务
        inpatient = 1800 + i * 120  # 万人
        
        # 中医预防保健服务
        preventive = 1.5 + i * 0.25  # 亿人次
        
        # 中医康复服务
        rehabilitation = 800 + i * 60  # 万人
        
        # 中医养老服务
        elderly_care = 500 + i * 45  # 万人
        
        # 中医家庭医生签约
        family_doctor = 2.1 + i * 0.3  # 亿人
        
        data.append([
            year, 
            round(outpatient, 2), 
            inpatient, 
            round(preventive, 2),
            rehabilitation, 
            elderly_care, 
            round(family_doctor, 2)
        ])
    
    return data

def generate_tcm_investment_data():
    """生成中医药投入数据"""
    years = list(range(2011, 2025))
    
    data = []
    for i, year in enumerate(years):
        # 政府财政投入
        gov_investment = 850 + i * 95  # 亿元
        
        # 基础设施投资
        infra_investment = 320 + i * 42  # 亿元
        
        # 科研经费
        research_fund = 85 + i * 12  # 亿元
        
        # 人才培养投入
        training_fund = 45 + i * 6  # 亿元
        
        # 医保支付中医药
        insurance_payment = 620 + i * 75  # 亿元
        
        # 总投入
        total = gov_investment + infra_investment + research_fund + training_fund
        
        data.append([
            year, 
            round(gov_investment, 0),
            round(infra_investment, 0),
            round(research_fund, 0),
            round(training_fund, 0),
            round(insurance_payment, 0),
            round(total, 0)
        ])
    
    return data

def save_csv(filename, headers, data, directory):
    """保存CSV文件"""
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    return filepath

def main():
    """主函数"""
    print("=" * 70)
    print("🏥 中医药统计数据生成器")
    print("基于公开信息构建参考数据集")
    print("=" * 70)
    
    # 设置数据目录
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    data_dir = os.path.join(base_dir, 'data', 'generated')
    os.makedirs(data_dir, exist_ok=True)
    
    # 生成各类数据
    print("\n📊 生成中医医院基础数据...")
    hospital_data = generate_tcm_hospital_data()
    headers = ['年份', '中医医院数量', '中医床位数', '中医药人员数', 
               '诊疗人次', '出院人数', '床位使用率', '平均住院日',
               '医疗收入', '医保收入']
    file1 = save_csv('tcm_hospital_basic_2011_2024.csv', headers, hospital_data, data_dir)
    print(f"✅ 已保存: {file1}")
    
    print("\n🏥 生成各省中医药数据...")
    province_data = generate_tcm_province_data()
    headers = ['省份', '中医医院数', '床位数', '人员数', '诊疗人次']
    file2 = save_csv('tcm_province_data_2024.csv', headers, province_data, data_dir)
    print(f"✅ 已保存: {file2}")
    
    print("\n📋 生成中医药服务数据...")
    service_data = generate_tcm_service_data()
    headers = ['年份', '门诊服务', '住院服务', '预防保健', 
               '康复服务', '养老服务', '家庭医生']
    file3 = save_csv('tcm_service_data_2011_2024.csv', headers, service_data, data_dir)
    print(f"✅ 已保存: {file3}")
    
    print("\n💰 生成中医药投入数据...")
    investment_data = generate_tcm_investment_data()
    headers = ['年份', '政府投入', '基础设施', '科研经费', 
               '人才培养', '医保支付', '总投入']
    file4 = save_csv('tcm_investment_data_2011_2024.csv', headers, investment_data, data_dir)
    print(f"✅ 已保存: {file4}")
    
    print("\n" + "=" * 70)
    print("📊 数据生成完成!")
    print("=" * 70)
    print(f"📁 数据保存位置: {data_dir}")
    print("\n💡 说明:")
    print("1. 这些数据基于公开信息估算，仅供参考")
    print("2. 实际研究请使用官方统计数据")
    print("3. 数据时间范围: 2011-2024年")
    print("4. 包含4个数据集:")
    print("   - 中医医院基础数据")
    print("   - 各省中医药数据")
    print("   - 中医药服务数据")
    print("   - 中医药投入数据")

if __name__ == '__main__':
    main()