"""
AI Coach floating action button — injected into the Streamlit parent page.
Uses components.html (height=0 iframe) + window.parent to run JS.
"""

import os
import streamlit.components.v1 as components
import streamlit as st

# Server-side URL (Python/httpx): may be internal Docker hostname
_API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")
# Browser-side URL (JavaScript fetch): must be reachable from the user's browser
# Use 127.0.0.1 explicitly — on Windows, "localhost" may resolve to IPv6 (::1)
# which fails when uvicorn only listens on IPv4.
_PUBLIC_API_BASE = os.environ.get("PUBLIC_API_BASE", "http://127.0.0.1:8000")


_FAB_CSS_LIGHT = """
    #ai-fab{position:fixed;right:1.5rem;bottom:2rem;z-index:99999;width:54px;height:54px;
      border-radius:50%;background:#059669;border:none;cursor:pointer;font-size:1.4rem;
      box-shadow:0 4px 20px rgba(5,150,105,.35);transition:transform .2s,box-shadow .2s;
      display:flex;align-items:center;justify-content:center;color:#FFFFFF;font-weight:700;}
    #ai-fab:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(5,150,105,.5);}
    #ai-overlay{display:none;position:fixed;inset:0;background:rgba(15,23,42,.35);z-index:99998;backdrop-filter:blur(2px);}
    #ai-drawer{position:fixed;top:0;right:0;height:100vh;width:370px;max-width:95vw;z-index:99999;
      background:#FFFFFF;border-left:1px solid #E2E8F0;box-shadow:-8px 0 40px rgba(0,0,0,.12);
      display:flex;flex-direction:column;transform:translateX(100%);
      transition:transform .3s cubic-bezier(.4,0,.2,1);font-family:'Inter',-apple-system,sans-serif;}
    #ai-drawer.open{transform:translateX(0);}
    #ai-overlay.open{display:block;}
    #ai-hdr{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;
      border-bottom:1px solid #E2E8F0;background:linear-gradient(135deg,rgba(5,150,105,.06),transparent);}
    #ai-hdr-title{font-size:1rem;font-weight:700;color:#0F172A;display:flex;align-items:center;gap:.5rem;}
    .ai-badge{font-size:.6rem;background:rgba(5,150,105,.1);color:#059669;border:1px solid rgba(5,150,105,.25);
      border-radius:20px;padding:.1rem .45rem;font-weight:600;}
    #ai-close{background:#F1F5F9;border:1px solid #E2E8F0;color:#64748B;
      border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:.9rem;
      display:flex;align-items:center;justify-content:center;transition:all .15s;}
    #ai-close:hover{background:rgba(5,150,105,.1);color:#059669;border-color:rgba(5,150,105,.3);}
    #ai-pills{display:flex;flex-wrap:wrap;gap:.35rem;padding:.6rem 1.25rem;border-bottom:1px solid #E2E8F0;}
    .ai-pill{background:#F8FAFC;border:1px solid #E2E8F0;color:#64748B;border-radius:20px;
      padding:.22rem .65rem;font-size:.72rem;cursor:pointer;transition:all .15s;font-family:inherit;}
    .ai-pill:hover{background:rgba(5,150,105,.08);border-color:rgba(5,150,105,.35);color:#059669;}
    #ai-msgs{flex:1;overflow-y:auto;padding:1rem 1.25rem;display:flex;flex-direction:column;gap:.5rem;scroll-behavior:smooth;}
    #ai-msgs::-webkit-scrollbar{width:4px;}
    #ai-msgs::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:4px;}
    .ai-row-user{display:flex;flex-direction:column;align-items:flex-end;}
    .ai-row-ai{display:flex;flex-direction:column;align-items:flex-start;}
    .ai-lbl{font-size:.66rem;font-weight:600;margin-bottom:.15rem;padding:0 .2rem;}
    .ai-lbl.user{color:#059669;}.ai-lbl.ai{color:#0891B2;}
    .ai-bbl{max-width:90%;padding:.45rem .75rem;border-radius:10px;font-size:.83rem;line-height:1.5;}
    .ai-bbl.user{background:#059669;color:#FFFFFF;font-weight:500;border-bottom-right-radius:3px;}
    .ai-bbl.ai{background:#F1F5F9;border:1px solid #E2E8F0;color:#0F172A;border-bottom-left-radius:3px;}
    #ai-input-bar{display:flex;gap:.4rem;padding:.8rem 1.25rem;border-top:1px solid #E2E8F0;}
    #ai-input{flex:1;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;color:#0F172A;
      font-size:.875rem;padding:.5rem .8rem;outline:none;font-family:inherit;transition:border-color .15s;}
    #ai-input::placeholder{color:#94A3B8;}
    #ai-input:focus{border-color:#059669;box-shadow:0 0 0 3px rgba(5,150,105,.12);}
    #ai-send{background:#059669;border:none;border-radius:8px;color:#FFFFFF;width:40px;height:40px;
      cursor:pointer;font-size:.9rem;display:flex;align-items:center;justify-content:center;
      transition:transform .15s,box-shadow .15s;flex-shrink:0;font-weight:700;}
    #ai-send:hover{transform:scale(1.08);box-shadow:0 4px 14px rgba(5,150,105,.35);}
    #ai-send:disabled{opacity:.5;cursor:not-allowed;transform:none;}
"""

