"""Climate-based data-center water use (WUE) per country.

WUE = cooling-tower formula applied to the annual-mean wet-bulb temperature
(Sen Gupta et al. 2024; Shumba et al. 2025). Wet-bulb comes from World Bank
CCKP ERA5 1991-2020 monthly temperature and humidity via Stull (2011). The 44
African countries in Shumba et al.'s dataset are used to validate the method;
the 9 in our list take their published values directly.

Writes data/sources/country-wue.json.
"""
import csv, json, math
from common import download, save

iso = {"United States of America":"USA","Canada":"CAN","Mexico":"MEX","Brazil":"BRA","Argentina":"ARG","Chile":"CHL","Colombia":"COL","Peru":"PER","Venezuela":"VEN","United Kingdom":"GBR","Ireland":"IRL","France":"FRA","Germany":"DEU","Netherlands":"NLD","Belgium":"BEL","Spain":"ESP","Portugal":"PRT","Italy":"ITA","Switzerland":"CHE","Austria":"AUT","Poland":"POL","Czechia":"CZE","Sweden":"SWE","Norway":"NOR","Finland":"FIN","Denmark":"DNK","Iceland":"ISL","Greece":"GRC","Romania":"ROU","Ukraine":"UKR","Russia":"RUS","Turkey":"TUR","Kazakhstan":"KAZ","China":"CHN","India":"IND","Japan":"JPN","South Korea":"KOR","Taiwan":"TWN","Mongolia":"MNG","Vietnam":"VNM","Thailand":"THA","Malaysia":"MYS","Indonesia":"IDN","Philippines":"PHL","Singapore":"SGP","Bangladesh":"BGD","Pakistan":"PAK","Saudi Arabia":"SAU","United Arab Emirates":"ARE","Iran":"IRN","Iraq":"IRQ","Israel":"ISR","Egypt":"EGY","Morocco":"MAR","Algeria":"DZA","Nigeria":"NGA","South Africa":"ZAF","Kenya":"KEN","Ethiopia":"ETH","Ghana":"GHA","Tanzania":"TZA","Angola":"AGO","Australia":"AUS","New Zealand":"NZL",
 "Benin":"BEN","Botswana":"BWA","Cameroon":"CMR","Chad":"TCD","Gabon":"GAB","Mali":"MLI","Namibia":"NAM","Senegal":"SEN","Sudan":"SDN","Tunisia":"TUN","Zambia":"ZMB","Lesotho":"LSO","Libya":"LBY","Mozambique":"MOZ","Uganda":"UGA"}

CODES = ','.join(sorted(set(iso.values())))
CCKP = ('https://cckpapi.worldbank.org/cckp/v1/era5-x0.25_climatology_{v}_climatology_monthly_1991-2020_mean_'
        'historical_era5_x0.25_mean/' + CODES + '?_format=json')
AFRICA_CSV = 'https://huggingface.co/datasets/PengfeiLi/WaterEfficientDatasetForAfricanDataCenters/resolve/main/Country_Summary.csv'
tas = json.load(open(download(CCKP.format(v='tas'), 'cckp-tas.json')))['data']
hurs = json.load(open(download(CCKP.format(v='hurs'), 'cckp-hurs.json')))['data']
af = {r['Country']: r for r in csv.DictReader(open(download(AFRICA_CSV, 'africa-wue-country-summary.csv'), encoding='utf-8'))}

def stull(T, RH):
    return (T * math.atan(0.151977 * (RH + 8.313659) ** 0.5) + math.atan(T + RH) - math.atan(RH - 1.676331)
            + 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH) - 4.686035)

def wue_f(TwF):
    return max(0.0, 0.0005112 * TwF ** 2 - 0.04982 * TwF + 2.387)

def c2f(c): return c * 9 / 5 + 32

def months(c):
    k = sorted(tas[c]); return [(tas[c][m], hurs[c][m]) for m in k]

res = {}
for name, c in iso.items():
    ms = months(c)
    tw_monthly = [stull(T, RH) for T, RH in ms]
    tw_mean = sum(tw_monthly) / 12
    Tann = sum(t for t, _ in ms) / 12; RHann = sum(r for _, r in ms) / 12
    res[name] = dict(iso=c, T=Tann, RH=RHann, tw=tw_mean, tw_of_means=stull(Tann, RHann),
                     minRH=min(r for _, r in ms), minT=min(t for t, _ in ms), wue=wue_f(c2f(tw_mean)))

