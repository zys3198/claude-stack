// wrapper: 直连抓取(微信 UA + 重定向 + UTF-8) + extractor 的 extract(html) 解析
// 绕过 extractor 自带的 request-promise 抓取(微信会挡),复用它成熟的解析逻辑
const fs = require('fs');
const https = require('https');
const http = require('http');
const { extract } = require('./extract');

function fetchHtml(url) {
  const UA = 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 MMWEBID/1234 MicroMessenger/8.0.37.2480(0x28002573)';
  const headers = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
  };
  return new Promise((resolve, reject) => {
    const get = (target, hops) => {
      const lib = target.startsWith('https') ? https : http;
      lib.get(target, { headers }, (res) => {
        if ([301,302,303,307,308].includes(res.statusCode) && hops < 5 && res.headers.location) {
          res.resume();
          return get(res.headers.location, hops + 1);
        }
        if (res.statusCode !== 200) { reject(new Error('HTTP ' + res.statusCode)); return; }
        const chunks = [];
        res.on('data', (c) => chunks.push(c));
        res.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
      }).on('error', reject);
    };
    get(url, 0);
  });
}

function toMarkdown(d) {
  // extractor 返回的 data 字段见 extract.js;取核心字段拼笔记骨架
  const lines = [];
  lines.push('# ' + (d.msg_title || '(无标题)'));
  lines.push('');
  // 公众号名与文章作者可能相同,去重避免 "Datawhale / Datawhale"
  const who = [...new Set([d.account_name, d.msg_author].filter(Boolean))].join(' / ');
  lines.push('> ' + (who || '未知公众号') + (d.msg_publish_time_str ? ' | ' + d.msg_publish_time_str : ''));
  lines.push('');
  if (d.msg_desc) { lines.push('## 摘要'); lines.push(''); lines.push(d.msg_desc); lines.push(''); }
  lines.push('## 正文');
  lines.push('');
  // msg_content 是 HTML,转成粗略 markdown(段落/图片)
  if (d.msg_content) {
    let html = d.msg_content;
    html = html.replace(/<img[^>]*(?:data-src|src)=['"]([^'"]+)['"][^>]*>/gi, '\n\n![图片]($1)\n');
    html = html.replace(/<br\s*\/?>(?=\s*<)/gi, '\n');
    html = html.replace(/<\/(p|section|div|h[1-6])>/gi, '\n');
    html = html.replace(/<[^>]+>/g, '');
    html = html.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
    html = html.replace(/\n{3,}/g, '\n\n').replace(/[ \t]+\n/g, '\n');
    lines.push(html.trim());
  } else {
    lines.push('(_正文为空_)');
  }
  lines.push('');
  // 附:extractor 提取的额外元信息(迁移/版权/类型/内嵌链接)
  const meta = [];
  if (d.msg_type) meta.push('类型: ' + d.msg_type);
  if (d.msg_has_copyright) meta.push('原创');
  if (d.account_biz) meta.push('biz: ' + d.account_biz);
  if (d.msg_sn) meta.push('sn: ' + d.msg_sn);
  if (Array.isArray(d.mp_links) && d.mp_links.length) meta.push('内嵌公众号链接: ' + d.mp_links.length + ' 条');
  if (Array.isArray(d.tags) && d.tags.length) meta.push('标签: ' + d.tags.join(', '));
  if (meta.length) { lines.push('## 提取元信息'); lines.push(''); meta.forEach((m) => lines.push('- ' + m)); lines.push(''); }
  return lines.join('\n');
}

(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  if (!url || !out) { console.error('usage: node run.js <mp-url> <out.md>'); process.exit(1); }
  let html;
  try { html = await fetchHtml(url); }
  catch (e) { console.error('抓取失败: ' + e.message); process.exit(2); }
  // 传 HTML + url,绕过 extract 内部的 request-promise 抓取
  const result = await extract(html, { url });
  if (!result.done) { console.error('解析失败 code ' + result.code + ': ' + result.msg); process.exit(3); }
  const d = result.data;
  const body = toMarkdown(d);
  const fm = [
    '---',
    // msg_publish_time_str 形如 "2026/06/24 22:08:13",frontmatter 要求 YYYY-MM-DD(连字符)
    'date: ' + (d.msg_publish_time_str ? d.msg_publish_time_str.split(' ')[0].replace(/\//g, '-') : new Date().toISOString().slice(0, 10)),
    'source: ' + url,
    'author: ' + (d.account_name || d.msg_author || '未知公众号'),
    'tags: [wechat-article]',
    'status: raw',
    '---',
    ''
  ].join('\n');
  fs.writeFileSync(out, fm + body + '\n', 'utf8');
  console.log('OK title=' + (d.msg_title || '') + ' body=' + body.length + 'chars -> ' + out);
})();
