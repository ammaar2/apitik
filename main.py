import requests
import random
import uuid
import os
import time
import secrets
import binascii
from MedoSigner import Argus, Gorgon, md5, Ladon
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode

app = FastAPI()

# إضافة CORS للسماح بطلبات من أي مصدر خارجي
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكنك تخصيص هذه القيمة بالمصادر التي تحتاجها فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# دالة لتوقيع البيانات المطلوبة
def sign(params, payload: str = None, sec_device_id: str = "", cookie: str = None, aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = "2.3.1.i18n", sdk_version: int = 2, platform: int = 19, unix: int = None):
    x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload else None
    if not unix:
        unix = int(time.time())
    return Gorgon(params, unix, payload, cookie).get_value() | {
        "x-ladon": Ladon.encrypt(unix, license_id, aid),
        "x-argus": Argus.get_sign(
            params, x_ss_stub, unix, platform=platform, aid=aid, license_id=license_id,
            sec_device_id=sec_device_id, sdk_version=sdk_version_str, sdk_version_int=sdk_version
        )
    }

# دالة لتدقيق البريد الإلكتروني
@app.get("/Check-Email-Tik/")
async def process_email(email: str, ses: str):
    try:
        session = requests.Session()

        # إعداد الكوكيز بشكل آمن
        secret = secrets.token_hex(16)
        cookies = {
            "passport_csrf_token": secret,
            "passport_csrf_token_default": secret,
            "sessionid": ses
        }
        session.cookies.update(cookies)

        # إعدادات العشوائية لأجهزة مختلفة
        device_brands = ["samsung", "huawei", "xiaomi", "apple", "oneplus"]
        device_types = ["SM-S928B", "P40", "Mi 11", "iPhone12,1", "OnePlus9"]
        regions = ["AE", "IQ", "US", "FR", "DE"]
        languages = ["ar", "en", "fr", "de"]

        # إعداد المعاملات المطلوبة
        params = {
            'passport-sdk-version': "6031490",
            'device_platform': "android",
            'os': "android",
            'ssmix': "a",
            '_rticket': str(round(random.uniform(1.2, 1.6) * 100000000)) + "4632",
            'cdid': str(uuid.uuid4()),
            'channel': "googleplay",
            'aid': "1233",
            'app_name': "musical_ly",
            'version_code': "370104",
            'version_name': "37.1.4",
            'manifest_version_code': "2023701040",
            'update_version_code': "2023701040",
            'ab_version': "37.1.4",
            'resolution': "720*1448",
            'dpi': str(random.choice([420, 480, 532])),
            'device_type': random.choice(device_types),
            'device_brand': random.choice(device_brands),
            'language': random.choice(languages),
            'os_api': str(random.randint(28, 34)),
            'os_version': str(random.randint(10, 14)),
            'ac': "wifi",
            'is_pad': "0",
            'current_region': random.choice(regions),
            'app_type': "normal",
            'sys_region': random.choice(regions),
            'last_install_time': str(random.randint(1600000000, 1700000000)),
            'mcc_mnc': "41840",
            'timezone_name': "Asia/Baghdad",
            'carrier_region_v2': "418",
            'residence': random.choice(regions),
            'app_language': random.choice(languages),
            'carrier_region': random.choice(regions),
            'timezone_offset': str(random.randint(0, 14400)),
            'host_abi': "arm64-v8a",
            'locale': random.choice(languages),
            'ac2': "wifi",
            'uoo': "0",
            'op_region': random.choice(regions),
            'build_number': "37.1.4",
            'region': random.choice(regions),
            'ts': str(int(time.time())),
            'iid': str(random.randint(1, 10**19)),
            'device_id': str(random.randint(1, 10**19)),
            'openudid': str(binascii.hexlify(os.urandom(8)).decode()),
            'support_webview': "1",
            'reg_store_region': random.choice(regions).lower(),
            'user_selected_region': "0",
            'cronet_version': "f6248591_2024-09-11",
            'ttnet_version': "4.2.195.9-tiktok",
            'use_store_region_cookie': "1"
        }

        payload = {"email": email}

        # إعدادات الـ User-Agent
        app_name = "com.zhiliaoapp.musically"
        app_version = f"{random.randint(2000000000, 3000000000)}"
        platform = "Linux"
        os_version = f"Android {random.randint(10, 15)}"
        locales = ["ar_AE", "en_US", "fr_FR", "es_ES"]
        locale = random.choice(locales)
        device_type = random.choice(["phone", "tablet", "tv"])
        build = f"UP1A.{random.randint(200000000, 300000000)}"
        cronet_version = f"{random.randint(10000000, 20000000)}"
        cronet_date = f"{random.randint(2023, 2025)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}"
        quic_version = f"{random.randint(10000000, 20000000)}"
        quic_date = f"{random.randint(2023, 2025)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}"

        user_agent = (f"{app_name}/{app_version} ({platform}; U; {os_version}; {locale}; {device_type}; "
                      f"Build/{build}; Cronet/{cronet_version} {cronet_date}; "
                      f"QuicVersion:{quic_version} {quic_date})")

        x_args = sign(params=urlencode(params), payload="", cookie="")

        headers = {
            'User-Agent': user_agent,
            'x-tt-passport-csrf-token': secret,
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'x-argus': x_args["x-argus"],
            'x-gorgon': x_args["x-gorgon"],
            'x-khronos': x_args["x-khronos"],
            'x-ladon': x_args["x-ladon"],
        }

        # إرسال الطلب
        url = "https://api22-normal-c-alisg.tiktokv.com/passport/email/bind_without_verify/"
        response = session.post(url, params=params, data=payload, headers=headers).text

        # تحديد الاستجابة بناءً على المحتوى
        if "1023" in response:
            return {"status": "Good", "by": "@jokerpython3"}
        else:
            return {"status": "Bad", "by": "@jokerpython3"}

    except Exception as e:
        # في حالة حدوث خطأ، إرجاع حالة خطأ واضحة
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
