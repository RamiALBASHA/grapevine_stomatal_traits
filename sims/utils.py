from datetime import datetime


def handle_irrigation(date_sim: datetime, date_start_irrigation: datetime, irrigation_freq: int, sapflow: list,
                      irrigation_to_apply: float, drip_rate: float, rdi: float) -> (float, float):
    days_since_irrigation_start = (date_sim - date_start_irrigation).days
    if days_since_irrigation_start % irrigation_freq == 0:
        irrigation_to_apply += (sapflow[-24 * 7:]) / 1000 * rdi

    if irrigation_to_apply > 0:
        irrigation_rate_max = drip_rate  # hr * kg hr-1
        irrigation_to_apply = irrigation_to_apply  # replace a percentage of cumul. transpiration
        irrigation_applied = min(irrigation_to_apply, irrigation_rate_max)
        irrigation_remain = max(0.0, irrigation_to_apply - irrigation_applied)  # amount remaining to apply
    else:
        irrigation_applied = 0
        irrigation_remain = 0
    return irrigation_applied, irrigation_remain
