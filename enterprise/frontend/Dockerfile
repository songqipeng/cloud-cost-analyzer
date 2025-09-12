FROM nginx:alpine

# 创建前端页面目录
RUN mkdir -p /usr/share/nginx/html

# 复制所有HTML文件
COPY *.html /usr/share/nginx/html/

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]