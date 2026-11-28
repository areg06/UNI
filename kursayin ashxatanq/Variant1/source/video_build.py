"""Build the narrated Armenian construction video from the canonical model.

Optional dependencies: Pillow, PyMuPDF, piper-tts, FFmpeg with libass/libx264.
The native Armenian Piper model is supplied with --voice-model; do not commit it.
All transient WAVs, frames and encoded scene clips stay in --cache (outside git).
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import wave

from video_draw import frame, font, wrap, W, H, CHAPTERS
from video_kinematic_lesson import SCENES as KINEMATIC
from video_dynamic_lesson import SCENES as DYNAMIC

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
FPS=12

INTRO={
    'id':'intro','chapter':1,'view':'overview','stage':0,
    'title':'Չորս թերթ․ գծում ենք՝ հասկանալով',
    'speech':'Այս տեսանյութում միասին կկառուցենք քո տարբերակի բոլոր չորս գծագրական թերթերը։ Յուրաքանչյուր նոր գծի համար կգտնենք երեք պատասխան՝ ինչն արդեն գիտենք, ինչ սահմանափակումից է այն ստացվում, և ինչով ենք ստուգում արդյունքը։ Երբ պատրաստ լինես նույն քայլը թղթի վրա անել, դադարեցրու տեսանյութը, հետո շարունակենք հաջորդ կետից։',
    'note':'Գծի աղբյուրը → կառուցումը → ստուգումը։',
    'formula':'3 × A3 + 1 × A4 · Տարբերակ 1',
    'tip':'Մասշտաբները կարդում ենք նշումներից։ Էկրանին երևացող նկարը քանոնով չենք չափում։',
}
FINISH={
    'id':'finish','chapter':5,'view':'overview','stage':0,
    'title':'Վերջնական ստուգում՝ մինչև մաքուր գծագիրը',
    'speech':'Հիմա բոլոր չորս թերթերը մի ամբողջություն են։ Ստուգիր, որ ամեն տեղ դիրքերի համարները նույնն են, արագությունների պլաններում հայտնի սլաքը հիսուն միլիմետր է, իսկ արագացումների պլանում՝ յոթանասուն։ Էներգիայի առաջին ու վերջին արժեքները զրո են, և գրաֆիկների մասշտաբները նշված են իրենց միավորներով։ Ճշգրիտ չափերով տպելու համար բացիր առանձին թերթերի ֆայլերը և ընտրիր իրական չափը։',
    'note':'Նույն դիրքը կապում է մեխանիզմը, պլաններն ու բոլոր գրաֆիկները։',
    'formula':'pb = 50 մմ · πb = 70 մմ · ΔE₀ = ΔE₈ = 0',
    'tip':'Մնացած ազատ հատվածը նախատեսված է հաջորդ՝ էներգիա–զանգված դիագրամի փուլի համար։',
}

def scenes():
    velocity_sheet={
        'id':'velocity-sheet','chapter':2,'view':'sheet','stage':0,'sheet':2,
        'title':'Թերթ 2․ պլանները տեղադրում ենք չորսը երկու շարքով',
        'speech':'Ութ կառուցված պլանները տեղավորում ենք երկրորդ մեծ թերթի վրա՝ չորս սյունակով և երկու շարքով։ Վերևի շարքը զրոյից երրորդ դիրքերն են, ներքևինը՝ չորրորդից յոթերորդը։ Բևեռները կարելի է տեղափոխել, բայց յուրաքանչյուր պլանի ներսում բոլոր կետերը տեղափոխվում են միասին։ Մասշտաբը նույնն ենք թողնում, որպեսզի պլանների չափերն անմիջապես համեմատելի լինեն։',
        'note':'Տարբեր դիրքերի համար փոխվում են ուղղությունները, մասշտաբը մնում է նույնը։',
        'formula':'Վերև՝ 0,1,2,3 · ներքև՝ 4,5,6,7 · pb = 50 մմ',
    }
    first_sheet={
        'id':'mechanism-sheet','chapter':3,'view':'sheet','stage':0,'sheet':1,
        'title':'Թերթ 1․ դիրքերն ու արագացումները հավաքում ենք միասին',
        'speech':'Հիմա առաջին թերթն էլ ամբողջական է։ Ձախ կողմում դիրքերի պլանն ու օգտակար դիմադրության գրաֆիկն են, աջ կողմի ազատ տեղում՝ երկրորդ դիրքի արագացումների պլանը։ Հոդերի համարները նույնն են, բայց այս երկու պատկերներում հատվածները տարբեր բաներ են նշանակում։ Դրա համար առանձին նշում ենք երկարությունների, ուժի և արագացումների մասշտաբները։',
        'note':'Մեկ թերթի վրա տարբեր մասշտաբներ կան, և ամեն մեկը պետք է ստորագրված լինի։',
        'formula':'μₗ = 0,00175 մ/մմ · μF = 200 Ն/մմ · μₐ = 0,2909',
    }
    data=[INTRO]
    for scene in KINEMATIC:
        if data[-1]['chapter']==2 and scene['chapter']==3:data.append(velocity_sheet)
        data.append(scene)
    data.extend([first_sheet]+DYNAMIC+[FINISH])
    assert len({x['id'] for x in data})==len(data)
    assert all(x['speech'] and x['note'] and 1<=x['chapter']<=5 for x in data)
    return data

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))

def duration(path):return float(probe(path)['format']['duration'])

def timestamp(t,ass=False):
    if ass:
        n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
    n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02}.{n%1000:03}'

def caption_chunks(text,seconds,offset):
    words=text.split();groups=[];current=''
    for word in words:
        if current and len(current+' '+word)>82:groups.append(current);current=word
        else:current=(current+' '+word).strip()
    if current:groups.append(current)
    weight=sum(len(s) for s in groups) or 1;cursor=offset;output=[]
    # Keep short final words with a neighbour instead of flashing a 0.1 s cue.
    while len(groups)>1:
        weight=sum(len(s) for s in groups)
        tiny=next((i for i,g in enumerate(groups) if seconds*len(g)/weight<1.3),None)
        if tiny is None:break
        if tiny==0:groups[:2]=[groups[0]+' '+groups[1]]
        else:groups[tiny-1:tiny+1]=[groups[tiny-1]+' '+groups[tiny]]
    weight=sum(len(s) for s in groups) or 1
    for g in groups:
        end=cursor+seconds*len(g)/weight
        lines=wrap(g,36,1620)
        if len(lines)==2:
            words=g.split()
            options=[(' '.join(words[:k]),' '.join(words[k:])) for k in range(1,len(words))]
            options=[pair for pair in options if all(font(36).getlength(x)<=1620 for x in pair)]
            if options:lines=list(min(options,key=lambda pair:abs(font(36).getlength(pair[0])-font(36).getlength(pair[1]))))
        output.append({'start':cursor,'end':end,'text':'\n'.join(lines)})
        cursor=end
    return output

def synthesize(data,model,cache,length_scale):
    from piper import PiperVoice
    from piper.config import SynthesisConfig
    voice=PiperVoice.load(str(model))
    config=SynthesisConfig(length_scale=length_scale,noise_scale=.55,noise_w_scale=.7,normalize_audio=True)
    out=[];audio_dir=cache/'audio';audio_dir.mkdir(parents=True,exist_ok=True)
    model_hash=hashlib.sha256(model.read_bytes()).hexdigest()[:16]
    for index,s in enumerate(data):
        digest=hashlib.sha256((model_hash+str(length_scale)+s['speech']).encode()).hexdigest()[:20]
        target=audio_dir/(digest+'.wav');metadata=target.with_suffix('.json')
        if target.exists() and metadata.exists():
            entry=json.loads(metadata.read_text())
            if entry.get('caption_version')!=3:
                batches=[]
                for c in entry['captions']:
                    if batches and abs(c['start']-batches[-1][-1]['end'])<.04:batches[-1].append(c)
                    else:batches.append([c])
                entry['captions']=[]
                for batch in batches:
                    text=' '.join(c['text'].replace('\n',' ') for c in batch)
                    entry['captions'].extend(caption_chunks(text,batch[-1]['end']-batch[0]['start'],batch[0]['start']))
                entry['caption_version']=3
                metadata.write_text(json.dumps(entry,ensure_ascii=False,indent=2))
        else:
            sentences=re.split(r'(?<=[։.!])\s+',s['speech'].strip())
            buffers=[];captions=[];cursor=.28;rate=None
            for k,text in enumerate(sentences):
                sentence=audio_dir/f'{digest}-{k}.wav'
                with wave.open(str(sentence),'wb') as wav:voice.synthesize_wav(text,wav,syn_config=config)
                with wave.open(str(sentence),'rb') as wav:
                    assert wav.getnchannels()==1 and wav.getsampwidth()==2
                    sr=wav.getframerate();raw=wav.readframes(wav.getnframes())
                if rate is None:rate=sr
                assert sr==rate
                seconds=len(raw)/(sr*2)
                captions.extend(caption_chunks(text,seconds,cursor))
                buffers.append(raw);buffers.append(bytes(round(sr*.17)*2));cursor+=seconds+.17
                sentence.unlink()
            with wave.open(str(target),'wb') as wav:
                wav.setparams((1,2,rate,0,'NONE','not compressed'));wav.writeframes(b''.join(buffers))
            entry={'audio':str(target),'captions':captions,'caption_version':3,'duration':math.ceil((cursor+.65)*FPS)/FPS}
            metadata.write_text(json.dumps(entry,ensure_ascii=False,indent=2))
        out.append({**s,**entry})
        if index%5==0 or index+1==len(data):print(f'Հայերեն ձայն՝ {index+1}/{len(data)}',flush=True)
    return out

def write_ass(captions,path):
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans Armenian,36,&H00FFFFFF,&H00FFFFFF,&H003C2316,&H003C2316,0,0,0,0,100,100,0,0,1,1.1,0,2,155,155,80,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for item in captions:
        text=item['text'].replace('{','(').replace('}',')').replace('\n',r'\N')
        header+=f'Dialogue: 0,{timestamp(item["start"],True)},{timestamp(item["end"],True)},Main,,0,0,0,,{text}\n'
    path.write_text(header)

def encode_scene(task):
    index,total,s,cache,crf,renderer_hash=task;cache=Path(cache)
    digest=hashlib.sha256((json.dumps(s,sort_keys=True,ensure_ascii=False)+str(crf)+renderer_hash).encode()).hexdigest()[:18]
    target=cache/'clips'/f'{index:03}-{digest}.mp4';target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():return index,str(target),duration(target)
    ass=target.with_suffix('.ass');write_ass(s['captions'],ass)
    temporary=target.with_suffix('.working.mp4')
    args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',s['audio'],
          '-vf',f"ass={ass}",'-af','adelay=280,apad','-t',str(s['duration']),'-c:v','libx264','-preset','veryfast','-crf',str(crf),'-g','72','-pix_fmt','yuv420p',
          '-c:a','aac','-b:a','56k','-ar','24000','-ac','1','-threads','2','-movflags','+faststart',str(temporary)]
    process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    nframes=round(s['duration']*FPS);frames={}
    try:
        for n in range(nframes):
            fraction=n/max(1,nframes-1)
            # Explain the premise first; draw while the reason is spoken; then allow inspection.
            key=round(max(0,min(1,(fraction-.08)/.48))*24)
            if key not in frames:frames[key]=frame(s,key/24,index/total).tobytes()
            process.stdin.write(frames[key])
        process.stdin.close();error=process.stderr.read().decode();code=process.wait()
        if code:raise RuntimeError(error)
    except BaseException:
        process.kill();temporary.unlink(missing_ok=True);raise
    temporary.replace(target)
    return index,str(target),duration(target)

def build(args):
    cache=args.cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    output=ROOT/'video';output.mkdir(exist_ok=True)
    data=scenes()
    if args.preview:
        args.preview.mkdir(parents=True,exist_ok=True)
        for index,s in enumerate(data):frame(s,1,index/len(data)).save(args.preview/f'{index:03}-{s["id"]}.jpg',quality=90)
        print(f'{len(data)} preview frames');return
    if not args.voice_model or not args.voice_model.exists():raise SystemExit('Supply --voice-model /path/to/hy_AM-gor-medium.onnx')
    data=synthesize(data,args.voice_model.resolve(),cache,args.length_scale)
    (cache/'narrated-scenes.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    if args.audio_only:
        print(f'Խոսքի տևողությունը՝ {sum(x["duration"] for x in data)/60:.1f} րոպե',flush=True)
        return
    renderer_hash=hashlib.sha256((HERE/'video_draw.py').read_bytes()).hexdigest()
    tasks=[(i,len(data),s,str(cache),args.crf,renderer_hash) for i,s in enumerate(data)]
    clips={}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(encode_scene,t) for t in tasks]
        for k,future in enumerate(as_completed(futures)):
            index,path,seconds=future.result();clips[index]=(path,seconds)
            print(f'Տեսարան՝ {k+1}/{len(data)} · {data[index]["id"]} · {seconds:.1f} վ',flush=True)
    cursor=0;chapters=[];captions=[];public=[]
    for index,s in enumerate(data):
        path,seconds=clips[index]
        if not chapters or chapters[-1]['id']!=s['chapter']:
            if chapters:chapters[-1]['end']=cursor
            chapters.append({'id':s['chapter'],'title':CHAPTERS[s['chapter']],'start':cursor})
        public.append({k:v for k,v in {**s,'start':cursor,'duration':seconds}.items() if k not in ['audio','captions']})
        captions.extend({**c,'start':c['start']+cursor,'end':c['end']+cursor} for c in s['captions'])
        cursor+=seconds
    chapters[-1]['end']=cursor
    concat=cache/'concat.txt';concat.write_text(''.join(f"file '{clips[i][0]}'\n" for i in range(len(data))))
    meta=cache/'chapters.ffmetadata';metadata=';FFMETADATA1\ntitle=ՄՄՏ․ գծագրերի քայլ առ քայլ կառուցում\nartist=Տարբերակ 1\n'
    for chapter in chapters:metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(chapter["start"]*1000)}\nEND={round(chapter["end"]*1000)}\ntitle={chapter["title"]}\n'
    meta.write_text(metadata)
    movie=output/'drawing-guide.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(meta),'-map','0','-map_metadata','1','-c','copy','-movflags','+faststart',str(movie)],check=True)
    if movie.stat().st_size>99_000_000:raise RuntimeError('Video exceeds repository file-size limit. Rebuild with higher --crf.')
    vtt='WEBVTT\n\n'
    for c in captions:vtt+=f'{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}\n\n'
    (output/'drawing-guide.hy.vtt').write_text(vtt)
    manifest={'title':'Գծագրերի կառուցումը՝ քայլ առ քայլ','duration':cursor,'width':W,'height':H,'chapters':chapters,'scenes':public,
              'voice':{'type':'Հայերեն սինթեզված ձայն','model':'hy_AM-gor-medium','source':'https://huggingface.co/davit312/piper-TTS-Armenian'}}
    (output/'lesson.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    poster=frame(INTRO,1,0);poster.save(output/'poster.jpg',quality=92)
    subprocess.run([os.sys.executable,str(HERE/'video_page.py')],check=True)
    print(f'Պատրաստ է՝ {cursor/60:.1f} րոպե, {movie.stat().st_size/1e6:.1f} ՄԲ',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice-model',type=Path,default=Path(os.environ['UNI_PIPER_MODEL']) if 'UNI_PIPER_MODEL' in os.environ else None)
    parser.add_argument('--cache',type=Path,default=Path('/tmp/uni-video-cache'))
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--crf',type=int,default=28)
    parser.add_argument('--length-scale',type=float,default=1.02)
    parser.add_argument('--preview',type=Path)
    parser.add_argument('--audio-only',action='store_true')
    build(parser.parse_args())
