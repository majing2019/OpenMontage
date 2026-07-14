#!/usr/bin/env python3
"""TTS Voice Preview — 99-voice catalog for Healing Text Pipeline."""

from __future__ import annotations
import base64, json, os, subprocess, sys, time, uuid
from pathlib import Path
import requests

PROJECT_ROOT = Path("/Users/majing/projects/OpenMontage")
OUTPUT_DIR = PROJECT_ROOT / "skills" / "pipelines" / "healing-text"
SAMPLES_DIR = OUTPUT_DIR / "voice-samples"
SAMPLE_TEXT = "生活不是等待暴风雨过去，而是学会在雨中起舞。"
SPEECH_RATE = -20
RESOURCE_ID = "seed-tts-2.0"

DOTENV_PATH = PROJECT_ROOT / ".env"
if DOTENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(DOTENV_PATH)
API_KEY = os.environ.get("DOUBAO_SPEECH_API_KEY", "")

# Bypass macOS system proxy for Volcengine API hosts
_NO_PROXY = {"http": None, "https": None}

VOICES = [
    {"id": "zh_female_vv_uranus_bigtts", "name": "vivi 2.0", "g": "女"},
    {"id": "saturn_zh_female_cancan_tob", "name": "知性灿灿(saturn)", "g": "女"},
    {"id": "saturn_zh_female_keainvsheng_tob", "name": "可爱女生(saturn)", "g": "女"},
    {"id": "saturn_zh_female_tiaopigongzhu_tob", "name": "调皮公主(saturn)", "g": "女"},
    {"id": "saturn_zh_male_shuanglangshaonian_tob", "name": "爽朗少年(saturn)", "g": "男"},
    {"id": "saturn_zh_male_tiancaitongzhuo_tob", "name": "天才同桌(saturn)", "g": "男"},
    {"id": "zh_female_xiaohe_uranus_bigtts", "name": "小何", "g": "女"},
    {"id": "zh_male_m191_uranus_bigtts", "name": "云舟", "g": "男"},
    {"id": "zh_male_taocheng_uranus_bigtts", "name": "小天", "g": "男"},
    {"id": "en_male_tim_uranus_bigtts", "name": "Tim (EN)", "g": "男"},
    {"id": "en_female_dacey_uranus_bigtts", "name": "Dacey (EN)", "g": "女"},
    {"id": "en_female_stokie_uranus_bigtts", "name": "Stokie (EN)", "g": "女"},
    {"id": "zh_male_liufei_uranus_bigtts", "name": "刘飞 2.0", "g": "男"},
    {"id": "zh_female_qingxinnvsheng_uranus_bigtts", "name": "清新女声 2.0", "g": "女"},
    {"id": "zh_female_cancan_uranus_bigtts", "name": "知性灿灿 2.0", "g": "女"},
    {"id": "zh_female_sajiaoxuemei_uranus_bigtts", "name": "撒娇学妹 2.0", "g": "女"},
    {"id": "zh_female_tianmeixiaoyuan_uranus_bigtts", "name": "甜美小源 2.0", "g": "女"},
    {"id": "zh_female_tianmeitaozi_uranus_bigtts", "name": "甜美桃子 2.0", "g": "女"},
    {"id": "zh_female_shuangkuaisisi_uranus_bigtts", "name": "爽快思思 2.0", "g": "女"},
    {"id": "zh_female_peiqi_uranus_bigtts", "name": "佩奇猪 2.0", "g": "女"},
    {"id": "zh_female_linjianvhai_uranus_bigtts", "name": "邻家女孩 2.0", "g": "女"},
    {"id": "zh_male_shaonianzixin_uranus_bigtts", "name": "少年梓辛 2.0", "g": "男"},
    {"id": "zh_male_sunwukong_uranus_bigtts", "name": "猴哥 2.0", "g": "男"},
    {"id": "zh_female_yingyujiaoxue_uranus_bigtts", "name": "Tina老师 2.0", "g": "女"},
    {"id": "zh_female_kefunvsheng_uranus_bigtts", "name": "暖阳女声 2.0", "g": "女"},
    {"id": "zh_female_xiaoxue_uranus_bigtts", "name": "儿童绘本 2.0", "g": "女"},
    {"id": "zh_male_dayi_uranus_bigtts", "name": "大壹 2.0", "g": "男"},
    {"id": "zh_female_mizai_uranus_bigtts", "name": "黑猫侦探社咪仔", "g": "女"},
    {"id": "zh_female_jitangnv_uranus_bigtts", "name": "鸡汤女 2.0", "g": "女"},
    {"id": "zh_female_meilinvyou_uranus_bigtts", "name": "魅力女友 2.0", "g": "女"},
    {"id": "zh_female_liuchangnv_uranus_bigtts", "name": "流畅女声 2.0", "g": "女"},
    {"id": "zh_male_ruyayichen_uranus_bigtts", "name": "儒雅逸辰 2.0", "g": "男"},
    {"id": "zh_female_wenroumama_uranus_bigtts", "name": "温柔妈妈 2.0", "g": "女"},
    {"id": "zh_male_jieshuoxiaoming_uranus_bigtts", "name": "解说小明 2.0", "g": "男"},
    {"id": "zh_female_tvbnv_uranus_bigtts", "name": "TVB女声 2.0", "g": "女"},
    {"id": "zh_male_yizhipiannan_uranus_bigtts", "name": "译制片男 2.0", "g": "男"},
    {"id": "zh_female_qiaopinv_uranus_bigtts", "name": "俏皮女声 2.0", "g": "女"},
    {"id": "zh_female_zhishuaiyingzi_uranus_bigtts", "name": "直率英子 2.0", "g": "女"},
    {"id": "zh_male_linjiananhai_uranus_bigtts", "name": "邻家男孩 2.0", "g": "男"},
    {"id": "zh_male_silang_uranus_bigtts", "name": "四郎 2.0", "g": "男"},
    {"id": "zh_male_ruyaqingnian_uranus_bigtts", "name": "儒雅青年 2.0", "g": "男"},
    {"id": "zh_male_qingcang_uranus_bigtts", "name": "擎苍 2.0", "g": "男"},
    {"id": "zh_male_xionger_uranus_bigtts", "name": "熊二 2.0", "g": "男"},
    {"id": "zh_female_yingtaowanzi_uranus_bigtts", "name": "樱桃丸子 2.0", "g": "女"},
    {"id": "zh_male_wennuanahu_uranus_bigtts", "name": "温暖阿虎 2.0", "g": "男"},
    {"id": "zh_male_naiqimengwa_uranus_bigtts", "name": "奶气萌娃 2.0", "g": "男"},
    {"id": "zh_female_popo_uranus_bigtts", "name": "婆婆 2.0", "g": "女"},
    {"id": "zh_female_gaolengyujie_uranus_bigtts", "name": "高冷御姐 2.0", "g": "女"},
    {"id": "zh_male_aojiaobazong_uranus_bigtts", "name": "傲娇霸总 2.0", "g": "男"},
    {"id": "zh_male_lanyinmianbao_uranus_bigtts", "name": "懒音绵宝 2.0", "g": "男"},
    {"id": "zh_male_fanjuanqingnian_uranus_bigtts", "name": "反卷青年 2.0", "g": "男"},
    {"id": "zh_female_wenroushunv_uranus_bigtts", "name": "温柔淑女 2.0", "g": "女"},
    {"id": "zh_female_gufengshaoyu_uranus_bigtts", "name": "古风少御 2.0", "g": "女"},
    {"id": "zh_male_huolixiaoge_uranus_bigtts", "name": "活力小哥 2.0", "g": "男"},
    {"id": "zh_male_baqiqingshu_uranus_bigtts", "name": "霸气青叔 2.0", "g": "男"},
    {"id": "zh_male_xuanyijieshuo_uranus_bigtts", "name": "悬疑解说 2.0", "g": "男"},
    {"id": "zh_female_mengyatou_uranus_bigtts", "name": "萌丫头 2.0", "g": "女"},
    {"id": "zh_female_tiexinnvsheng_uranus_bigtts", "name": "贴心女声 2.0", "g": "女"},
    {"id": "zh_female_jitangmei_uranus_bigtts", "name": "鸡汤妹妹 2.0", "g": "女"},
    {"id": "zh_male_cixingjieshuonan_uranus_bigtts", "name": "磁性解说男声 2.0", "g": "男"},
    {"id": "zh_male_liangsangmengzai_uranus_bigtts", "name": "亮嗓萌仔 2.0", "g": "男"},
    {"id": "zh_female_kailangjiejie_uranus_bigtts", "name": "开朗姐姐 2.0", "g": "女"},
    {"id": "zh_male_gaolengchenwen_uranus_bigtts", "name": "高冷沉稳 2.0", "g": "男"},
    {"id": "zh_male_shenyeboke_uranus_bigtts", "name": "深夜播客 2.0", "g": "男"},
    {"id": "zh_male_lubanqihao_uranus_bigtts", "name": "鲁班七号 2.0", "g": "男"},
    {"id": "zh_female_jiaochuannv_uranus_bigtts", "name": "娇喘女声 2.0", "g": "女"},
    {"id": "zh_female_linxiao_uranus_bigtts", "name": "林潇 2.0", "g": "女"},
    {"id": "zh_female_lingling_uranus_bigtts", "name": "玲玲姐姐 2.0", "g": "女"},
    {"id": "zh_female_chunribu_uranus_bigtts", "name": "春日部姐姐 2.0", "g": "女"},
    {"id": "zh_male_tangseng_uranus_bigtts", "name": "唐僧 2.0", "g": "男"},
    {"id": "zh_male_zhuangzhou_uranus_bigtts", "name": "庄周 2.0", "g": "男"},
    {"id": "zh_male_kailangdidi_uranus_bigtts", "name": "开朗弟弟 2.0", "g": "男"},
    {"id": "zh_male_zhubajie_uranus_bigtts", "name": "猪八戒 2.0", "g": "男"},
    {"id": "zh_female_ganmaodianyin_uranus_bigtts", "name": "感冒电音姐姐 2.0", "g": "女"},
    {"id": "zh_female_chanmeinv_uranus_bigtts", "name": "谄媚女声 2.0", "g": "女"},
    {"id": "zh_female_nvleishen_uranus_bigtts", "name": "女雷神 2.0", "g": "女"},
    {"id": "zh_female_qinqienv_uranus_bigtts", "name": "亲切女声 2.0", "g": "女"},
    {"id": "zh_male_kuailexiaodong_uranus_bigtts", "name": "快乐小东 2.0", "g": "男"},
    {"id": "zh_male_kailangxuezhang_uranus_bigtts", "name": "开朗学长 2.0", "g": "男"},
    {"id": "zh_male_youyoujunzi_uranus_bigtts", "name": "悠悠君子 2.0", "g": "男"},
    {"id": "zh_female_wenjingmaomao_uranus_bigtts", "name": "文静毛毛 2.0", "g": "女"},
    {"id": "zh_female_zhixingnv_uranus_bigtts", "name": "知性女声 2.0", "g": "女"},
    {"id": "zh_male_qingshuangnanda_uranus_bigtts", "name": "清爽男大 2.0", "g": "男"},
    {"id": "zh_male_yuanboxiaoshu_uranus_bigtts", "name": "渊博小叔 2.0", "g": "男"},
    {"id": "zh_male_yangguangqingnian_uranus_bigtts", "name": "阳光青年 2.0", "g": "男"},
    {"id": "zh_female_qingchezizi_uranus_bigtts", "name": "清澈梓梓 2.0", "g": "女"},
    {"id": "zh_female_tianmeiyueyue_uranus_bigtts", "name": "甜美悦悦 2.0", "g": "女"},
    {"id": "zh_female_xinlingjitang_uranus_bigtts", "name": "心灵鸡汤 2.0", "g": "女"},
    {"id": "zh_male_wenrouxiaoge_uranus_bigtts", "name": "温柔小哥 2.0", "g": "男"},
    {"id": "zh_female_roumeinvyou_uranus_bigtts", "name": "柔美女友 2.0", "g": "女"},
    {"id": "zh_male_dongfanghaoran_uranus_bigtts", "name": "东方浩然 2.0", "g": "男"},
    {"id": "zh_female_wenrouxiaoya_uranus_bigtts", "name": "温柔小雅 2.0", "g": "女"},
    {"id": "zh_male_tiancaitongsheng_uranus_bigtts", "name": "天才童声 2.0", "g": "男"},
    {"id": "zh_female_wuzetian_uranus_bigtts", "name": "武则天 2.0", "g": "女"},
    {"id": "zh_female_gujie_uranus_bigtts", "name": "顾姐 2.0", "g": "女"},
    {"id": "zh_male_guanggaojieshuo_uranus_bigtts", "name": "广告解说 2.0", "g": "男"},
    {"id": "zh_female_shaoergushi_uranus_bigtts", "name": "少儿故事 2.0", "g": "女"},
    {"id": "zh_female_sophie_uranus_bigtts", "name": "魅力苏菲 2.0", "g": "女"},
    {"id": "saturn_zh_male_qingxinmumu_cs_tob", "name": "清新沐沐(saturn CS)", "g": "男"},
]


