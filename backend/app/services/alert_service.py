"""
IGNIS — Alert Service

Handles alert lifecycle management:
- Creating alerts when high-severity hotspots are classified
- Broadcasting alerts via WebSocket
- Acknowledging and resolving alerts
"""

import logging
import httpx
from sqlalchemy.orm import Session

from app.models.spatial import Alert, Hotspot, MLClassificationEnum, SystemSetting

logger = logging.getLogger("ignis.services.alert")

# Thresholds for automatic alert generation
FRP_CRITICAL_THRESHOLD = 200.0  # MW
FRP_HIGH_THRESHOLD = 100.0

def dispatch_notifications(db: Session, alert: Alert, hotspot: Hotspot):
    """
    Simulates sending notifications (Push, Email, Sound) by checking the SystemSetting table.
    """
    # Fetch all notification settings
    settings = db.query(SystemSetting).filter(SystemSetting.key.like("settings_notif_%")).all()
    prefs = {s.key: s.value == 'true' for s in settings}
    
    # Defaults in case settings are missing
    notif_ind = prefs.get("settings_notif_ind", True)
    notif_gas = prefs.get("settings_notif_gas", False)
    notif_email = prefs.get("settings_notif_email", False)
    notif_sound = prefs.get("settings_notif_sound", True)

    msg = f"[NOTIFICATION DISPATCH] Alert {alert.id} ({alert.alert_type}): "
    actions = []

    if hotspot.ml_label == MLClassificationEnum.INDUSTRIAL_FIRE and notif_ind:
        actions.append("PUSH_NOTIFICATION (Industrial)")
    
    if hotspot.ml_label == MLClassificationEnum.GAS_FLARE and notif_gas:
        actions.append("PUSH_NOTIFICATION (Gas Flare)")

    if alert.severity == "CRITICAL" and notif_sound:
        actions.append("SOUND_ALARM")

    if notif_email:
        actions.append("QUEUE_EMAIL_DIGEST")

    if actions:
        logger.warning(msg + " | ".join(actions))
    else:
        logger.info(f"No notifications dispatched for alert {alert.id} based on user preferences.")

    # External Webhook Logic
    webhook_url_setting = db.query(SystemSetting).filter(SystemSetting.key == "settings_webhook_url").first()
    if webhook_url_setting and webhook_url_setting.value and alert.severity == "CRITICAL":
        payload = {
            "text": f"🔥 *CRITICAL INCIDENT DETECTED* 🔥\n"
                    f"*Type:* {alert.alert_type}\n"
                    f"*Location:* {hotspot.latitude}, {hotspot.longitude}\n"
                    f"*FRP:* {hotspot.frp} MW\n"
                    f"*Confidence:* {hotspot.confidence}%\n"
                    f"*Time:* {hotspot.acq_date}"
        }
        try:
            httpx.post(webhook_url_setting.value, json=payload, timeout=5.0)
            logger.info(f"Dispatched webhook alert to {webhook_url_setting.value}")
        except Exception as e:
            logger.error(f"Failed to dispatch webhook alert: {e}")


def create_alert_if_needed(db: Session, hotspot: Hotspot) -> Alert | None:
    """
    Check if a classified hotspot warrants an alert.
    Industrial fires with FRP > threshold trigger alerts automatically.
    """
    if hotspot.ml_label == MLClassificationEnum.INDUSTRIAL_FIRE:
        if hotspot.frp and hotspot.frp > FRP_CRITICAL_THRESHOLD:
            severity = "CRITICAL"
            alert_type = "CRITICAL_INDUSTRIAL_FIRE"
        elif hotspot.frp and hotspot.frp > FRP_HIGH_THRESHOLD:
            severity = "HIGH"
            alert_type = "HIGH_FRP_INDUSTRIAL_FIRE"
        else:
            severity = "MEDIUM"
            alert_type = "INDUSTRIAL_FIRE_DETECTED"
    elif hotspot.ml_label == MLClassificationEnum.GAS_FLARE:
        if hotspot.frp and hotspot.frp > FRP_HIGH_THRESHOLD:
            severity = "HIGH"
            alert_type = "ABNORMAL_GAS_FLARE"
        else:
            return None  # Normal gas flares don't trigger alerts
    else:
        return None

    alert = Alert(
        hotspot_id=hotspot.id,
        alert_type=alert_type,
        severity=severity,
        status="NEW",
    )
    db.add(alert)
    db.flush() # flush to get alert.id
    
    logger.info(f"Alert created: {alert_type} (severity={severity}) for hotspot {hotspot.id}")
    
    # Check preferences and dispatch
    dispatch_notifications(db, alert, hotspot)
    
    return alert


def acknowledge_alert(db: Session, alert_id: int) -> Alert | None:
    """Mark an alert as acknowledged."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.status = "ACKNOWLEDGED"
        alert.is_read = True
        db.commit()
    return alert


def resolve_alert(db: Session, alert_id: int, note: str = None) -> Alert | None:
    """Mark an alert as resolved with an optional resolution note."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.status = "RESOLVED"
        alert.is_read = True
        alert.resolution_note = note
        db.commit()
    return alert


def get_active_alerts(db: Session, limit: int = 50):
    """Return all non-resolved alerts, newest first."""
    return (
        db.query(Alert)
        .filter(Alert.status != "RESOLVED")
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )
