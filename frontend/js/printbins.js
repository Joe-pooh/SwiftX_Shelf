const PrintBins = {
  async render(){
    const area = document.getElementById('print-area'); area.innerHTML = '';
    const lines = document.getElementById('binsInput').value.split('\n').map(s=>s.trim()).filter(Boolean);
    for(const code of lines){
      const div = document.createElement('div'); div.className='card';
      const title = document.createElement('div'); title.style.fontWeight='700'; title.style.marginBottom='8px'; title.textContent = code;
      const img = document.createElement('img'); img.width = 256; img.height = 256;
      const url = new URL(App.BACKEND_BASE.replace(/\/$/,'') + '/qr.png');
      url.searchParams.set('text', code); url.searchParams.set('size', '256');
      img.src = url.toString();
      div.appendChild(title); div.appendChild(img); document.getElementById('print-area').appendChild(div);
    }
  }
};
