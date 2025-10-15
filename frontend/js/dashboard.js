const Dashboard = {
  async exportLogs(){
    const r = await apiFetch('/export/scan_logs');
    if(!r.ok){ alert('导出失败'); return; }
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'scan_logs.csv'; a.click();
    URL.revokeObjectURL(url);
  }
};
