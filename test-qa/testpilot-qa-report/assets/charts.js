(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var passColor = style.getPropertyValue('--pass').trim();
  var failColor = style.getPropertyValue('--fail').trim();
  var warnColor = style.getPropertyValue('--warn').trim();

  var chart = echarts.init(document.getElementById('chart-bugs'), null, { renderer: 'svg' });
  chart.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['P0严重', 'P1高', 'P2中', 'P3低'], textStyle: { color: muted }, top: 5 },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['Dashboard', '项目管理', '需求管理', 'AI分析/生成', '稳定性保障', 'AI评审', '用例库', '执行中心', '报告中心', '前端UI'],
      axisLabel: { color: muted, fontSize: 11, rotate: 30 },
      axisLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: muted },
      splitLine: { lineStyle: { color: rule } }
    },
    series: [
      { name: 'P0严重', type: 'bar', stack: 'total', itemStyle: { color: failColor }, data: [2, 0, 0, 0, 0, 0, 0, 0, 0, 1] },
      { name: 'P1高', type: 'bar', stack: 'total', itemStyle: { color: warnColor }, data: [1, 1, 0, 1, 0, 0, 0, 0, 1, 0] },
      { name: 'P2中', type: 'bar', stack: 'total', itemStyle: { color: accent }, data: [0, 1, 2, 1, 1, 2, 2, 1, 1, 0] },
      { name: 'P3低', type: 'bar', stack: 'total', itemStyle: { color: muted }, data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 1] }
    ]
  });
  window.addEventListener('resize', function() { chart.resize(); });
})();
