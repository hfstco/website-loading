import copy
import io
import json
import sys
import time
from urllib.parse import urlparse

from selenium import webdriver
from pexpect import pxssh

server_config = {
    "hostname": "faui7s3.informatik.uni-erlangen.de",
    "port": "22",
    "username": "mhof"
}

def start_picoquic(server: pxssh):
    server.sendline('cd ~/website-loading/picoquic')
    server.prompt()
    server.sendline('sudo ./picoquicdemo -p 50043 -1 -q ./qlogs -w ../www -k /etc/letsencrypt/live/h3.hfst.dev/privkey.pem -c /etc/letsencrypt/live/h3.hfst.dev/cert.pem')
    server.expect('Waiting for packets.')

def stop_picoquic(server: pxssh):
    server.sendcontrol('c')
    server.prompt()

def copy_qlogs():
    pass

def start_nginx(server: pxssh):
    server.sendline('cd ~/website-loading/nginx')
    server.prompt()
    server.sendline('sudo nginx -c nginx.conf -p $PWD')

def stop_nginx(server: pxssh):
    server.sendcontrol('c')
    server.prompt()

def run_chrome(url: str, use_quic: bool):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-gpu')
    if use_quic:
        options.add_argument("--enable-quic")
        options.add_argument(f"--origin-to-force-quic-on={urlparse(url).hostname}:{urlparse(url).port}")
    else:
        options.add_argument("--disable-quic")

    driver = webdriver.Chrome(options=options)
    driver.delete_all_cookies()
    # disable cache
    # https://stackoverflow.com/questions/66956625/disable-cache-on-network-tab-using-python-seleniumautomation
    # https://chromedevtools.github.io/devtools-protocol/tot/Network/#method-setCacheDisabled
    driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})

    try:
        driver.get(url)

        perf_timing = driver.execute_script("return window.performance.timing")
    except Exception as e:
        driver.quit()
        raise RuntimeError(f"Chrome error: {e}")

    driver.close()

    return perf_timing

def main():
    h3_perf_timings = []
    h2_perf_timings = []

    server = pxssh.pxssh(logfile=sys.stdout, encoding='utf-8')
    server.login(server_config["hostname"], server_config["username"], server_config["port"])

    for i in range(10):
        for t in ["h2", "h3"]:
            if t == "h2":
                start_nginx(server)

                perf_timing = run_chrome("https://h2.hfst.dev:50044", False)

                stop_nginx(server)

                h2_perf_timings.append(perf_timing)
            elif t == "h3":
                start_picoquic(server)

                perf_timing = run_chrome("https://h3.hfst.dev:50043", True)

                h3_perf_timings.append(perf_timing)

    with open('h2_perf_timings.json', 'w') as file:
        json.dump(h2_perf_timings, file)
    with open('h3_perf_timings.json', 'w') as file:
        json.dump(h3_perf_timings, file)

    server.close()

if __name__ == "__main__":
    main()