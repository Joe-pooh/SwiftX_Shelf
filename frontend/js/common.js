const App = {
  BACKEND_BASE: localStorage.getItem('BACKEND_BASE') || (location.origin.includes('github.io') ? 'http://localhost:8000' : (location.origin + '/api')),
  token: localStorage.getItem('TOKEN') || null,
  init(){
    document.getElementById('backendBase').value = this.BACKEND_BASE;
    const user = localStorage.getItem('USER');
    if(user){
      const u = JSON.parse(user);
      document.getElementById('userLabel').textContent = '已登录：' + u.username;
      document.getElementById('userLabel').classList.remove('hidden');
      document.getElementById('navbar').classList.remove('hidden');
      this.show('putaway');
    }
    const pwTrack = document.getElementById('pwTrack'); if(pwTrack) pwTrack.addEventListener('keydown', e=>{ if(e.key==='Enter'){ Putaway.putaway(); }});
    const pkTrack = document.getElementById('pkTrack'); if(pkTrack) pkTrack.addEventListener('keydown', e=>{ if(e.key==='Enter'){ Pick.pick(); }});
  },
  saveBase(){
    const v = document.getElementById('backendBase').value.trim();
    this.BACKEND_BASE = v; localStorage.setItem('BACKEND_BASE', v);
    this.beep(600, 100);
  },
  show(id){
    document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
  },
  log(divId, msg, ok=true){
    const el = document.getElementById(divId);
    const p = document.createElement('div');
    p.innerHTML = (ok? '<span class=ok>✔</span>':'<span class=err>✖</span>') + ' ' + msg;
    el.prepend(p);
  },
  beep(freq=440, dur=100){
    try{
      this.ctx = this.ctx || new (window.AudioContext || window.webkitAudioContext)();
      const o = this.ctx.createOscillator();
      const g = this.ctx.createGain();
      o.connect(g); g.connect(this.ctx.destination);
      o.frequency.value = freq; o.start(); setTimeout(()=>o.stop(), dur);
    }catch(e){}
  }
};
async function apiFetch(path, options={}){
  options.headers = options.headers || {};
  if(App.token){ options.headers['Authorization'] = 'Bearer ' + App.token; }
  const url = App.BACKEND_BASE.replace(/\/$/,'') + path;
  const r = await fetch(url, options);
  if(r.status === 401){
    alert('未登录或登录过期，请重新登录');
    localStorage.removeItem('TOKEN'); localStorage.removeItem('USER'); App.token=null;
    document.getElementById('navbar').classList.add('hidden');
    document.getElementById('userLabel').classList.add('hidden');
    return r;
  }
  return r;
}
