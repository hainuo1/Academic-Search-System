"""龙卷风分析模块 Blueprint —— 气象科学研究数据平台"""
import re
from flask import Blueprint, request, jsonify
from db import get_connection
from utils import get_pagination, login_required
from config import Config
tornado_bp = Blueprint('tornado', __name__)


def _parse_damage(raw):
    """将NOAA SPC机器格式的Damage字段解析为中文可读文本。
    例如: 'length:168.5300mi width:2600yd loss:25000'
    返回: '路径长度 168.5 mi（约271.2 km）· 宽度 2600 yd（约2.38 km）· 经济损失 $25,000'"""
    if not raw:
        return raw
    # 只处理 machine format 的情况；human-written text 直接返回
    if not re.search(r'\b(length|width|loss):', raw, re.IGNORECASE):
        return raw
    parts = []
    m_len = re.search(r'length:\s*([\d.]+)\s*mi', raw, re.IGNORECASE)
    if m_len:
        mi = float(m_len.group(1))
        km = mi * 1.60934
        parts.append(f'路径长度 {mi:.1f} mi（约{km:.1f} km）')
    m_wid = re.search(r'width:\s*([\d.]+)\s*yd', raw, re.IGNORECASE)
    if m_wid:
        yd = float(m_wid.group(1))
        km_w = yd * 0.0009144
        parts.append(f'宽度 {yd:.0f} yd（约{km_w:.2f} km）')
    m_loss = re.search(r'loss:\s*([\d.]+)', raw, re.IGNORECASE)
    if m_loss:
        loss_val = float(m_loss.group(1))
        if loss_val >= 1_000_000:
            parts.append(f'经济损失 ${loss_val/1_000_000:.1f}M')
        elif loss_val >= 1_000:
            parts.append(f'经济损失 ${loss_val:,.0f}')
        else:
            parts.append(f'经济损失 ${loss_val:.0f}')
    return ' · '.join(parts) if parts else raw


