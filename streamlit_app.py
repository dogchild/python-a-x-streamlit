#!/usr/bin/env python3
"""
Python-A-X Streamlit App
提供网络链接的 Python 工具 (Streamlit版)
原作者: dogchild
"""

import os
import asyncio
import json
import base64
import platform
import stat
import re
import threading
import time
import psutil
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import httpx
import aiofiles
import streamlit as st
from fastapi import FastAPI, Response
import uvicorn
from dotenv import load_dotenv

# 加载.env文件配置，优先级：.env文件 > 系统环境变量 > 默认值
load_dotenv(override=True)

# 环境变量配置
FILE_PATH = os.getenv('FILE_PATH', './tmp')  # 运行目录,sub节点文件保存目录
UID = os.getenv('UID', '75de94bb-b5cb-4ad4-b72b-251476b36f3a')  # 用户ID
S_PATH = os.getenv('S_PATH', UID)      # 访问路径
PORT = int(os.getenv('SERVER_PORT', os.getenv('PORT', '3005')))  # HTTP服务端口
A_DOMAIN = os.getenv('A_DOMAIN', '')   # 固定域名，留空即启用临时服务
A_AUTH = os.getenv('A_AUTH', '')       # 固定服务凭证，留空即启用临时服务
A_PORT = int(os.getenv('A_PORT', '8001'))  # 固定服务端口，使用凭证需在管理后台设置和这里一致
CIP = os.getenv('CIP', 'cf.877774.xyz')    # 节点优选域名或优选IP
CPORT = int(os.getenv('CPORT', '443'))     # 节点优选域名或优选IP对应的端口
NAME = os.getenv('NAME', 'Vls')            # 节点名称前缀
MLKEM_S = os.getenv('MLKEM_S', 'mlkem768x25519plus.native.600s.ugygldXvD2pi5St4XBlF4Cgd-55qGCdaOrcJsxdIR5aHGFeYh-Dm1BDsSluXrHUmscV5n9_hPJ8zPfBP4HEgaA')
MLKEM_C = os.getenv('MLKEM_C', 'mlkem768x25519plus.native.0rtt.h7xFrUkiWbhXfCNmehc209OOlXhUaPM-2bgKIQyRRLt7WXmEJFsY64QT8se8HcGNLNkKPlTGS1W5XIgRZfFVuNqATbcyuNa7O9BveTB5GaESadgUsWMCs-ugCyTG3WNonYlL0otGzxMEhnohNnkTnoCchQgVULxZAGZW8oYbaNcS-UUZJGhoSvBbz4gZj8RVqDQhd1ReD1E4IMFd2tANlCANZcyZJKykjPdCrqRxiDsxSHGwB6kB4UikaOEAzCSgXNZcJleylvJVkkg54sh4pnGfC0pXp2GjiZFe_cIFRGJJr4mlaCSHphsvecYzctZQiYw3p4xxxRsCtgpUQ2KWReg6YmZCBDy-ckYg8pNp5LtcZBRWE9nDZKVnbpOqL0s442XLqniTLuI1exkbjMJEz-vLIZSNXDA6DieyFyKOUPtFbjcutoq9QGxICAgmvpGn0Qw_JBVoBsJZqwG43wiBcedwBJotJ_SV7klDZEiF-Nud3OaNcmnJWDcEf3O2BiNknpcKbHmrstg8Y0y5kjtfMrau9NDNoiVidNtKtYwQXHA8ndVo15YutaGKs-N9YCavxYUX62fAunulLJAuc6KsDXs_rDlhrFMfxhumq6kNpZxC0vJsvVSQRcVmd-pi8gseXAUOY_zD2paGv2JEQilTtqlrh9cCn-GCP_cYErud-QSsRyCIz5dpGZdEggrPumAlQ4C5j4JniKYaELScBWQWK6E1Y1SPhQFsLgxJFSC9w0pNmIyfleSEEXcd9uOPdVvF0QpJ04dHHKO4r6ekTkkM4XZc7lp1pTwvB8B-tqmjl9Fu4kcgZ0PCQDqGLeq9U3kJUhBsxLhCH8zNzjtaeGooPZAdw_eCJ8dsQmXByaiAs4ofocko4HEfiWh1urqO5dxJMuS3f7WPs6BWthW5vXCuA3mJ_Go87GUY0XEilpE3OJvNNLiBoidadIFnOFI_fqfGGNhxseEGjdF1cLlEtpdLQjWxxcB1BNudQAdWc6tO1StI0KVQwQeFOYS7v3LK2usU1qQmH6UIbmiN5TtmVxodk8FM3xE6fvZZXON1POM_08KPU8QcoYATmUu_sRaWGrlFmTY59zZNoASc7zPHxJm66ZYOiVFcsSh-pmenuzCCa9UcvUSR-OxLNvi9XoZrWOy6n8iP26gnUmcygTQB0phUajxa6fa_85JF6adgD8ylDXiuGpbOchwokbwGbTUMGwmsBSnKDWKqRffDUPq-pZxQOXuwlblsEWUU87DJFHwI2eVKj9sjYVBzm7onKZpt9yRwCEUajIIggzwDRDQwlPil5MS1vWFd4TsIO4oLtbKrR3YK3Xp-kIeZBUMJBliBJfld0vDJNFMnWKXAE_gPySFO9blD8lGgsHKSSYCgF1VUx6B0nsS1nIPMIFvKB6CwKbeHh0gpR9YepBFm99ZAkRRH2Gu0Xtd59fWoOHRFDYVTWtWTA8gY0oxzE4gcFyePjxw0-7Ax2-gg_fnJZia1fwEAZmZnIAg28OAlRutOPVfLFDBIplSb2NCnsfh6tDcruSt6bZhPlwwDS8pggEKdudxNBkNPYeICnErthTVl5qYB_gQ')
M_AUTH = os.getenv('M_AUTH', 'ML-KEM-768, Post-Quantum')

