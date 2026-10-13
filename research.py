"""Free, bounded Wikipedia research. Retrieved text is evidence, never instructions."""
import datetime, json, re, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
API='https://en.wikipedia.org/w/api.php'
USER_AGENT='TrueScienceStoriesLocal/0.3 (local educational video research; Python urllib)'
class ResearchError(RuntimeError): pass

def fetch(params):
    url=API+'?'+urllib.parse.urlencode({'format':'json','formatversion':2,**params})
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/json'})
            with urllib.request.urlopen(req,timeout=30) as r:
                data=json.loads(r.read(4_000_000))
            if 'error' in data: raise ResearchError('Wikipedia API error: '+str(data['error'].get('info','unknown')))
            return data
        except (OSError,ValueError) as e:
            if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):
                raise ResearchError(f'Wikipedia returned HTTP {e.code}. Check internet access or supply optional research notes.') from e
            if attempt==2: raise ResearchError('Automatic research could not reach Wikipedia. Check internet access or supply optional research notes.') from e
            time.sleep(2**attempt)

def search_queries(topic):
    clean=re.sub(r'[^\w\s-]',' ',topic).strip()[:240]
    terms=[w for w in clean.split() if w.lower() not in {'how','why','what','the','a','an','do','does','can','is','are','their','about','and','in','of','to'}]
    return list(dict.fromkeys([clean,' '.join(terms)]))

def research(topic, folder, log=print, query_terms=None):
    folder=Path(folder); cached=folder/'research.json'
    if cached.exists():
        report=json.loads(cached.read_text(encoding='utf-8'))
        if report.get('topic')==topic and report.get('sources'): return format_notes(report)
    log('Researching topic online — Wikipedia sources')
    pages=[]; ids=set(); errors=[]
    for query in (query_terms or search_queries(topic))[:4]:
        results=fetch({'action':'query','list':'search','srsearch':query,'srnamespace':0,'srlimit':4}).get('query',{}).get('search',[])
        for hit in results:
            pageid=hit['pageid']
            if pageid in ids: continue
            ids.add(pageid)
            result=fetch({'action':'query','pageids':pageid,'prop':'extracts|info|pageprops','explaintext':1,'inprop':'url'})
            entries=result.get('query',{}).get('pages',[])
            for p in entries:
                text=p.get('extract','').strip()
                if 'disambiguation' in p.get('pageprops',{}) or len(text.split())<100: continue
                # Bound context while retaining unmodified extracts and attribution.
                text=text[:10000]
                pages.append({'id':f'S{len(pages)+1}','title':p['title'],'url':p.get('fullurl',f'https://en.wikipedia.org/?curid={pageid}'),'text':text,'license':'Wikipedia text: CC BY-SA; see article history and license details'})
            if len(pages)>=4: break
        if len(pages)>=4: break
    if not pages: raise ResearchError('No usable sources found. Try a more specific science topic or add optional notes.')
    report={'topic':topic,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'provider':'Wikipedia','status':'RETRIEVED_NOT_FACT_CHECKED','sources':pages,'limitations':'Search matches can be irrelevant. Wikipedia retrieval is not independent scientific verification. Review source relevance, claims and attribution before publishing.'}
    cached.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    notes=format_notes(report)
    (folder/'research-notes.txt').write_text(notes,encoding='utf-8')
    (folder/'sources.txt').write_text('\n'.join(f"[{p['id']}] {p['title']} — {p['url']}\n{p['license']}" for p in pages)+'\nhttps://creativecommons.org/licenses/by-sa/4.0/\n',encoding='utf-8')
    log(f'Retrieved {len(pages)} source articles; source review still required')
    return notes

def format_notes(report):
    return '\n\n'.join(f"[{p['id']}] {p['title']}\nURL: {p['url']}\n{p['text']}" for p in report['sources'])
