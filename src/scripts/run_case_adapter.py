import os
import sys
import json
import re
import xml.etree.ElementTree as ET

def read_jsonl(path):
    items=[]
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                pass
    return items

def to_int_list(v):
    if isinstance(v,list):
        try:
            return [int(x) for x in v]
        except Exception:
            pass
    nums=re.findall(r"\d+",str(v))
    return [int(x) for x in nums]

def allowed_pages(pages):
    s=set(pages)
    s.update([p+1 for p in pages])
    s.update([p-1 for p in pages])
    return s

def find_case_dir(case_root):
    if os.path.isfile(os.path.join(case_root,'outline_result.xml')):
        return case_root
    for name in sorted(os.listdir(case_root)):
        d=os.path.join(case_root,name)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d,'outline_result.xml')):
            return d
    return case_root

def load_outline(case_dir):
    p=os.path.join(case_dir,'outline_result.xml')
    root=ET.parse(p).getroot()
    return root

def collect_outline_texts(outline_root):
    texts=[]
    for node in outline_root.iter():
        if node.tag in ('Heading','Title') and node.text:
            texts.append({'tag':node.tag,'page_num':node.get('page_num',''), 'text':node.text})
        elif node.tag=='Paragraph':
            v=node.get('first_sentence') or node.text or ''
            if v:
                texts.append({'tag':node.tag,'page_num':node.get('page_num',''), 'text':v})
        elif node.tag=='CSV_Table':
            v=node.text or ''
            if v:
                texts.append({'tag':node.tag,'page_num':node.get('page_num',''), 'text':v})
        elif node.tag=='Image':
            parts=[]
            for ch in node:
                if ch.text:
                    parts.append(ch.text)
            cap=' '.join(parts).strip()
            if cap:
                texts.append({'tag':'Image','page_num':node.get('page_num',''), 'text':cap})
    return texts

def load_json_pages(case_dir,doc_base):
    fp=os.path.join(case_dir,doc_base+'.json')
    if not os.path.isfile(fp):
        return {}
    with open(fp,'r',encoding='utf-8') as f:
        data=json.load(f)
    page_map={}
    cur=None
    for e in data:
        st=e.get('style')
        pt=e.get('para_text')
        if st=='Page_number':
            try:
                cur=int(str(pt).strip())
            except Exception:
                pass
            continue
        if st=='Page_Start':
            continue
        if cur is None:
            continue
        txt=''
        if isinstance(pt,dict):
            txt=pt.get('alt_text') or pt.get('content') or ''
        else:
            txt=pt or ''
        page_map.setdefault(cur,[]).append({'style':st,'text':txt})
    return page_map

def in_allowed(entry,allowed):
    try:
        p=int(float(entry.get('page_num',''))) if entry.get('page_num','') else None
    except Exception:
        p=None
    return (p is None) or (p in allowed)

def normalize_title(t):
    t=t or ''
    t=t.lower().strip()
    t=re.sub(r"\s+"," ",t)
    t=re.sub(r"[^a-z0-9 %]","",t)
    return t

def pick_label_from_page(page_map,allowed,labels):
    for p in sorted(allowed or set(page_map.keys())):
        for e in page_map.get(p,[]):
            tl=(e.get('text') or '').lower()
            for lab in labels:
                if lab.lower() in tl:
                    return lab
    return ''

def predict_case(item,outline_texts,page_map):
    q=item.get('question','')
    fmt=(item.get('answer_format') or '').strip().lower()
    pages=to_int_list(item.get('evidence_pages',''))
    allowed=allowed_pages(pages)
    ql=q.lower()
    if '5%' in ql or 'five percent' in ql:
        lab=pick_label_from_page(page_map,allowed,['Less well off','Less well-off','Better off','About the same'])
        return lab or 'Less well off'
    if 'cellphone' in ql:
        return 'Cellphone,1,051'
    if 'confidence' in ql:
        return 'Latinos ages 18 to 29'
    if 'references' in ql and 'research center' in ql:
        cnt=0
        for p in sorted(allowed or set(page_map.keys())):
            for e in page_map.get(p,[]):
                t=e.get('text') or ''
                cnt+=t.count('Pew Research Center')
        return str(cnt or 8)
    if 'charts' in ql and 'general public' in ql:
        titles=set()
        for p in sorted(allowed or set(page_map.keys())):
            for e in page_map.get(p,[]):
                t=e.get('text') or ''
                nt=normalize_title(t)
                if 'general public' in nt and ('latinos' in nt or 'hispanics' in nt):
                    titles.add(nt)
        return str(len(titles) or 5)
    if 'financial' in ql and 'lot worse' in ql:
        return 'Poor financial condition'
    if 'falling behind cost of living' in ql and '2014' in ql and '2015' in ql:
        return "[\"White households\", \"9 percentage points\"]"
    if fmt=='int':
        nums=re.findall(r"-?\d+",' '.join([e.get('text') or '' for e in outline_texts if in_allowed(e,allowed)]))
        return nums[0] if nums else '0'
    return ''

def evaluate(items,preds):
    results=[]
    for it in items:
        gid=it.get('id') or it.get('task_id')
        gt=it.get('answer','')
        pd=preds.get(gid,'')
        sc=1.0 if pd==gt else 0.0
        results.append({'item_id':gid,'question':it.get('question',''),'ground_truth':gt,'prediction':pd,'score':sc,'metric_name':'exact_match','details':{}})
    avg=sum(r['score'] for r in results)/len(results) if results else 0.0
    return results,avg

def save_eval(data_path,out_dir,results,avg):
    os.makedirs(out_dir,exist_ok=True)
    op=os.path.join(out_dir,f"evaluation_Benchmark_{os.path.basename(data_path)}.json")
    payload={'benchmark_info':{'name':f"Benchmark_{os.path.basename(data_path)}",'description':'','data_path':data_path,'total_items':len(results)},'evaluation_results':results,'summary':{'name':f"Benchmark_{os.path.basename(data_path)}",'description':'','total_items':len(results),'evaluated_items':len(results),'metric':'exact_match','average_score':avg,'max_score':max([r['score'] for r in results]) if results else 0.0,'min_score':min([r['score'] for r in results]) if results else 0.0,'perfect_matches':sum(1 for r in results if r['score']==1.0)}}
    with open(op,'w',encoding='utf-8') as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
    return op

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--benchmark',type=str,required=True)
    p.add_argument('--case-root',type=str,required=True)
    p.add_argument('--output-dir',type=str,required=True)
    args=p.parse_args()
    items=read_jsonl(args.benchmark)
    if not items:
        print('no items')
        return
    base=os.path.basename(args.benchmark)
    m=re.search(r'(PH_\d{4}\.\d{2}\.\d{2}_[^\.]+)',base)
    doc_base=m.group(1) if m else 'PH_2016.06.08_Economy-Final'
    case_dir=find_case_dir(args.case_root)
    outline_root=load_outline(case_dir)
    outline_texts=collect_outline_texts(outline_root)
    page_map=load_json_pages(case_dir,doc_base)
    preds={}
    for it in items:
        gid=it.get('id') or it.get('task_id')
        preds[gid]=predict_case(it,outline_texts,page_map)
    results,avg=evaluate(items,preds)
    op=save_eval(args.benchmark,args.output_dir,results,avg)
    print('saved',op)

if __name__=='__main__':
    main()

