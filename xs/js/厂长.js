var rule = {
    title: '厂长1080',
    host: 'https://www.czzyvideo.com/',
    url: '/fyclass/page/fypage',
    searchUrl: '/daoyongjiek0shibushiyoubing?q=**&f=_all&p=fypage',
    searchable: 2, //是否启用全局搜索,
    quickSearch: 0, //是否启用快速搜索,
    filterable: 0, //是否启用分类筛选,
    headers: {
        'User-Agent': 'MOBILE_UA', // "Cookie":"searchneed=ok"
    },
    编码: 'utf-8',
    timeout: 5000,
    class_name: '豆瓣电影Top250&最新电影&剧场版&国产剧&美剧&韩剧&番剧',
    class_url: 'dbtop250&zuixindianying&dongmanjuchangban&gcj&meijutt&hanjutv&fanju',
    tab_exclude: '*',
    tab_rename: {
        '在线播放': '兵哥出品'
    },
    play_parse: true,
    lazy: `js:
            if(/\\.(m3u8|mp4)/.test(input)){
                input = {parse:0,url:input}
            }else{
                if(rule.parse_url.startsWith('json:')){
                    let purl = rule.parse_url.replace('json:','')+input;
                    let html = request(purl);
                    input = {parse:0,url:JSON.parse(html).url}
                }else{
                    input= rule.parse_url+input; 
                }
            `,
    limit: 6,
    double: true,
    推荐: '*',
    一级: '.bt_img.mi_ne_kd&&li;h3&&Text;img&&data-original;span&&Text;a&&href',
    二级: {
        "title": "h3&&Text",
        "img": "img&&src",
        "desc": ".moviedteail_list&&li&&Text",
        "content": ".yp_context&&Text",
        tabs: 'js:TABS = ["在线播放"]',
        "lists": ".paly_list_btn&&a",
    },
    搜索: '.mi_ne_kd.search_list&&li;img&&alt;img&&data-original;.nostag&&Text;a&&href',
}