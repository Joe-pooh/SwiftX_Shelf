const Putaway = {
  async createBin(){
    const code = document.getElementById('pwBin').value.trim();
    if(!code){ alert('请输入库位'); return; }
    const r = await apiFetch('/bins', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({code}) });
    if(r.ok){ App.log('pwLog', '创建库位：'+code); App.beep(660,120); } else { App.log('pwLog', '创建库位失败：'+ await r.text(), false); App.beep(220,200); }
  },
  async putaway(){
    const bin_code = document.getElementById('pwBin').value.trim();
    const tracking = document.getElementById('pwTrack').value.trim();
    if(!bin_code || !tracking){ App.beep(220,200); return; }
    const r = await apiFetch('/putaway', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({bin_code, tracking}) });
    if(r.ok){
      const data = await r.json();
      App.log('pwLog', `上架成功：${data.tracking} → ${data.bin_code}`); App.beep(800, 120);
      document.getElementById('pwTrack').value='';
    }else{
      App.log('pwLog', '上架失败：'+ await r.text(), false); App.beep(220, 200);
    }
  }
};