# ── TTS generation ────────────────────────────────────────────────────────
def generate(text: str, voice_id: str, output_path: Path) -> dict:
    req_id = str(uuid.uuid4())
    h = {
        "X-Api-Key": API_KEY, "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": req_id, "Content-Type": "application/json",
    }
    body = {
        "user": {"uid": "vp"}, "unique_id": req_id,
        "req_params": {
            "text": text, "speaker": voice_id,
            "audio_params": {"format": "mp3", "sample_rate": 24000,
                             "speech_rate": SPEECH_RATE, "enable_timestamp": False},
            "additions": json.dumps({"disable_markdown_filter": False}, ensure_ascii=False),
        },
    }
    try:
        r = requests.post("https://openspeech.bytedance.com/api/v3/tts/submit",
                          headers=h, json=body, timeout=(10, 60), proxies=_NO_PROXY)
        d = r.json()
    except Exception as e:
        return {"error": str(e)}
    c = d.get("code", -1)
    if c != 20000000:
        return {"error": d.get("message", f"code={c}")}
    tid = d.get("data", {}).get("task_id")
    if not tid:
        return {"error": "no task_id"}
    dl = time.time() + 120
    while time.time() < dl:
        time.sleep(2)
        try:
            qr = requests.post("https://openspeech.bytedance.com/api/v3/tts/query",
                               headers={**h, "X-Api-Request-Id": str(uuid.uuid4())},
                               json={"task_id": tid}, timeout=(10, 60), proxies=_NO_PROXY)
            qd = qr.json()
        except Exception:
            continue
        ts = qd.get("data", {}).get("task_status")
        if ts == 2:
            au = qd["data"].get("audio_url")
            if not au:
                return {"error": "no audio_url"}
            ar = requests.get(au, timeout=(10, 120),
                              proxies={"http": None, "https": None})
            ar.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(ar.content)
            return {"path": str(output_path), "dur": _dur(output_path)}
        elif ts == 3:
            return {"error": qd.get("message", "failed")}
    return {"error": "timeout"}


