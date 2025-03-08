# 使用官方的Python镜像作为基础镜像
FROM python:3.9-slim

# 创建并设置国内镜像源
RUN mkdir -p /etc/apt \
    && echo "deb http://mirrors.ustc.edu.cn/debian/ bullseye main contrib non-free" > /etc/apt/sources.list \
    && echo "deb http://mirrors.ustc.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.ustc.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list

# 安装必要的依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 安装Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装固定版本的ChromeDriver
RUN wget -q -O chromedriver_linux64.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

WORKDIR /app

# 使用国内PyPI镜像
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 5002

# 修改app.py中的Chrome初始化部分
RUN sed -i 's/driver = webdriver.Chrome(options=chrome_options)/driver = webdriver.Chrome(options=chrome_options, service_args=["--verbose", "--log-path=\/tmp\/chromedriver.log"])/' app.py

CMD ["python", "app.py"]