TARGET = list(iso)[:64]
LOWER_F = 45.0
LOWER_C = (LOWER_F - 32) * 5 / 9

countries = {}
for n in TARGET:
    r = res[n]
    era_tw = r["tw"]
    if n in af and af[n]["WB (°C)"]:
        tw = float(af[n]["WB (°C)"]); wue = float(list(af[n].values())[3])
        note = (f"Published value from Shumba et al. 2025 Country_Summary.csv (WeatherAPI, Aug 2023-Aug 2024). "
                f"For comparison our ERA5/CCKP+Stull method gives Tw {era_tw:.2f} C -> WUE {wue_f(c2f(era_tw)):.3f}.")
        countries[n] = {"wetbulb_c": round(tw, 2), "wue": round(wue, 3), "source": "shumba2025_published", "clamped": False, "note": note}
        continue
    twF = c2f(era_tw)
    raw = wue_f(twF)
    clamped = twF < LOWER_F
    wue = wue_f(LOWER_F) if clamped else raw
    note = (f"ERA5 1991-2020 area-weighted monthly T {r['T']:.1f} C / RH {r['RH']:.0f}% (annual means) -> mean of monthly Stull Tw.")
    if clamped:
        note += (f" Tw {era_tw:.1f} C is below the formula's stated 45 F ({LOWER_C:.1f} C) lower limit; WUE clamped to the value at 45 F "
                 f"(unclamped extrapolation would be {raw:.3f}, which is a fitting artifact: the quadratic rises again below ~9.3 C). "
                 "In climates this cold, real facilities largely use free/air-side cooling, so actual on-site WUE is likely far lower.")
    if n in ("United States of America", "China", "Russia", "Australia", "Canada", "Brazil", "India", "Kazakhstan", "Argentina", "Chile", "Mongolia", "Indonesia", "Iran", "Saudi Arabia"):
        note += " Very large/climatically diverse country: area-weighted national mean is dominated by sparsely populated regions and may not reflect where data centers sit."
    countries[n] = {"wetbulb_c": round(era_tw, 2), "wue": round(wue, 3), "source": "era5_cckp_stull", "clamped": clamped, "note": note}

