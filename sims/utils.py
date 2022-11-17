from datetime import datetime


def handle_irrigation(date_sim: datetime, date_start_irrigation: datetime, irrigation_freq: int, sapflow: list,
                      drip_rate: float, replacement_fraction: float, irrigation_to_apply: float = 0.) -> (float, float):
    days_since_irrigation_start = (date_sim - date_start_irrigation).days
    if days_since_irrigation_start % irrigation_freq == 0:
        irrigation_to_apply += (sapflow[-24 * 7:]) / 1000 * replacement_fraction

    if irrigation_to_apply > 0:
        irrigation_rate_max = drip_rate  # hr * kg hr-1
        irrigation_applied = min(irrigation_to_apply, drip_rate)
        irrigation_remain = max(0.0, irrigation_to_apply - irrigation_applied)
    else:
        irrigation_applied = 0
        irrigation_remain = 0
    return irrigation_applied, irrigation_remain