# --- Global State ---

current_domain: Optional[str] = None
current_links_content: Optional[str] = None
running_processes = []

# --- Service Helper Functions ---

def create_directory():
    if not Path(FILE_PATH).exists():
        Path(FILE_PATH).mkdir(parents=True, exist_ok=True)
        print(f"{FILE_PATH} is created", flush=True)

def cleanup_old_files():
    for file in ['sub.txt', 'boot.log']:
        try:
            (Path(FILE_PATH) / file).unlink(missing_ok=True)
        except:
            pass

async def generate_front_config():
    p_v = base64.b64decode('dmxlc3M=').decode('utf-8')
    config = {
        "log": {"access": "/dev/null", "error": "/dev/null", "loglevel": "none"},
        "inbounds": [
            {"port": A_PORT, "protocol": p_v, "settings": {"clients": [{"id": UID, "flow": base64.b64decode('eHRscy1ycHJ4LXZpc2lvbg==').decode('utf-8')}], "decryption": "none", "fallbacks": [{"dest": 3001}, {"path": "/vla", "dest": 3002}]}, "streamSettings": {"network": "tcp"}},
            {"port": 3001, "listen": "127.0.0.1", "protocol": p_v, "settings": {"clients": [{"id": UID}], "decryption": "none"}, "streamSettings": {"network": "tcp", "security": "none"}},
            {"port": 3002, "listen": "127.0.0.1", "protocol": p_v, "settings": {"clients": [{"id": UID}], "decryption": MLKEM_S, "selectedAuth": M_AUTH}, "streamSettings": {"network": "ws", "security": "none", "wsSettings": {"path": "/vla"}}, "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"], "metadataOnly": False}}
        ],
        "dns": {"servers": ["https+local://8.8.8.8/dns-query"]},
        "outbounds": [{"protocol": base64.b64decode('ZnJlZWRvbQ==').decode('utf-8'), "tag": "direct"}, {"protocol": base64.b64decode('YmxhY2tob2xl').decode('utf-8'), "tag": "block"}]
    }
    async with aiofiles.open(Path(FILE_PATH) / 'config.json', 'w') as f:
        await f.write(json.dumps(config, indent=2))

def get_system_architecture():
    arch = platform.machine().lower()
    return 'arm' if arch in ['arm', 'arm64', 'aarch64'] else 'amd'

def get_files_for_architecture(architecture):
    if architecture == 'arm':
        return [{"fileName": "front", "fileUrl": "https://arm.dogchild.eu.org/front"}, {"fileName": "backend", "fileUrl": "https://arm.dogchild.eu.org/backend"}]
    else:
        return [{"fileName": "front", "fileUrl": "https://amd.dogchild.eu.org/front"}, {"fileName": "backend", "fileUrl": "https://amd.dogchild.eu.org/backend"}]

