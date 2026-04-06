import time, os, requests
from playwright.sync_api import sync_playwright
from undetected_playwright import Tarnished
from urllib.parse import urlparse

url = os.environ.get("URL")
config = os.environ.get("CONFIG")
sendkey = os.environ.get("SENDKEY")

login_url = "{}/auth/login".format(url)


def send_notification(content):
    print(content)
    if sendkey:
        push_url = "https://sctapi.ftqq.com/{}.send?title=机场签到&desp={}".format(
            sendkey, content
        )
        try:
            requests.post(url=push_url)
        except Exception as e:
            print(f"推送失败: {e}")


def checkin(index, user_account, user_password):
    print(f"\n--- 正在处理第 {index} 个账号: {user_account} ---")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        Tarnished.apply_stealth(context)
        page = context.new_page()

        try:
            # 1. 登录逻辑
            print("正在打开登录页面...")
            page.goto(login_url)
            page.fill('input[name="email"]', user_account)
            page.fill('input[name="password"]', user_password)

            # 处理极验 (若有)
            try:
                captcha_btn = page.wait_for_selector(".geetest_btn_click", timeout=3000)
                if captcha_btn:
                    print("检测到验证按钮，点击中...")
                    captcha_btn.click()
                    time.sleep(3)  # 等待手动/自动通过验证的时间
            except:
                pass

            # 点击登录
            login_btn = page.wait_for_selector(
                'button[type="submit"].login', timeout=5000
            )
            with page.expect_navigation():
                login_btn.click()

            # 2. 签到逻辑
            if "/user" in page.url or "/dashboard" in page.url:
                print("✅ 登录成功，准备签到...")

                # 检查是否已签到（通过文本判断）
                checkin_btn = page.query_selector("#checkin-div a")
                if checkin_btn:
                    btn_text = checkin_btn.inner_text().strip()
                    if "已签到" in btn_text or "明日再来" in btn_text:
                        send_notification(f"ℹ️ 今日已经签到过了。当前状态：{btn_text}")
                    else:
                        print(f"还没签到，准备发送签到指令。当前状态：{btn_text}")
                        # 直接执行 JS 签到，无视弹窗遮挡
                        page.evaluate("checkin()")
                        print("🚀 签到指令已发送")

                        time.sleep(2)
                        msg = page.query_selector(
                            ".swal2-html-container, .swal2-content"
                        )
                        if msg:
                            send_notification(
                                f"🎁 签到结果: {msg.inner_text().strip()}"
                            )
                else:
                    send_notification(
                        "❌ 错误：未能定位到 ID 为 checkin-div 内部的 a 标签"
                    )

            else:
                current_url = page.url
                parsed = urlparse(current_url)
                path = parsed.path
                send_notification(f"❌ 登录失败，停留页面路径: {path}")

        except Exception as e:
            send_notification(f"❗ 运行出错: {str(e)}")

        finally:
            browser.close()


if __name__ == "__main__":
    if not config:
        send_notification("错误: CONFIG仓库密钥为空，请在action中创建CONFIG仓库密钥")
        exit()

    # 读取参数：过滤空行并去除首尾空格
    configs = [line.strip() for line in config.splitlines() if line.strip()]

    if len(configs) % 2 != 0:
        send_notification("⚠️ CONFIG参数格式不正确（行数应为偶数：一行账号，一行密码）")
        exit()

    user_quantity = len(configs) // 2

    for i in range(user_quantity):
        user = configs[i * 2]
        pwd = configs[i * 2 + 1]
        checkin(i + 1, user, pwd)
        # 账号间增加小量延迟防止并发/IP被封
        time.sleep(2)
