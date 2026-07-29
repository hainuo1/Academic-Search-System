#!/usr/bin/env python3
"""生成3000篇文献SQL + 自动从keywords_text重建关键词关联（修复补丁）"""
import random, os
random.seed(42)
CATS = ['大气科学','大气物理学','大气化学','大气动力学','天气学','气候学','气候变化','气候系统','地球系统科学','季风研究','边界层气象','中尺度气象','高空气象','城市气象','天气预报','数值天气预报','灾害天气','极端天气事件','台风','热带气旋','龙卷风','强对流天气','暴雨洪涝','干旱','寒潮','高温事件','沙尘暴','冰雹','雷暴','雷电灾害','雾霾污染','气象观测','地面观测','高空气象观测','气象雷达','天气雷达','多普勒雷达','卫星遥感','气象卫星','遥感技术','微波遥感','激光雷达','无人机气象观测','气象数据分析','气象大数据','数据同化','模式模拟','数值模拟','高性能计算','科学计算','机器学习气象应用','深度学习气象应用','人工智能气象预测','神经网络模型','时间序列分析','统计气象学','海洋气象','海气相互作用','海洋科学','环境科学','环境污染','空气质量','大气污染控制','生态气象','农业气象','水文气象','冰冻圈科学','极地气象','地球物理学','地震学','地质学','地理信息系统','GIS技术','空间信息科学','自然灾害','灾害风险评估','遥感监测','人工智能','机器学习','深度学习','自然语言处理','计算机视觉','数据挖掘','数据库技术','信息检索','软件工程','云计算','大数据技术','数学','应用数学','统计学','概率论','随机过程','偏微分方程','数值分析','物理学','流体力学','热力学','动力系统']
SUR=['张','王','李','赵','陈','刘','杨','黄','周','吴','徐','孙','马','朱','胡','郭','何','高','林','郑','罗','梁','谢','宋','唐','韩','曹','许','邓','冯','曾','程','彭','潘','袁']
GV=['明','伟','强','敏','芳','涛','静','军','勇','洋','鹏','华','斌','杰','健','磊','娟','宁','平','婷','博','文','刚','辉','浩','凯','旭','琳','峰','阳','海','波','超','艳','玲','云','国','亮','帅','建','鑫','志','雪','飞','丽','锐','宇']
Y=[2016,2017,2018,2019,2020,2021,2022,2023,2024,2025]
R=['中国东部','华北','华东','华南','西北太平洋','青藏高原','长江流域','西北地区','西南地区','东北地区','东南沿海','黄河流域','内蒙古']
AL=['随机森林','XGBoost','LSTM','CNN','Transformer','GAN','图神经网络','注意力机制','迁移学习','集成学习']

