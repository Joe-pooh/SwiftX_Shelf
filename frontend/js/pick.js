const Pick = {
  targetSet: new Set(),
  pickedSet: new Set(),
  loadTargets(){
    const lines = document.getElementById('pickList').value.split('\n').map(s=>s.trim().toUpperCase()).filter(Boolean);
    this.targetSet = new Set(lines); this.pickedSet = new Set();
    document.getElementById('pkCount').textContent = `0/${this.targetSet.size}`;
    document.getElementById('pkLog').innerHTML='';
    App.log('pkLog', '已载入目标：'+lines.length+' 条'); App.beep(700, 120);
  },
  async pick(){
    const t = document.getElementById('pkTrack').value.trim().toUpperCase();
    if(!t){ return; }
    if(this.targetSet.size === 0){
      App.log('pkLog', '请先载入拣选任务', false); App.beep(220,200); document.getElementById('pkTrack').value=''; return;
    }
    if(!this.targetSet.has(t)){
      App.log('pkLog', '非本次目标：'+t, false); App.beep(240, 250);
      document.getElementById('pkTrack').value=''; return;
    }
    const r = await apiFetch('/pick', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({tracking:t}) });
    if(r.ok){
      this.pickedSet.add(t);
      App.log('pkLog', '命中并下架：'+t, true); App.beep(880, 120);
    }else{
      App.log('pkLog', '下架失败：'+ await r.text(), false); App.beep(220, 220);
    }
    document.getElementById('pkTrack').value='';
    document.getElementById('pkCount').textContent = `${this.pickedSet.size}/${this.targetSet.size}`;
  }
};