async def download_file(file_name, file_url):
    file_path = Path(FILE_PATH) / file_name
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with aiofiles.open(file_path, 'wb') as f:
                async with client.stream('GET', file_url) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        if chunk:
                            await f.write(chunk)
            print(f"成功下载 {file_name}", flush=True)
            return True
    except Exception as e:
        print(f"Download {file_name} failed: {e}", flush=True)
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        return False

async def download_files_and_run():
    architecture = get_system_architecture()
    all_files = get_files_for_architecture(architecture)
    if not all_files:
        return False
    
    files_to_download = [f for f in all_files if not (Path(FILE_PATH) / f["fileName"]).exists()]
    if files_to_download:
        results = await asyncio.gather(*[download_file(f["fileName"], f["fileUrl"]) for f in files_to_download])
        if not all(results):
            return False
            
    for file_name in ['front', 'backend']:
        file_path = Path(FILE_PATH) / file_name
        if file_path.exists():
            try:
                file_path.chmod(stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            except:
                pass
    return True

async def start_front():
    front_path = Path(FILE_PATH) / 'front'
    config_path = Path(FILE_PATH) / 'config.json'
    try:
        process = await asyncio.create_subprocess_exec(
            str(front_path), '-c', str(config_path),
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        running_processes.append(process)
        return process
    except Exception as e:
        print(f"front running error: {e}", flush=True)
        return None

async def start_backend():
    backend_path = Path(FILE_PATH) / 'backend'
    if not backend_path.exists():
        return None
    
    c_t = base64.b64decode('dHVubmVs').decode('utf-8')
    if A_AUTH and A_DOMAIN and re.match(r'^[A-Z0-9a-z=]{120,250}$', A_AUTH):
        args = [c_t, '--edge-ip-version', 'auto', '--no-autoupdate', '--protocol', 'http2', 'run', '--token', A_AUTH]
    else:
        args = [c_t, '--edge-ip-version', 'auto', '--no-autoupdate', '--protocol', 'http2', '--logfile', str(Path(FILE_PATH) / 'boot.log'), '--loglevel', 'info', '--url', f'http://localhost:{A_PORT}']
    
    try:
        process = await asyncio.create_subprocess_exec(str(backend_path), *args, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        running_processes.append(process)
        return process
    except Exception as e:
        print(f"Error executing backend: {e}", flush=True)
        return None

async def extract_domains():
    global current_domain
    if A_AUTH and A_DOMAIN:
        current_domain = A_DOMAIN
        return current_domain
    
    boot_log_path = Path(FILE_PATH) / 'boot.log'
    tcf_domain = base64.b64decode('dHJ5Y2xvdWRmbGFyZS5jb20=').decode('utf-8')
    for _ in range(15):
        try:
            if boot_log_path.exists():
                async with aiofiles.open(boot_log_path, 'r') as f:
                    content = await f.read()
                matches = re.findall(rf'https?://([^\]*{tcf_domain})/?', content)
                if matches:
                    current_domain = matches[0]
                    return current_domain
        except:
            pass
        await asyncio.sleep(2)
    return None

async def get_isp_info():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get('https://ipapi.co/json/')
            data = response.json()
            return f"{data.get('country_code', 'Unknown')}-{data.get('org', 'ISP')}".replace(' ', '_')
    except:
        return 'Unknown-ISP'

async def generate_links(a_domain):
    global current_links_content
    try:
        isp = await get_isp_info()
        p_v = base64.b64decode('dmxlc3M=').decode('utf-8')
        v_link = f"{p_v}://{UID}@{CIP}:{CPORT}?encryption={MLKEM_C}&security=tls&sni={a_domain}&fp=chrome&type=ws&host={a_domain}&path=%2Fvla%3Fed%3D2560#{NAME}-{isp}"
        sub_content = f"{v_link}\n"
        current_links_content = base64.b64encode(sub_content.encode()).decode()
        async with aiofiles.open(Path(FILE_PATH) / 'sub.txt', 'w') as f:
            await f.write(current_links_content)
        
        print(f"{Path(FILE_PATH) / 'sub.txt'} saved successfully", flush=True)
        print(current_links_content, flush=True)
        return current_links_content
    except Exception as e:
        print(f"Link generation failed: {e}")
        return None

async def cleanup_processes():
    for process in running_processes:
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except:
            try:
                process.kill()
                await process.wait()
            except:
                pass
    running_processes.clear()

async def setup_services():
    """
    Application main setup logic.
    """
    create_directory()
    cleanup_old_files()
    await generate_front_config()
    
    if not await download_files_and_run():
        print("Failed to download required files", flush=True)
        return
    
    front_process = await start_front()
    if not front_process:
        print("Failed to start front", flush=True)
        return
    
    backend_process = await start_backend()
    if not backend_process:
        print("Failed to start backend", flush=True)
        return
    
    await asyncio.sleep(5)
    domain = await extract_domains()
    if not domain:
        print("Failed to extract domain", flush=True)
        return
    
    await generate_links(domain)
    
    print(f"\nService setup complete!", flush=True)
    print(f"Port: {PORT}", flush=True)
    print(f"Access URL: http://localhost:{PORT}/{S_PATH}", flush=True)
    print(f"Service Domain: {domain}", flush=True)
    print("=" * 60, flush=True)

# --- FastAPI Setup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Starting setup in background...", flush=True)
    asyncio.create_task(setup_services())
    yield
    print("Application shutdown: Cleaning up processes...", flush=True)
    await cleanup_processes()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return "Hello world! python-a-x is running."

@app.get(f"/{S_PATH}")
async def get_links():
    content = current_links_content
    if not content:
         sub_path = Path(FILE_PATH) / 'sub.txt'
         if sub_path.exists():
             try:
                 async with aiofiles.open(sub_path, 'r') as f:
                     content = await f.read()
             except:
                 pass
    return Response(content=content or "Links not ready", media_type="text/plain")

# --- Streamlit & Threading Logic ---

def run_fastapi():
    """Run FastAPI in a separate thread"""
    uvicorn.run(app, host="0.0.0.0", port=PORT)

@st.cache_resource
def start_background_services():
    """
    Start FastAPI server (which triggers setup services via lifespan).
    """
    # Start FastAPI thread
    t = threading.Thread(target=run_fastapi, daemon=True)
    t.start()
    return t

def get_process_status(process_name):
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if process_name in proc.name() or (proc.cmdline() and any(process_name in cmd for cmd in proc.cmdline())):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# --- UI Layout ---

st.set_page_config(page_title="Python-A-X Monitor", page_icon="⚡", layout="wide")

# Start services (safe to call multiple times due to @st.cache_resource)
start_background_services()

st.title("⚡ Python-A-X Streamlit Monitor")
st.markdown("---")

# Metrics Container
metrics_placeholder = st.empty()
info_placeholder = st.empty()

# Refresh loop
while True:
    try:
        # System Metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        mem_info = psutil.virtual_memory()
        net_io = psutil.net_io_counters()
        
        with metrics_placeholder.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="CPU Usage", value=f"{cpu_percent}%")
            with col2:
                st.metric(label="Memory Usage", value=f"{mem_info.percent}%", delta=f"{mem_info.used / (1024**3):.2f} GB / {mem_info.total / (1024**3):.2f} GB")
            with col3:
                st.metric(label="Network Sent/Recv", value=f"{net_io.bytes_sent / (1024**2):.1f} MB / {net_io.bytes_recv / (1024**2):.1f} MB")
        
        # Status
        with info_placeholder.container():
            st.subheader("System Status")
            sub_file = Path(FILE_PATH) / 'sub.txt'
            c1, c2 = st.columns(2)
            c1.success("Backend Service Running") if get_process_status("backend") else c1.warning("Backend Service Starting/Stopped")
            c2.success("Front Service Running") if get_process_status("front") else c2.warning("Front Service Starting/Stopped")

            if sub_file.exists():
                st.markdown("### 🔗 Subscription Link")
                try:
                    with open(sub_file, 'r') as f:
                        content = f.read()
                    st.code(f"http://localhost:{PORT}/{S_PATH}", language="text")
                    st.text_area("Base64 Subscription Content", content, height=100)
                except:
                    st.error("Error reading subscription file")
            else:
                st.info("Waiting for services to initialize... (This may take 10-20 seconds)")
    
    except Exception as e:
        # Catch UI errors to prevent crash
        st.error(f"UI Error: {e}")
        
    time.sleep(2)