def a():return random.choice(SUR)+random.choice(GV)
def au():n=random.randint(1,3);return ','.join(a()for _ in range(n))
def ca():n=random.randint(2,4);return ','.join(random.sample(CATS,min(n,len(CATS))))
def ti(cl):c1=cl[0];c2=cl[1]if len(cl)>1 else random.choice(CATS);y=random.choice(Y);r=random.choice(R);a2=random.choice(AL);n=random.randint(10,60);return random.choice([f'基于{c1}的{c2}研究',f'{y}年{r}{c1}特征分析',f'{c1}的时空演变规律及机理探讨',f'基于卫星遥感的{c1}监测方法研究',f'{c2}对{c1}的影响机制研究',f'{r}{c1}的多尺度特征分析',f'利用机器学习改进{c1}预报精度',f'全球变暖背景下{c1}的变化趋势',f'基于再分析资料的{c1}气候态研究',f'{c1}与{c2}的耦合关系分析',f'高分辨率模式中{c1}的参数化方案改进',f'深度学习在{c1}中的应用研究',f'基于{c1}的{c2}风险评估模型',f'{c1}极端事件的统计特征及归因分析',f'近{n}年{r}{c1}的年代际变化',f'多源数据融合在{c1}中的应用',f'基于{a2}的{c1}趋势预测研究',f'{c1}对农业生产的影响评估',f'{c1}成因的诊断分析与数值模拟',f'{c2}在{c1}研究中的应用进展',f'{r}近{n}年{c1}特征及变化趋势',f'{c1}观测技术与方法研究进展',f'基于AI的{c1}智能识别方法',f'气候模式对{c1}的模拟能力评估',f'{c1}的物理机制与预报预警技术'])
def ab(cl):c1=cl[0];c2=cl[1]if len(cl)>1 else random.choice(CATS);y=random.choice(Y);r=random.choice(R);n=random.randint(10,60);return random.choice([f'随着{c1}研究的不断深入，{c2}的应用为其提供了新的技术手段和研究视角。本文利用{y}年至{y+3}年的观测数据和数值模式结果，系统分析了{c1}的时空变化特征及其与{c2}的内在联系。结果表明：{c1}的变化呈现显著的时空差异性，{c2}对其产生了重要影响。研究结论为{c1}的机理认识和预测预警提供了科学依据。',f'{c1}是当前科学研究的前沿热点问题。本文基于多源观测数据和数值模拟方法，深入探讨了{c2}背景下{c1}的演变规律和驱动机制。研究运用统计分析方法和高分辨率数值模式，揭示了{c1}与{c2}之间的复杂耦合关系，发现两者间存在显著的非线性相互作用。本文的研究成果对深入理解{c1}的物理机制具有重要的理论意义。',f'本文针对{c1}领域的核心科学问题，提出了一种融合{c2}的创新研究框架。通过引入人工智能技术和大数据分析方法，建立了{c1}的高精度预测模型。实验验证表明，所提出的方法相比传统方案在准确率和泛化能力方面均有显著提升。该研究为{c1}的智能化分析和实时监测开辟了新途径。',f'{y}年{r}发生了一起典型的{c1}事件。本文综合利用多平台观测资料和数值模拟技术，对该事件的成因、演变过程和影响进行了全面的诊断分析。研究发现，{c2}的异常配置为该事件的发生提供了有利条件。本文还评估了当前业务模式对该类事件的预报能力，并提出了改进建议。',f'本文基于{n}年长时间序列数据，运用{c2}分析方法，系统研究了{r}{c1}的年代际变化特征和长期趋势。通过集合经验模态分解和小波分析等方法，揭示了{c1}的多时间尺度振荡特征及其与全球气候变暖的关联。研究结果为应对气候变化背景下的{c1}变化提供了科学参考。'])
def kw(cs):ws=cs.split(',');random.shuffle(ws);return ';'.join(ws[:random.randint(3,len(ws))])
def es(s):return s.replace("'","''")
def rd():return f'{random.choice(Y)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}'

total=3000
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'3000篇文献模拟数据.sql')
with open(out,'w',encoding='utf-8')as f:
    f.write("-- 3000篇气象科学文献 + 自动关键词关联\n")
    f.write("TRUNCATE TABLE documents RESTART IDENTITY CASCADE;\n")
    f.write("TRUNCATE TABLE keywords RESTART IDENTITY CASCADE;\n")
    f.write("TRUNCATE TABLE document_keyword RESTART IDENTITY;\n\n")
    for s in range(1,total+1,500):
        e=min(s+499,total)
        f.write(f"-- {s}-{e}\nINSERT INTO documents(title,author,abstract,publish_date,category,file_path,upload_user_id,keywords_text,view_count,download_count) VALUES\n")
        for i in range(s,e+1):
            cs=ca();cl=cs.split(',');vc=random.randint(5,500);dc=random.randint(1,max(1,vc//2))
            f.write(f"('{es(ti(cl))}','{es(au())}','{es(ab(cl))}','{rd()}','{es(cs)}','',2,'{es(kw(cs))}',{vc},{dc}){';'if i==e else','}\n")
        f.write('\n')
    # 自动从documents.keywords_text重建关键词及关联
    f.write("""
-- 从 keywords_text 自动重建关键词字典和关联
DO $$
DECLARE r RECORD; arr TEXT[]; w TEXT; kid INT;
BEGIN
  FOR r IN SELECT document_id, keywords_text FROM documents WHERE keywords_text!='' LOOP
    arr:=string_to_array(r.keywords_text,';');
    FOREACH w IN ARRAY arr LOOP w:=trim(w); IF w='' THEN CONTINUE; END IF;
      INSERT INTO keywords(keyword_name) VALUES(w) ON CONFLICT DO NOTHING;
      SELECT keyword_id INTO kid FROM keywords WHERE keyword_name=w;
      INSERT INTO document_keyword(document_id,keyword_id,tf_idf) VALUES(r.document_id,kid,1.0) ON CONFLICT DO NOTHING;
    END LOOP;
  END LOOP;
END $$;
UPDATE documents SET full_text_tsv=setweight(to_tsvector('simple',COALESCE(title,'')),'A')||setweight(to_tsvector('simple',COALESCE(abstract,'')),'B');
SELECT 'docs' AS item, COUNT(*) FROM documents
UNION ALL SELECT 'keywords', COUNT(*) FROM keywords
UNION ALL SELECT 'links', COUNT(*) FROM document_keyword;
""")
print('OK:',out)
