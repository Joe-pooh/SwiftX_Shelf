const Auth = {
  async login(){
    const username = document.getElementById('loginUser').value.trim();
    const password = document.getElementById('loginPass').value.trim();
    if(!username || !password){ alert('请输入用户名和密码'); return; }
    const r = await apiFetch('/auth/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
    if(!r.ok){ alert('登录失败：' + await r.text()); return; }
    const data = await r.json();
    App.token = data.token; localStorage.setItem('TOKEN', data.token);
    localStorage.setItem('USER', JSON.stringify(data.user));
    document.getElementById('userLabel').textContent = '已登录：' + data.user.username;
    document.getElementById('userLabel').classList.remove('hidden');
    document.getElementById('navbar').classList.remove('hidden');
    App.beep(800, 120);
  },
  async logout(){
    await apiFetch('/auth/logout', { method:'POST' });
    localStorage.removeItem('TOKEN'); localStorage.removeItem('USER'); App.token=null;
    document.getElementById('navbar').classList.add('hidden');
    document.getElementById('userLabel').classList.add('hidden');
    App.beep(220, 120);
  }
};
