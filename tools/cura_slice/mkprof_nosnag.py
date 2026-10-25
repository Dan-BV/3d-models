# Cura "Standard" Generic PLA for Ender 3 Pro plus travel settings that keep
# the nozzle from snagging part edges when it jumps between models.
import sys, zipfile
NAME = 'Ender3Pro PLA Standard nosnag 0.20'
SLUG = NAME.replace(' ', '+')
GLOBAL = {
    'adhesion_z_offset': 1.1,
}
EXTRUDER = {
    'retraction_hop_enabled': True,
    'retraction_hop': 0.4,
    'retraction_hop_only_when_collides': False,
    'retraction_combing': 'noskin',
    'travel_avoid_other_parts': True,
    'travel_avoid_distance': 1.2,
    'cool_fan_full_layer': 5,
    'adhesion_z_offset': 1.1,
}
def section(vals, extruder):
    meta = 'type = quality_changes\nquality_type = standard\n'
    if extruder: meta += 'intent_category = default\nposition = 0\n'
    meta += 'setting_version = 27\n'
    body = '\n'.join(f'{k} = {v}' for k, v in vals.items())
    return (f'[general]\nversion = 4\nname = {NAME}\ndefinition = creality_ender3pro\n\n'
            f'[metadata]\n{meta}\n[values]\n{body}\n\n')
out = sys.argv[1]
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr(f'Creality+Ender-3+Pro_{SLUG}', section(GLOBAL, False))
    z.writestr(f'creality_base_extruder_0+%232_{SLUG}', section(EXTRUDER, True))
print('wrote', out)