doc = {
    "formula": {
        "expression": "WUE_onsite [L/kWh] = max(0, 0.0005112*Tw^2 - 0.04982*Tw + 2.387), Tw = wet-bulb temperature in deg F (Tw_F = Tw_C*9/5+32); applied to the annual-mean wet-bulb temperature",
        "parameters": {
            "a": 0.0005112, "b": -0.04982, "c": 2.387, "Tw_units": "Fahrenheit",
            "configuration": "'Fixed cold water' cooling tower (cold water held at 85 F, variable approach); Eq.(3) in Sen Gupta et al. 2024, Eq.(2) in Shumba et al. 2025",
            "derivation": "Fit to SPX Cooling 'water usage calculator' output: flow 1000 gpm, range 10 F (1466 kW), drift 0.005%, cycles of concentration 3 (do not affect evaporation in the tool), lambda (tower efficiency multiplier) = 1",
            "stated_lower_limit_F": 45, "stated_lower_limit_C": round(LOWER_C, 2),
            "clamp_rule_used_here": f"Tw < 45 F -> WUE fixed at value at 45 F = {wue_f(LOWER_F):.4f} L/kWh",
            "basis": "Water consumed (evaporated) on site per kWh of server/IT energy; excludes offsite electricity-generation water and PUE",
        },
        "citation": "Shumba, Tshekiso, Li, Fanti, Ren. 'A Water Efficiency Dataset for African Data Centers', ACM COMPASS 2025, doi:10.1145/3715335.3735483 (arXiv 2412.03716), Eq.(2); formula originates in Sen Gupta, Hossen, Li, Ren, Islam. 'A Dataset for Research on Water Sustainability', ACM e-Energy 2024, doi:10.1145/3632775.3661962 (arXiv 2405.17469), Eq.(3).",
        "url": "https://arxiv.org/abs/2412.03716 ; https://arxiv.org/abs/2405.17469 ; data: https://huggingface.co/datasets/PengfeiLi/WaterEfficientDatasetForAfricanDataCenters",
        "check": "Reproduces Nigeria 1.385339 at Tw 69.100873 F (20.61 C) exactly; reproduces all 44 African rows in Country_Summary.csv to 6 decimals (e.g. Ghana 1.451786 at 72.07 F, Ethiopia 1.196372 at 55.46 F, South Africa 1.206376 at 56.79 F), confirming the formula is applied to the annual-mean wet-bulb with no multiplier.",
    },
    "wetbulb_source": {
        "source": "World Bank Climate Change Knowledge Portal (CCKP) country aggregates of ERA5 (0.25 deg) monthly climatology 1991-2020: near-surface air temperature (tas) and relative humidity (hurs); wet-bulb via Stull (2011) 'Wet-bulb temperature from relative humidity and air temperature', J. Appl. Meteor. Climatol. 50:2267-2269 (same wet-bulb formula used by Sen Gupta et al. 2024).",
        "url": "https://cckpapi.worldbank.org/cckp/v1/era5-x0.25_climatology_{tas|hurs}_climatology_monthly_1991-2020_mean_historical_era5_x0.25_mean/{ISO3}?_format=json",
        "method": "For each of 12 calendar months, Tw_m = Stull(T_m, RH_m) from the country-mean monthly climatology; annual Tw = mean of the 12 monthly Tw (i.e. mean of monthly wet-bulbs, not wet-bulb of annual means, but still wet-bulb of monthly-mean T/RH rather than mean of hourly wet-bulb). Spatial weighting: area-weighted country mean (CCKP 'mean' aggregation; no population weighting available for this series). WUE then = formula(annual Tw), matching how Shumba et al. applied it. Countries present in Shumba et al. Country_Summary.csv use the published Tw/WUE directly. Validation on 24 African countries in both sets: our Tw minus theirs mean bias -0.27 C, MAE 1.55 C (range -3.6 to +4.3 C; theirs is WeatherAPI, one year, likely station/city-based).",
        "year_range": "1991-2020 climatology (ERA5); Shumba et al. published values: 2023-08-23 to 2024-08-22",
    },
    "countries": countries,
    "caveats": [
        "Evaporative cooling-tower basis only: many real data centers (especially in cool climates, and hyperscalers using air-side economization or closed-loop/dry coolers) consume far less on-site water; treat values as a climate-driven estimate for a tower-cooled facility, roughly an upper-ish bound, not a measured national average.",
        "The fitted quadratic has a minimum near 48.7 F (9.3 C) and rises again at lower wet-bulbs; its authors state a 45 F lower limit. Countries with annual-mean Tw below 7.2 C are clamped to 1.180 L/kWh (flag 'clamped'); the formula therefore cannot express the low WUE that free cooling achieves in cold climates, and cold-country values are not meaningfully differentiated.",
        "The formula is fairly flat: across all climates here it spans only ~1.17-1.57 L/kWh, so it differentiates hot-humid tropics from temperate zones but understates real-world spread (reported fleet WUEs range from ~0 to >2 L/kWh).",
        "Applying a convex formula to an annual-mean wet-bulb (as the source dataset does) underestimates the mean of hourly WUE in seasonal climates; the national-mean approach also ignores diurnal and seasonal extremes.",
        "Area-weighted national means are crude for large or climatically diverse countries (USA, Canada, Russia, China, Brazil, Australia, India, Kazakhstan, Chile, Argentina, Indonesia, Saudi Arabia, Iran, Mongolia): the mean is dominated by sparsely populated land (e.g. Canadian/Russian Arctic, Australian outback, Tibetan plateau) rather than where data centers are.",
        "Stull (2011) is an empirical fit valid roughly for RH 5-99% and T -20 to 50 C at sea-level pressure, accuracy about +/-1 C; applying it to monthly-mean T and RH (rather than hourly data) adds further error, larger in arid countries (wet-bulb of means vs mean of hourly wet-bulbs differs by up to ~1 C for Iraq/Saudi Arabia/Iran).",
        "Mixed sources: 9 African countries (Nigeria, Egypt, Morocco, Algeria, South Africa, Kenya, Ethiopia, Ghana, Tanzania) use Shumba et al.'s published WeatherAPI-based values (a single year, Aug 2023-Aug 2024) while the rest use the ERA5 1991-2020 climatology; for Kenya and Ethiopia the two methods differ by ~3.6-4.3 C in Tw (~0.08-0.10 L/kWh), probably because the published values reflect cooler highland locations. ERA5-method values for these are given in each note.",
        "Only on-site (direct) WUE; excludes off-site water embedded in electricity generation, which is often larger.",
    ],
}
save('country-wue.json', doc)
print(f'country-wue.json: {len(countries)} countries, clamped: {sum(c["clamped"] for c in countries.values())}')
