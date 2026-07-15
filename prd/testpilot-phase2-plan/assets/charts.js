(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var muted2 = style.getPropertyValue('--muted2').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var danger = style.getPropertyValue('--danger').trim();
  var warning = style.getPropertyValue('--warning').trim();

  // ===== Chart 1: Task Priority Distribution =====
  var chart1 = echarts.init(document.getElementById('chart-priority'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['P0 (必须先做)', 'P1 (核心增强)', 'P2 (体验优化)'], bottom: 0, textStyle: { color: muted, fontSize: 12 } },
    grid: { left: '3%', right: '4%', bottom: '12%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['T01 SQLite迁移', 'T02 API联通', 'T03 稳定性引擎', 'T04 登录态注入', 'T05 WebSocket', 'T06 AI评审', 'T07 飞书集成', 'T08 任务队列', 'T09 模型选型', 'T10 系统设置', 'T11 成本监控', 'T12 报告导出'],
      axisLabel: { color: muted, fontSize: 10, rotate: 35, interval: 0 },
      axisLine: { lineStyle: { color: rule } }
    },
    yAxis: {
      type: 'value',
      name: '工时(天)',
      nameTextStyle: { color: muted, fontSize: 11 },
      axisLabel: { color: muted, fontSize: 11 },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    series: [
      { name: 'P0 (必须先做)', type: 'bar', stack: 'total', data: [2, 4, 5, 2, 0, 0, 0, 0, 0, 0, 0, 0], itemStyle: { color: danger }, barWidth: '50%' },
      { name: 'P1 (核心增强)', type: 'bar', stack: 'total', data: [0, 0, 0, 0, 3, 3, 3, 3, 2, 0, 0, 0], itemStyle: { color: warning } },
      { name: 'P2 (体验优化)', type: 'bar', stack: 'total', data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 2], itemStyle: { color: accent2 } },
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // ===== Chart 2: Gantt Chart =====
  var chart2 = echarts.init(document.getElementById('chart-gantt'), null, { renderer: 'svg' });
  var tasks = [
    { name: 'T01 SQLite数据库迁移', start: 0, duration: 2, priority: 'P0' },
    { name: 'T02 前端全量API联通', start: 2, duration: 4, priority: 'P0' },
    { name: 'T03 脚本稳定性检查引擎', start: 2, duration: 5, priority: 'P0' },
    { name: 'T04 登录态storageState注入', start: 4, duration: 2, priority: 'P0' },
    { name: 'T05 WebSocket实时执行进度', start: 9, duration: 3, priority: 'P1' },
    { name: 'T06 AI评审报告页', start: 11, duration: 3, priority: 'P1' },
    { name: 'T07 飞书文档API集成', start: 9, duration: 3, priority: 'P1' },
    { name: 'T08 Redis+RQ任务队列', start: 9, duration: 3, priority: 'P1' },
    { name: 'T09 AI模型动态选型', start: 12, duration: 2, priority: 'P1' },
    { name: 'T10 系统设置页功能实现', start: 17, duration: 3, priority: 'P2' },
    { name: 'T11 成本监控与记录', start: 19, duration: 2, priority: 'P2' },
    { name: 'T12 报告导出PDF/HTML', start: 19, duration: 2, priority: 'P2' },
  ];

  var colorMap = { 'P0': danger, 'P1': warning, 'P2': accent2 };
  var ganttData = tasks.map(function(t, i) {
    return {
      name: t.name,
      value: [i, t.start, t.start + t.duration, t.duration],
      itemStyle: { color: colorMap[t.priority] }
    };
  });

  chart2.setOption({
    animation: false,
    tooltip: {
      trigger: 'item',
      appendToBody: true,
      formatter: function(p) {
        var v = p.value;
        var dayStart = Math.floor(v[1] / 5) + 1;
        var dayEnd = Math.ceil(v[2] / 5);
        return p.name + '<br/>第' + dayStart + '-' + dayEnd + '个工作日 (' + v[3] + '天)';
      }
    },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '5%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '工作日',
      nameTextStyle: { color: muted, fontSize: 11 },
      min: 0,
      max: 25,
      interval: 5,
      axisLabel: {
        color: muted, fontSize: 11,
        formatter: function(val) { return 'Week ' + (Math.floor(val / 5) + 1); }
      },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: tasks.map(function(t) { return t.name; }),
      axisLabel: { color: ink, fontSize: 10 },
      axisLine: { lineStyle: { color: rule } },
      inverse: true,
    },
    series: [{
      type: 'custom',
      renderItem: function(params, api) {
        var cat = api.value(0);
        var start = api.coord([api.value(1), cat]);
        var end = api.coord([api.value(2), cat]);
        var height = api.size([0, 1])[1] * 0.6;
        return {
          type: 'rect',
          shape: { x: start[0], y: start[1] - height / 2, width: end[0] - start[0], height: height, r: 3 },
          style: api.style()
        };
      },
      data: ganttData,
      encode: { x: [1, 2], y: 0 }
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // ===== Chart 3: Architecture Comparison =====
  var chart3 = echarts.init(document.getElementById('chart-arch'), null, { renderer: 'svg' });
  chart3.setOption({
    animation: false,
    tooltip: { appendToBody: true },
    series: [{
      type: 'graph',
      layout: 'none',
      symbolSize: [140, 45],
      symbol: 'roundRect',
      roam: false,
      label: { show: true, color: '#fff', fontSize: 11, fontWeight: 600 },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 8],
      data: [
        // Current (left side)
        { name: '前端 HTML\n(localStorage)', x: 0, y: 0, itemStyle: { color: muted2 }, label: { color: '#fff', fontSize: 10 } },
        { name: 'FastAPI\n(同步)', x: 0, y: 80, itemStyle: { color: accent } },
        { name: 'DeepSeek\n(硬编码)', x: 0, y: 160, itemStyle: { color: warning } },
        { name: 'Playwright\n(进程内)', x: 0, y: 240, itemStyle: { color: muted2 }, label: { color: '#fff', fontSize: 10 } },

        // Divider
        { name: '当前 v1.0', x: 0, y: 310, itemStyle: { color: 'transparent' }, label: { color: muted2, fontSize: 12, fontWeight: 700 } },

        // Target (right side)
        { name: '前端 HTML\n(API驱动)', x: 300, y: 0, itemStyle: { color: accent } },
        { name: 'FastAPI\n(异步)', x: 300, y: 80, itemStyle: { color: accent } },
        { name: 'Redis\n(队列)', x: 200, y: 160, itemStyle: { color: danger } },
        { name: 'RQ Worker\n(异步执行)', x: 300, y: 160, itemStyle: { color: accent2 } },
        { name: '多模型\n(动态选型)', x: 400, y: 160, itemStyle: { color: warning } },
        { name: 'Playwright\n(独立进程)', x: 300, y: 240, itemStyle: { color: accent2 } },
        { name: 'SQLite\n(零配置)', x: 100, y: 80, itemStyle: { color: accent } },
        { name: '飞书API\n(文档拉取)', x: 500, y: 80, itemStyle: { color: accent } },

        { name: 'Phase 2 v1.1', x: 300, y: 310, itemStyle: { color: 'transparent' }, label: { color: accent, fontSize: 12, fontWeight: 700 } },
      ],
      links: [
        // Current
        { source: '前端 HTML\n(localStorage)', target: 'FastAPI\n(同步)', lineStyle: { color: muted2, width: 1.5 } },
        { source: 'FastAPI\n(同步)', target: 'DeepSeek\n(硬编码)', lineStyle: { color: muted2, width: 1.5 } },
        { source: 'FastAPI\n(同步)', target: 'Playwright\n(进程内)', lineStyle: { color: muted2, width: 1.5 } },

        // Target
        { source: '前端 HTML\n(API驱动)', target: 'FastAPI\n(异步)', lineStyle: { color: accent, width: 2 } },
        { source: 'FastAPI\n(异步)', target: 'Redis\n(队列)', lineStyle: { color: accent, width: 2 } },
        { source: 'FastAPI\n(异步)', target: '多模型\n(动态选型)', lineStyle: { color: accent, width: 2 } },
        { source: 'FastAPI\n(异步)', target: 'SQLite\n(零配置)', lineStyle: { color: accent, width: 2 } },
        { source: 'FastAPI\n(异步)', target: '飞书API\n(文档拉取)', lineStyle: { color: accent, width: 2 } },
        { source: 'Redis\n(队列)', target: 'RQ Worker\n(异步执行)', lineStyle: { color: danger, width: 2 } },
        { source: 'RQ Worker\n(异步执行)', target: 'Playwright\n(独立进程)', lineStyle: { color: accent2, width: 2 } },
        // Worker 结果回传 FastAPI（不直接写 SQLite）
        { source: 'RQ Worker\n(异步执行)', target: 'FastAPI\n(异步)', lineStyle: { color: accent2, width: 1.5, type: 'dashed', curveness: 0.3 } },
      ],
      lineStyle: { opacity: 0.7 }
    }]
  });
  window.addEventListener('resize', function() { chart3.resize(); });

})();