_FAB_CSS_DARK = """
    #ai-fab{position:fixed;right:1.5rem;bottom:2rem;z-index:99999;width:54px;height:54px;
      border-radius:50%;background:#10B981;border:none;cursor:pointer;font-size:1.4rem;
      box-shadow:0 4px 20px rgba(16,185,129,.4);transition:transform .2s,box-shadow .2s;
      display:flex;align-items:center;justify-content:center;color:#000;font-weight:700;}
    #ai-fab:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(16,185,129,.6);}
    #ai-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:99998;backdrop-filter:blur(2px);}
    #ai-drawer{position:fixed;top:0;right:0;height:100vh;width:370px;max-width:95vw;z-index:99999;
      background:#0D0D0D;border-left:1px solid #252525;box-shadow:-8px 0 40px rgba(0,0,0,.8);
      display:flex;flex-direction:column;transform:translateX(100%);
      transition:transform .3s cubic-bezier(.4,0,.2,1);font-family:'Inter',-apple-system,sans-serif;}
    #ai-drawer.open{transform:translateX(0);}
    #ai-overlay.open{display:block;}
    #ai-hdr{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;
      border-bottom:1px solid #252525;background:linear-gradient(135deg,rgba(16,185,129,.08),transparent);}
    #ai-hdr-title{font-size:1rem;font-weight:700;color:#F1F5F9;display:flex;align-items:center;gap:.5rem;}
    .ai-badge{font-size:.6rem;background:rgba(16,185,129,.15);color:#10B981;border:1px solid rgba(16,185,129,.3);
      border-radius:20px;padding:.1rem .45rem;font-weight:600;}
    #ai-close{background:rgba(255,255,255,.06);border:1px solid #333;color:#9CA3AF;
      border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:.9rem;
      display:flex;align-items:center;justify-content:center;transition:all .15s;}
    #ai-close:hover{background:rgba(16,185,129,.15);color:#10B981;border-color:rgba(16,185,129,.3);}
    #ai-pills{display:flex;flex-wrap:wrap;gap:.35rem;padding:.6rem 1.25rem;border-bottom:1px solid #1A1A1A;}
    .ai-pill{background:#1A1A1A;border:1px solid #333;color:#9CA3AF;border-radius:20px;
      padding:.22rem .65rem;font-size:.72rem;cursor:pointer;transition:all .15s;font-family:inherit;}
    .ai-pill:hover{background:rgba(16,185,129,.12);border-color:rgba(16,185,129,.4);color:#10B981;}
    #ai-msgs{flex:1;overflow-y:auto;padding:1rem 1.25rem;display:flex;flex-direction:column;gap:.5rem;scroll-behavior:smooth;}
    #ai-msgs::-webkit-scrollbar{width:4px;}
    #ai-msgs::-webkit-scrollbar-thumb{background:rgba(16,185,129,.25);border-radius:4px;}
    .ai-row-user{display:flex;flex-direction:column;align-items:flex-end;}
    .ai-row-ai{display:flex;flex-direction:column;align-items:flex-start;}
    .ai-lbl{font-size:.66rem;font-weight:600;margin-bottom:.15rem;padding:0 .2rem;}
    .ai-lbl.user{color:#10B981;}.ai-lbl.ai{color:#0891B2;}
    .ai-bbl{max-width:90%;padding:.45rem .75rem;border-radius:10px;font-size:.83rem;line-height:1.5;}
    .ai-bbl.user{background:#10B981;color:#000;font-weight:500;border-bottom-right-radius:3px;}
    .ai-bbl.ai{background:#1A1A1A;border:1px solid #333;color:#F1F5F9;border-bottom-left-radius:3px;}
    #ai-input-bar{display:flex;gap:.4rem;padding:.8rem 1.25rem;border-top:1px solid #252525;}
    #ai-input{flex:1;background:#1A1A1A;border:1px solid #333;border-radius:8px;color:#F1F5F9;
      font-size:.875rem;padding:.5rem .8rem;outline:none;font-family:inherit;transition:border-color .15s;}
    #ai-input::placeholder{color:#6B7280;}
    #ai-input:focus{border-color:#10B981;box-shadow:0 0 0 3px rgba(16,185,129,.15);}
    #ai-send{background:#10B981;border:none;border-radius:8px;color:#000;width:40px;height:40px;
      cursor:pointer;font-size:.9rem;display:flex;align-items:center;justify-content:center;
      transition:transform .15s,box-shadow .15s;flex-shrink:0;font-weight:700;}
    #ai-send:hover{transform:scale(1.08);box-shadow:0 4px 14px rgba(16,185,129,.45);}
    #ai-send:disabled{opacity:.5;cursor:not-allowed;transform:none;}
"""


