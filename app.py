from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from datetime import datetime

app = Flask(__name__)

def get_cursor_usage(email, password):
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 创建Service对象并设置service_args
    service = Service(
        executable_path="/usr/local/bin/chromedriver",
        log_path="/tmp/chromedriver.log",
        service_args=["--verbose"]
    )
    
    # 使用Service对象初始化WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 访问登录页面
        driver.get("https://www.cursor.com/settings")
        time.sleep(2)  # 等待页面加载
        
        # 找到登录按钮并点击
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in')]"))
        )
        login_button.click()
        
        # 等待登录表单加载
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        )
        
        # 输入邮箱和密码
        email_input.send_keys(email)
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys(password)
        
        # 提交登录表单
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # 等待设置页面加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Usage')]"))
        )
        
        # 提取使用额度信息
        usage_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Usage')]/following-sibling::div")
        usage_text = usage_element.text
        
        # 提取到期日期
        expiry_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Next billing date')]/following-sibling::div")
        expiry_date = expiry_element.text
        
        # 解析数据
        total_usage_match = re.search(r"(\d+)/(\d+)", usage_text)
        used = int(total_usage_match.group(1)) if total_usage_match else 0
        total = int(total_usage_match.group(2)) if total_usage_match else 0
        remaining = total - used
        
        # 计算到期前的天数
        expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
        today = datetime.now()
        days_left = (expiry_date_obj - today).days
        
        # 计算每日平均剩余额度
        daily_average = remaining / max(days_left, 1) if days_left > 0 else 0
        
        return {
            "total_quota": total,
            "used_quota": used,
            "remaining_quota": remaining,
            "expiry_date": expiry_date,
            "days_until_expiry": days_left,
            "daily_average_remaining": round(daily_average, 2)
        }
        
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        result = get_cursor_usage(email, password)
    
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True) 