@tornado_bp.route('/api/tornado/list')
@login_required
def tornado_list():
    year=request.args.get('year','').strip();keyword=request.args.get('keyword','').strip()
    min_ef=request.args.get('min_ef','').strip();page_size=20
    conn=get_connection();cur=conn.cursor()
    cur.execute("SELECT DISTINCT YEAR(DateTime) AS y FROM TornadoInfo ORDER BY y DESC")
    ay=[r[0] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT Province FROM TornadoInfo WHERE Province!='' ORDER BY Province")
    ap=[r[0] for r in cur.fetchall()]
    conds,params=[],[]
    if year:conds.append("YEAR(DateTime)=%s");params.append(int(year))
    if keyword:conds.append("Place LIKE %s");params.append('%'+keyword+'%')
    if min_ef:
        try:conds.append("Magnitude>=%s");params.append(int(min_ef))
        except:pass
    wc=("WHERE "+" AND ".join(conds)) if conds else ""
    try:
        cnt_sql=f"SELECT COUNT(*) FROM TornadoInfo {wc}"
        cur.execute(cnt_sql,params);total=cur.fetchone()[0]
        page,offset,tp=get_pagination(request.args.get('page'),total,page_size)
        sel_sql=f"""SELECT EventID,DateTime,Place,Province,EFScale,Magnitude,Casualties,Deaths,Injuries,Damage FROM TornadoInfo {wc} ORDER BY DateTime DESC LIMIT %s OFFSET %s"""
        cur.execute(sel_sql,params+[page_size,offset]);rows=cur.fetchall()
    except Exception as e:return jsonify({'code':500,'message':f'查询失败：{str(e)}','data':None})
    tornadoes=[{'event_id':r.EventID,'datetime':r.DateTime.strftime('%Y-%m-%d %H:%M') if r.DateTime else '','place':r.Place,'province':r.Province,'ef_scale':r.EFScale,'magnitude':r.Magnitude,'casualties':r.Casualties or 0,'deaths':r.Deaths or 0,'injuries':r.Injuries or 0} for r in rows]
    return jsonify({'code':200,'message':'查询成功','data':{'tornadoes':tornadoes,'total_count':total,'page':page,'total_pages':tp,'available_years':ay,'available_provinces':ap}})

@tornado_bp.route('/api/tornado/<int:event_id>')
@login_required
def tornado_detail(event_id):
    conn=get_connection();cur=conn.cursor()
    cur.execute("""SELECT EventID,DateTime,Latitude,Longitude,Place,Province,EFScale,Magnitude,Casualties,Deaths,Injuries,Damage FROM TornadoInfo WHERE EventID=%s""",(event_id,))
    row=cur.fetchone()
    if not row:return jsonify({'code':404,'message':'龙卷风事件不存在','data':None})
    detail={'event_id':row.EventID,'datetime':row.DateTime.strftime('%Y-%m-%d %H:%M') if row.DateTime else '','latitude':row.Latitude,'longitude':row.Longitude,'place':row.Place,'province':row.Province,'ef_scale':row.EFScale,'magnitude':row.Magnitude,'casualties':row.Casualties or 0,'deaths':row.Deaths or 0,'injuries':row.Injuries or 0,'damage':_parse_damage(row.Damage)}
    cur.execute("""SELECT DateTime,EFScale,Magnitude,Place,Casualties,Deaths FROM TornadoInfo WHERE Province=%s AND EventID!=%s ORDER BY DateTime DESC LIMIT 20""",(row.Province,event_id))
    nearby=[{'datetime':r.DateTime.strftime('%Y-%m-%d %H:%M') if r.DateTime else '','ef_scale':r.EFScale,'magnitude':r.Magnitude,'place':r.Place,'casualties':r.Casualties,'deaths':r.Deaths} for r in cur.fetchall()]
    return jsonify({'code':200,'message':'查询成功','data':{'detail':detail,'nearby':nearby}})

@tornado_bp.route('/api/tornado/ai_analysis',methods=['POST'])
@login_required
def ai_analysis():
    data=request.get_json(silent=True) or {};event_id=data.get('event_id','');at=data.get('analysis_type','trend').strip()
    if not event_id:return jsonify({'code':400,'message':'缺少 event_id','data':None})
    conn=get_connection();cur=conn.cursor()
    cur.execute("SELECT Content FROM TornadoAIAnalysis WHERE EventID=%s AND AnalysisType=%s",(event_id,at))
    cached=cur.fetchone()
    if cached:return jsonify({'code':200,'message':'AI 分析完成（缓存）','data':{'analysis_type':at,'content':cached.Content,'cached':True}})
    cur.execute("""SELECT EventID,DateTime,Place,Province,EFScale,Magnitude,Casualties,Deaths,Injuries,Damage FROM TornadoInfo WHERE EventID=%s""",(event_id,))
    tr=cur.fetchone()
    if not tr:return jsonify({'code':404,'message':'龙卷风事件不存在','data':None})
    summary=f"龙卷风：{tr.DateTime} {tr.EFScale}，发生于{tr.Province}。死亡{tr.Deaths or 0}人，受伤{tr.Injuries or 0}人。{_parse_damage(tr.Damage) or ''}"
    sps={'trend':'你是气象学家。请用100-150字中文回复。','risk':'你是灾害评估专家。请用100-150字中文回复。','climate':'你是气候学家。请用100-150字中文回复。'}
    aps={'trend':f"""{summary}。请用100-150字中文分析该龙卷风的活动趋势与破坏力。""",'risk':f"""{summary}。请用100-150字中文评估该龙卷风的风险等级与防范建议。""",'climate':f"""{summary}。请用100-150字中文分析该区域龙卷风的气候特征与成因。"""}
    sp=sps.get(at,sps['trend']);up=aps.get(at,aps['trend'])
    ak=Config.DEEPSEEK_API_KEY
    if not ak:return jsonify({'code':500,'message':'DeepSeek API Key 未配置','data':None})
    try:
        import requests
        resp=requests.post(f"{Config.DEEPSEEK_API_BASE}/chat/completions",headers={'Authorization':f'Bearer {ak}','Content-Type':'application/json'},json={'model':Config.DEEPSEEK_MODEL,'messages':[{'role':'system','content':sp},{'role':'user','content':up}],'temperature':0.3,'max_tokens':350},timeout=60)
        resp.raise_for_status();result=resp.json();ai_text=result['choices'][0]['message']['content']
        cur.execute("INSERT INTO TornadoAIAnalysis (EventID,AnalysisType,Content) VALUES (%s,%s,%s)",(event_id,at,ai_text));conn.commit()
        return jsonify({'code':200,'message':'AI 分析完成','data':{'analysis_type':at,'content':ai_text,'cached':False}})
    except requests.exceptions.Timeout:return jsonify({'code':500,'message':'AI 服务请求超时','data':None})
    except requests.exceptions.RequestException as e:return jsonify({'code':500,'message':f'AI 服务请求失败：{str(e)}','data':None})
    except Exception as e:return jsonify({'code':500,'message':f'AI 分析异常：{str(e)}','data':None})