def render(token: str, pid: str) -> None:
    """Inject the AI coach FAB into the Streamlit parent window."""
    theme = st.session_state.get("theme", "light")
    no_profile_msg = "" if pid else "Please select a profile first."
    safe_token = token.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    safe_pid   = pid.replace("\\", "\\\\")
    safe_np    = no_profile_msg.replace("\\", "\\\\")
    _fab_css   = _FAB_CSS_DARK if theme == "dark" else _FAB_CSS_LIGHT
    css        = _fab_css.replace("`", "\\`").replace("${", "\\${")

    components.html(f"""<script>
(function(){{
  var par=window.parent,doc=par.document;
  par._aiCreds={{token:`{safe_token}`,pid:`{safe_pid}`,noProf:`{safe_np}`}};
  // Update CSS whenever theme changes — remove old style, inject new one
  var oldStyle=doc.getElementById('ai-fab-style');
  if(oldStyle)oldStyle.remove();
  var s=doc.createElement('style');s.id='ai-fab-style';s.textContent=`{css}`;doc.head.appendChild(s);
  if(doc.getElementById('ai-fab-root'))return;
  var root=doc.createElement('div');root.id='ai-fab-root';
  root.innerHTML=`
    <div id="ai-overlay" onclick="window._aiClose()"></div>
    <button id="ai-fab" onclick="window._aiToggle()" title="AI Coach" style="font-size:.85rem;font-weight:800;letter-spacing:.02em;">AI</button>
    <div id="ai-drawer">
      <div id="ai-hdr">
        <div id="ai-hdr-title"><span>AI Coach</span><span class="ai-badge">ONLINE</span></div>
        <button id="ai-close" onclick="window._aiClose()">✕</button>
      </div>
      <div id="ai-pills">
        <button class="ai-pill" onclick="window._aiQuick('Nutrition plan')">Nutrition</button>
        <button class="ai-pill" onclick="window._aiQuick('Workout tips')">Workout</button>
        <button class="ai-pill" onclick="window._aiQuick('Progress check')">Progress</button>
        <button class="ai-pill" onclick="window._aiQuick('Motivate me')">Motivate</button>
      </div>
      <div id="ai-msgs">
        <div class="ai-row-ai">
          <div class="ai-lbl ai">Coach</div>
          <div class="ai-bbl ai">Hey! I'm your AI fitness coach. Ask me anything.</div>
        </div>
      </div>
      <div id="ai-input-bar">
        <input id="ai-input" type="text" placeholder="Ask anything…"/>
        <button id="ai-send" onclick="window._aiSend()">➤</button>
      </div>
    </div>
  `;
  doc.body.appendChild(root);
  doc.getElementById('ai-input').addEventListener('keydown',function(e){{
    if(e.key==='Enter'&&!e.shiftKey){{e.preventDefault();window._aiSend();}}
  }});
  par._aiToggle=function(){{doc.getElementById('ai-drawer').classList.contains('open')?par._aiClose():par._aiOpen();}};
  par._aiOpen=function(){{
    doc.getElementById('ai-drawer').classList.add('open');
    doc.getElementById('ai-overlay').classList.add('open');
    doc.getElementById('ai-fab').textContent='✕';
    setTimeout(function(){{doc.getElementById('ai-input').focus();}},350);
  }};
  par._aiClose=function(){{
    doc.getElementById('ai-drawer').classList.remove('open');
    doc.getElementById('ai-overlay').classList.remove('open');
    doc.getElementById('ai-fab').textContent='AI';
  }};
  par._aiQuick=function(t){{doc.getElementById('ai-input').value=t;par._aiSend();}};
  par._aiSend=async function(){{
    var c=par._aiCreds||{{}},inp=doc.getElementById('ai-input'),btn=doc.getElementById('ai-send'),txt=inp.value.trim();
    if(!txt)return;
    if(c.noProf){{_aiAdd('ai','⚠️ '+c.noProf);return;}}
    inp.value='';btn.disabled=true;_aiAdd('user',txt);
    var typing=_aiTyping();
    try{{
      var res=await par.fetch('{_PUBLIC_API_BASE}/ai/chat',{{method:'POST',
        headers:{{'Content-Type':'application/json','Authorization':'Bearer '+c.token}},
        body:JSON.stringify({{profile_id:c.pid,message:txt}})}});
      typing.remove();
      if(res.ok){{var d=await res.json();_aiAdd('ai',d.reply||'No response');}}
      else if(res.status===401){{_aiAdd('ai','⚠️ Session expired — please log in again.');}}
      else{{var e=await res.json().catch(function(){{return {{}};}});_aiAdd('ai','⚠️ '+(e.detail||res.statusText));}}
    }}catch(e){{typing.remove();_aiAdd('ai','⚠️ Connection error — is the backend running?');}}
    btn.disabled=false;inp.focus();
  }};
  function _aiAdd(role,text){{
    var msgs=doc.getElementById('ai-msgs');
    var row=doc.createElement('div');row.className='ai-row-'+role;
    var lbl=doc.createElement('div');lbl.className='ai-lbl '+role;lbl.textContent=role==='user'?'You':'Coach';
    var bbl=doc.createElement('div');bbl.className='ai-bbl '+role;bbl.textContent=text;
    row.appendChild(lbl);row.appendChild(bbl);msgs.appendChild(row);
    msgs.scrollTop=msgs.scrollHeight;return row;
  }}
  function _aiTyping(){{
    var msgs=doc.getElementById('ai-msgs');
    var row=doc.createElement('div');row.className='ai-row-ai';
    var lbl=doc.createElement('div');lbl.className='ai-lbl ai';lbl.textContent='Coach';
    var d=doc.createElement('div');
    d.className='ai-bbl ai';d.style.cssText='display:flex;gap:4px;width:fit-content;';
    if(!doc.getElementById('ai-bounce-style')){{
      var ks=doc.createElement('style');ks.id='ai-bounce-style';
      ks.textContent='@keyframes ai-bounce{{0%,60%,100%{{transform:translateY(0);opacity:.4;}}30%{{transform:translateY(-5px);opacity:1;}}}}';
      doc.head.appendChild(ks);
    }}
    var dot='<span style="width:6px;height:6px;background:#9CA3AF;border-radius:50%;display:inline-block;animation:ai-bounce 1.2s infinite;"></span>';
    d.innerHTML=dot+dot.replace('infinite','1.2s .2s infinite')+dot.replace('infinite','1.2s .4s infinite');
    row.appendChild(lbl);row.appendChild(d);msgs.appendChild(row);msgs.scrollTop=msgs.scrollHeight;return row;
  }}
}})();
</script>""", height=0)