def _dur(p: Path) -> float | None:
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True, timeout=10)
        return round(float(r.stdout.strip()), 1)
    except Exception:
        return None


# ── HTML generation ───────────────────────────────────────────────────────
def data_uri(fp: str) -> str:
    with open(fp, "rb") as f:
        return "data:audio/mp3;base64," + base64.b64encode(f.read()).decode()


_CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{background:#F5F0EB;font-family:"PingFang SC","Noto Serif SC",system-ui,sans-serif;color:#3C3833;padding:24px 36px;max-width:1200px;margin:0 auto}
h1{font-size:24px;font-weight:500;margin-bottom:2px}
.sub{color:#8B7D73;font-size:12px;margin-bottom:4px}
.meta{color:#A09080;font-size:10px;margin-bottom:20px;padding:6px 12px;background:rgba(212,201,192,0.3);border-radius:5px;border-left:2px solid #D4C9C0;line-height:1.6}
.meta code{font-size:9px;background:#EDE7E0;padding:1px 4px;border-radius:2px;color:#6B5D4F}
.tabs{display:flex;gap:8px;margin-bottom:14px}
.tab{padding:5px 14px;border:1px solid #D4C9C0;border-radius:5px;background:#FDFAF6;cursor:pointer;font-size:12px;color:#6B5D4F;transition:.15s}
.tab:hover,.tab.sel{background:#4A3728;color:#F5F0EB;border-color:#4A3728}
.tab.sel{font-weight:500}
.tc{display:none}.tc.sel{display:block}
h2{font-size:15px;font-weight:500;color:#4A3728;margin-bottom:8px;padding-bottom:3px;border-bottom:1px solid #E8E0D8}
.cnt{font-size:10px;color:#A09080;font-weight:400;margin-left:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));gap:6px;margin-bottom:18px}
.vc{background:#FDFAF6;border:1px solid #E8E0D8;border-radius:6px;padding:8px 12px;transition:box-shadow .12s}
.vc:hover{box-shadow:0 1px 6px rgba(60,56,51,0.05)}.vc.fail{opacity:0.4}
.vch{display:flex;align-items:baseline;gap:7px;margin-bottom:5px;flex-wrap:wrap}
.vch b{font-size:13px;font-weight:500;color:#4A3728}
.g{font-size:8px;padding:1px 5px;border-radius:5px;background:#E8E0D8;color:#6B5D4F;font-weight:500}
.vid{font-size:7px;color:#B0A090;font-family:Menlo,monospace;margin-left:auto;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.player{display:flex;align-items:center;gap:6px}
.player audio{flex:1;height:28px}
.dur{font-size:9px;color:#8B9D83;min-width:24px;text-align:right}
.err{color:#C17767;font-size:10px}
audio::-webkit-media-controls-panel{background:#F5F0EB}
.foot{font-size:10px;color:#A09080;margin-top:20px;padding-top:10px;border-top:1px solid #E8E0D8;line-height:1.6}"""

_JS = """function t(n){document.querySelectorAll('.tab').forEach(function(e){e.classList.toggle('sel',e.textContent.indexOf(n)===0)});document.querySelectorAll('.tc').forEach(function(e){e.classList.toggle('sel',e.id==='tab'+n)})}"""


def make_html(results: dict) -> Path:
    females, males = [], []
    for v in VOICES:
        res = results.get(v["id"])
        vid, name, g = v["id"], v["name"], v["g"]
        if not res or "error" in res:
            card = ('<div class="vc fail"><div class="vch"><b>{name}</b>'
                    '<span class="g">{g}</span><span class="vid">{vid}</span></div>'
                    '<span class="err">{err}</span></div>').format(
                name=name, g=g, vid=vid, err=(res or {}).get("error", "?"))
        else:
            src = data_uri(res["path"])
            dur = res.get("dur") or 0
            card = ('<div class="vc"><div class="vch"><b>{name}</b>'
                    '<span class="g">{g}</span><span class="vid">{vid}</span></div>'
                    '<div class="player"><audio controls preload="auto" src="{src}"></audio>'
                    '<span class="dur">{dur}s</span></div></div>').format(
                name=name, g=g, vid=vid, src=src, dur=dur)
        (females if g == "女" else males).append(card)

    def section(title, cards_list):
        return '<h2>{title}<span class="cnt">{n}</span></h2><div class="grid">{cards}</div>'.format(
            title=title, n=len(cards_list), cards="".join(cards_list))

    ok = sum(1 for r in results.values() if "error" not in r)
    html = """<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>TTS音色试听 · {total}个音色</title><style>{css}</style></head><body>
<h1>&#x1f399; TTS 音色试听</h1>
<p class="sub">「{sample}」 — 语速{rate:+d}</p>
<div class="meta"><strong>引擎:</strong> doubao_tts · {rid} · {total}个音色 · {ok}个可用 · 音频base64内嵌<br>
<strong>使用:</strong> 点击&#x25b6;试听 → 选中音色 → 将 <code>voice_id</code> 告诉 agent</div>
<div class="tabs">
<span class="tab sel" onclick="t('全部')">全部 ({total})</span>
<span class="tab" onclick="t('女声')">女声 ({fn})</span>
<span class="tab" onclick="t('男声')">男声 ({mn})</span>
</div>
<div class="tc sel" id="tab全部">{all_sec}</div>
<div class="tc" id="tab女声">{female_sec}</div>
<div class="tc" id="tab男声">{male_sec}</div>
<script>{js}</script>
<p class="foot"><strong>更多音色:</strong> 火山引擎 → 语音合成 → 音色管理 → 复制 Voice_type 添加到脚本重新生成。全部{total}个音色均在 seed-tts-2.0 资源下可用。</p>
</body></html>""".format(
        total=len(VOICES), fn=len(females), mn=len(males), ok=ok,
        sample=SAMPLE_TEXT, rate=SPEECH_RATE, rid=RESOURCE_ID,
        css=_CSS, js=_JS,
        all_sec=section("全部音色", females + males),
        female_sec=section("女声", females),
        male_sec=section("男声", males),
    )

    hp = OUTPUT_DIR / "voice-preview.html"
    hp.write_text(html, encoding="utf-8")
    return hp


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    if not API_KEY:
        print("ERROR: DOUBAO_SPEECH_API_KEY not found"); sys.exit(1)
    print(f"生成 {len(VOICES)} 音色, 语速{SPEECH_RATE:+d}, 资源{RESOURCE_ID}\n")
    results = {}
    for i, v in enumerate(VOICES):
        vid, name = v["id"], v["name"]
        out = SAMPLES_DIR / f'{vid.replace("_", "-")}_r{SPEECH_RATE:+d}.mp3'
        print(f"  [{i+1:3d}/{len(VOICES)}] {name:16s} ... ", end="", flush=True)
        t0 = time.time()
        res = generate(SAMPLE_TEXT, vid, out)
        el = time.time() - t0
        if "error" in res:
            print(f"FAIL ({el:.0f}s) {res['error']}")
        else:
            print(f"OK {res.get('dur', 0):.1f}s ({el:.0f}s)")
        results[vid] = res
    hp = make_html(results)
    ok = sum(1 for r in results.values() if "error" not in r)
    print(f"\n{hp}  ({ok}/{len(VOICES)} 可用)")
    subprocess.Popen(["open", str(hp)])


if __name__ == "__main__":
    main()
