from datetime import datetime


def handle_irrigation(date_sim: datetime, date_start_irrigation: datetime, irrigation_freq: int, sapflow: list,
                      drip_rate: float, replacement_fraction: float, irrigation_to_apply: float = 0.) -> (float, float):
    days_since_irrigation_start = (date_sim - date_start_irrigation).days
    if all((days_since_irrigation_start >= 0,
            days_since_irrigation_start % irrigation_freq == 0,
            date_sim.hour == 5)):  # assumed irrigation starts at 5am
        irrigation_to_apply += sum(sapflow[-24 * irrigation_freq:]) * replacement_fraction * 3600.

    if irrigation_to_apply > 0:
        irrigation_applied = min(irrigation_to_apply, drip_rate)
        irrigation_remain = max(0.0, irrigation_to_apply - irrigation_applied)
    else:
        irrigation_applied = 0
        irrigation_remain = 0
    return irrigation_applied, irrigation_remain
