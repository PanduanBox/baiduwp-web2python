# baiduwp-web2python
对接百度网盘解析网站

# 使用说明：
在140行添加建立文件夹的代码
在160行添加下载文件的代码
在315行至320行进行设置

# 设置说明
type_dir：在浏览器中，当你的鼠标悬浮在一个文件夹按钮上时，按钮的链接为"javascript:opendir(xxxx,yyyy,...)"
这里的xxx，yyy就对应着不同的变量，按F12打开监控网络，点击按钮查看post的数据中xxx,yyy对应着什么，把对应的东西按照链接上的顺序填入这里
type_file: 同上，只不过这里要看的是解析文件的按钮
dir_info:用网站随便打开一个分享链接，这里写那些按钮的链接都在哪里，具体请搜索python xpath
file_link_info:打开下载文件的页面，像dir_info一样找到下载链接的所在地
file_inf_info:打开下载文件的页面，像dir_info一样找到文件名称的所在地

# 灵感/基础来源于:https://github.com/yuantuo666/baiduwp-php
