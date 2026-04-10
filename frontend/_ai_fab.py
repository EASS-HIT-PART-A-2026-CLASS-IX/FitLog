"""
AI Coach floating action button — injected into the Streamlit parent page.
Uses components.html (height=0 iframe) + window.parent to run JS.
"""

import streamlit.components.v1 as components
import streamlit as st


_FAB_CSS = """
    #ai-fab{position:fixed;right:1.5rem;bottom:2rem;z-index:99999;width:54px;height:54px;
      border-radius:50%;background:#00FF87;border:none;cursor:pointer;font-size:1.4rem;
      box-shadow:0 4px 20px rgba(0,255,135,.5);transition:transform .2s,box-shadow .2s;
      display:flex;align-items:center;justify-content:center;color:#0A0A0A;font-weight:700;}
    #ai-fab:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(0,255,135,.7);}
    #ai-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:99998;backdrop-filter:blur(2px);}
    #ai-drawer{position:fixed;top:0;right:0;height:100vh;width:370px;max-width:95vw;z-index:99999;
      background:#0D0D0D;border-left:1px solid #1E1E1E;box-shadow:-8px 0 40px rgba(0,0,0,.8);
      display:flex;flex-direction:column;transform:translateX(100%);
      transition:transform .3s cubic-bezier(.4,0,.2,1);font-family:'Inter',-apple-system,sans-serif;}
    #ai-drawer.open{transform:translateX(0);}
    #ai-overlay.open{display:block;}
    #ai-hdr{display:flex;align-items:center;justify-content:space-between;padding:1rem 1.25rem;
      border-bottom:1px solid #1E1E1E;background:linear-gradient(135deg,rgba(0,255,135,.08),transparent);}
    #ai-hdr-title{font-size:1rem;font-weight:700;color:#fff;display:flex;align-items:center;gap:.5rem;}
    .ai-badge{font-size:.6rem;background:rgba(0,255,135,.15);color:#00FF87;border:1px solid rgba(0,255,135,.3);
      border-radius:20px;padding:.1rem .45rem;font-weight:600;}
    #ai-close{background:rgba(255,255,255,.06);border:1px solid #2A2A2A;color:#9CA3AF;
      border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:.9rem;
      display:flex;align-items:center;justify-content:center;transition:all .15s;}
    #ai-close:hover{background:rgba(0,255,135,.15);color:#00FF87;border-color:rgba(0,255,135,.3);}
    #ai-pills{display:flex;flex-wrap:wrap;gap:.35rem;padding:.6rem 1.25rem;border-bottom:1px solid #1A1A1A;}
    .ai-pill{background:#1A1A1A;border:1px solid #2A2A2A;color:#9CA3AF;border-radius:20px;
      padding:.22rem .65rem;font-size:.72rem;cursor:pointer;transition:all .15s;font-family:inherit;}
    .ai-pill:hover{background:rgba(0,255,135,.12);border-color:rgba(0,255,135,.4);color:#00FF87;}
    #ai-msgs{flex:1;overflow-y:auto;padding:1rem 1.25rem;display:flex;flex-direction:column;gap:.5rem;scroll-behavior:smooth;}
    #ai-msgs::-webkit-scrollbar{width:4px;}
    #ai-msgs::-webkit-scrollbar-thumb{background:rgba(0,255,135,.25);border-radius:4px;}
    .ai-row-user{display:flex;flex-direction:column;align-items:flex-end;}
    .ai-row-ai{display:flex;flex-direction:column;align-items:flex-start;}
    .ai-lbl{font-size:.66rem;font-weight:600;margin-bottom:.15rem;padding:0 .2rem;}
    .ai-lbl.user{color:#00FF87;}.ai-lbl.ai{color:#00C2FF;}
    .ai-bbl{max-width:90%;padding:.45rem .75rem;border-radius:10px;font-size:.83rem;line-height:1.5;}
    .ai-bbl.user{background:#00FF87;color:#0A0A0A;font-weight:500;border-bottom-right-radius:3px;}
    .ai-bbl.ai{background:#1A1A1A;border:1px solid #2A2A2A;color:#f9fafb;border-bottom-left-radius:3px;}
    #ai-input-bar{display:flex;gap:.4rem;padding:.8rem 1.25rem;border-top:1px solid #1E1E1E;}
    #ai-input{flex:1;background:#1A1A1A;border:1px solid #2A2A2A;border-radius:8px;color:#fff;
      font-size:.875rem;padding:.5rem .8rem;outline:none;font-family:inherit;transition:border-color .15s;}
    #ai-input::placeholder{color:#6b7280;}
    #ai-input:focus{border-color:#00FF87;box-shadow:0 0 0 3px rgba(0,255,135,.12);}
    #ai-send{background:#00FF87;border:none;border-radius:8px;color:#0A0A0A;width:40px;height:40px;
      cursor:pointer;font-size:.9rem;display:flex;align-items:center;justify-content:center;
      transition:transform .15s,box-shadow .15s;flex-shrink:0;font-weight:700;}
    #ai-send:hover{transform:scale(1.08);box-shadow:0 4px 14px rgba(0,255,135,.45);}
    #ai-send:disabled{opacity:.5;cursor:not-allowed;transform:none;}
"""


def render(token: str, pid: str) -> None:
    """Inject the AI coach FAB into the Streamlit parent window."""
    no_profile_msg = "" if pid else "Please select a profile first."
    safe_token = token.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    safe_pid   = pid.replace("\\", "\\\\")
    safe_np    = no_profile_msg.replace("\\", "\\\\")
    css        = _FAB_CSS.replace("`", "\\`").replace("${", "\\${")

    components.html(f"""<script>
(function(){{
  var par=window.parent,doc=par.document;
  par._aiCreds={{token:`{safe_token}`,pid:`{safe_pid}`,noProf:`{safe_np}`}};
  if(doc.getElementById('ai-fab-root'))return;
  var s=doc.createElement('style');s.textContent=`{css}`;doc.head.appendChild(s);
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
      var res=await fetch('http://localhost:8000/ai/chat',{{method:'POST',
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
    d.style.cssText='display:flex;gap:4px;padding:.45rem .75rem;background:#1A1A1A;border:1px solid #2A2A2A;border-radius:10px;width:fit-content;';
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
