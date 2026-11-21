# security.py - Privacy Score + ATO
from dataclasses import dataclass
from typing import Dict, List
import math

@dataclass
class LoginContext:
    ip_country: str
    last_country: str
    hours_since_last_login: float
    is_new_device: bool
    failed_attempts: int
    ip_asn: str = ""
    last_asn: str = ""
    logins_last_10min: int = 0
    sensitive_actions_last_10min: int = 0
    distance_km: float = 0.0
    is_tor: bool = False
    is_datacenter_ip: bool = False

class NoorSecurityAlgorithms:
    @staticmethod
    def calculate_privacy_health_score(settings: Dict) -> Dict:
        score = 100
        recs: List[Dict] = []
        def penalize(amount, action, title, impact, severity, patch=None):
            nonlocal score
            score -= amount
            recs.append({"action": action, "title": title, "impact": impact, "severity": severity, "patch": patch or {}, "penalty": amount})
        if not settings.get("two_factor_enabled", False):
            penalize(30, "ENABLE_2FA", "تفعيل المصادقة الثنائية (2FA)", "+30%", "critical", {"route": "/settings/security/2fa"})
        if not settings.get("passkey_count", 0):
            penalize(10, "ADD_PASSKEY", "أضف Passkey - دخول بالبصمة", "+10%", "high", {"route": "/settings/security/passkey"})
        if settings.get("default_post_audience") == "PUBLIC":
            penalize(15, "RESTRICT_AUDIENCE", "تقييد المنشورات للأصدقاء فقط", "+15%", "high", {"default_post_audience": "FRIENDS"})
        if settings.get("app_lock_timeout", 0) == 0:
            penalize(10, "ENABLE_APP_LOCK", "تفعيل قفل نور شات بالبصمة", "+10%", "medium", {"app_lock_timeout": 1})
        if settings.get("phone_visibility") == "PUBLIC":
            penalize(10, "HIDE_PHONE", "رقم تلفونك ظاهر للعامة", "+10%", "high", {"phone_visibility": "FRIENDS"})
        if settings.get("active_status", True):
            penalize(5, "HIDE_ACTIVE_STATUS", "إخفاء حالة النشاط", "+5%", "low", {"active_status": False})
        if settings.get("message_delivery") == "EVERYONE":
            penalize(10, "LIMIT_MESSAGES", "الغرباء يقدروا يراسلوك - قيدها للأصدقاء", "+10%", "high", {"message_delivery": "FRIENDS"})
        score = max(0, score)
        recs = sorted(recs, key=lambda x: x["penalty"], reverse=True)
        return {"privacy_score": score, "status": "ممتاز 🟢" if score >= 85 else ("جيد 🟡" if score >= 70 else ("متوسط 🟠" if score >= 50 else "يحتاج تحسين 🔴")), "total_issues": len(recs), "quick_fixes": recs, "fix_all_patch": {k: v for r in recs for k, v in r.get("patch", {}).items() if k != "route"}}

    @staticmethod
    def detect_account_takeover_risk(ctx: LoginContext) -> Dict:
        travel = 0.0
        if ctx.ip_country != ctx.last_country:
            if ctx.hours_since_last_login < 2: travel = 1.0
            elif ctx.hours_since_last_login < 4: travel = 0.7
            else: travel = 0.3
        elif ctx.distance_km > 500 and ctx.hours_since_last_login < 2: travel = 1.0
        device = 1.0 if ctx.is_new_device else 0.0
        velocity = min(1.0, ctx.logins_last_10min / 5.0)
        ip_risk = 1.0 if ctx.is_tor else (0.8 if ctx.is_datacenter_ip else (0.5 if ctx.ip_asn and ctx.last_asn and ctx.ip_asn != ctx.last_asn else 0.0))
        failed = min(0.4, ctx.failed_attempts * 0.1) if ctx.failed_attempts > 0 else 0.0
        sensitive = 1.0 if ctx.sensitive_actions_last_10min >= 2 else (0.5 if ctx.sensitive_actions_last_10min == 1 else 0.0)
        z = (0.25 * travel + 0.20 * device + 0.15 * velocity + 0.10 * ip_risk + 0.10 * failed + 0.20 * sensitive) * 4 - 1.5
        risk = round(1 / (1 + math.exp(-z)), 2)
        if risk >= 0.75: action, lock, msg = "BIOMETRIC_OR_PASSKEY_CHALLENGE", True, "نشاط غير عادي - تم قفل الإعدادات الحساسة"
        elif risk >= 0.30: action, lock, msg = "TOTP_CHALLENGE", False, "دخول غير معتاد - أدخل كود المصادقة"
        else: action, lock, msg = "ALLOW", False, "دخول آمن"
        return {"risk_score": risk, "lock_sensitive_settings": lock, "action_required": action, "message": msg, "breakdown": {"impossible_travel": travel, "new_device": device, "login_velocity": velocity, "ip_reputation": ip_risk, "failed_attempts": failed, "sensitive_burst": sensitive}, "locked_features": ["change_password","change_email","change_phone","disable_2fa","unblock_users","request_data_export","delete_account"] if lock else []}
