import math
import random
from datetime import datetime, timedelta, timezone


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _noise(t, seed):
    # Deterministic pseudo-noise from time + seed (no shared state).
    return (
        math.sin(t * 0.37 + seed * 1.13)
        + math.sin(t * 0.11 + seed * 2.09)
        + math.sin(t * 0.71 + seed * 0.73)
    ) / 3.0


def sim_metrics(step_index: int, tz_name: str = "UTC"):
    """
    Generate realistic synthetic IoT metrics for a given simulation step.
    step_index increments each poll from the frontend.
    """
    # Use UTC to avoid timezone edge cases.
    now = datetime.now(timezone.utc)

    # Moisture typically drifts and reacts to "irrigation" pulses.
    irrigation_pulse = math.exp(-((step_index % 48) - 12) ** 2 / (2 * 6**2))
    moisture_base = 58.0 - 0.35 * math.sin(step_index * 0.08)
    moisture = moisture_base + 10.0 * irrigation_pulse + 3.0 * _noise(step_index, 1.0)
    moisture = _clamp(moisture, 18.0, 86.0)

    # Temperature varies with slow cycles.
    temperature = 23.5 + 1.8 * math.sin(step_index * 0.06) + 1.2 * _noise(step_index, 2.0)
    temperature = _clamp(temperature, 14.0, 36.0)

    # Crop health correlates with moisture and temperature stability.
    health = 92.0 + (moisture - 55.0) * 0.35 - abs(temperature - 26.0) * 0.55
    health += 2.0 * _noise(step_index, 3.0)
    health = _clamp(health, 35.0, 99.0)

    # Wind speed mostly changes slowly.
    wind_speed = 10.0 + 3.0 * math.sin(step_index * 0.09 + 1.1) + 1.5 * _noise(step_index, 4.0)
    wind_speed = _clamp(wind_speed, 2.0, 26.0)

    # Humidity (optional for later expansion).
    humidity = 52.0 + 7.0 * math.cos(step_index * 0.05 + 0.3) + 3.0 * _noise(step_index, 5.0)
    humidity = _clamp(humidity, 25.0, 92.0)

    # Build short trend history (last 12 points).
    history_len = 12
    points = list(range(step_index - history_len + 1, step_index + 1))

    soil_trend = []
    temp_trend = []
    wind_trend = []
    labels = []
    for i in points:
        t_m = i
        irrigation = math.exp(-((t_m % 48) - 12) ** 2 / (2 * 6**2))
        m_base = 58.0 - 0.35 * math.sin(t_m * 0.08)
        m_val = _clamp(m_base + 10.0 * irrigation + 3.0 * _noise(t_m, 1.0), 18.0, 86.0)
        temp_val = _clamp(23.5 + 1.8 * math.sin(t_m * 0.06) + 1.2 * _noise(t_m, 2.0), 14.0, 36.0)

        soil_trend.append(round(m_val, 1))
        temp_trend.append(round(temp_val, 1))

        wind_val = _clamp(
            10.0 + 3.0 * math.sin(t_m * 0.09 + 1.1) + 1.5 * _noise(t_m, 4.0),
            2.0,
            26.0,
        )
        wind_trend.append(round(wind_val, 1))

        age_min = max(0, (step_index - i) * 5)
        labels.append(f"{age_min}m")

    alerts = []

    # Alert rules (simple but realistic).
    if moisture < 35.0:
        alerts.append(
            {
                "type": "warning",
                "title": "Low moisture detected",
                "detail": "Consider targeted irrigation for the affected zone.",
            }
        )

    if temperature > 30.0:
        alerts.append(
            {
                "type": "warning",
                "title": "Heat stress risk",
                "detail": "Check canopy conditions and irrigation schedule.",
            }
        )

    if wind_speed > 18.0:
        alerts.append(
            {
                "type": "info",
                "title": "High wind detected",
                "detail": "Secure equipment and adjust spraying windows if needed.",
            }
        )

    # Pump maintenance due periodically.
    if (step_index % 60) >= 56:
        alerts.append(
            {
                "type": "maintenance",
                "title": "Pump maintenance due",
                "detail": "Inspect filters and check motor load trend.",
            }
        )

    # Cap alerts for UI.
    alerts = alerts[:3]

    # Convert to relative timestamps for display.
    alert_items = []
    for idx, a in enumerate(alerts):
        minutes_ago = 30 + idx * 12
        ts = now - timedelta(minutes=minutes_ago)
        alert_items.append(
            {
                "type": a["type"],
                "title": a["title"],
                "detail": a["detail"],
                "timestamp": ts.isoformat(),
                "minutesAgo": minutes_ago,
            }
        )

    return {
        "at": now.isoformat(),
        "avg_soil_moisture": round(moisture, 1),
        "temperature": round(temperature, 1),
        "crop_health": round(health, 0),
        "wind_speed": round(wind_speed, 1),
        "humidity": round(humidity, 0),
        "soil_trend": soil_trend,
        "temp_trend": temp_trend,
        "wind_trend": wind_trend,
        "trend_labels": labels,
        "alerts": alert_items,
    }

