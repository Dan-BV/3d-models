import zipfile, sys

name = "Ender3Pro PLA Naruto fine 0.08 v3"
out = sys.argv[1]

common = """\
layer_height = 0.08
layer_height_0 = 0.2
material_bed_temperature = 60
material_bed_temperature_layer_0 = 65
material_print_temperature = 210
material_print_temperature_layer_0 = 215
adhesion_type = brim
brim_width = 5
brim_outside_only = True
brim_gap = 0
skirt_brim_speed = 15
adhesion_z_offset = 1.1
support_enable = True
support_type = everywhere
support_structure = tree
support_angle = 65
support_tree_angle = 45
support_tree_branch_diameter = 3
support_tree_tip_diameter = 0.8
support_tree_top_rate = 15
support_z_distance = 0.16
support_bottom_distance = 0.16
support_xy_distance = 0.7
support_xy_distance_overhang = 0.3
support_xy_overrides_z = z_overrides_xy
support_interface_enable = False
support_brim_enable = True
support_line_width = 0.35
speed_support = 60
minimum_support_area = 0.1
retraction_combing = all
retraction_combing_max_distance = 0
retraction_hop_enabled = True
retraction_hop = 0.2
retraction_hop_only_when_collides = False
travel_avoid_other_parts = True
travel_avoid_supports = True
travel_avoid_distance = 0.8
"""

extruder = common + """\
line_width = 0.4
wall_line_width_0 = 0.38
initial_layer_line_width_factor = 110
wall_line_count = 2
wall_line_width_x = 0.45
optimize_wall_printing_order = True
outer_inset_first = False
fill_outline_gaps = True
min_wall_line_width = 0.2
top_layers = 12
bottom_layers = 8
z_seam_type = back
z_seam_corner = z_seam_corner_weighted
infill_sparse_density = 8
infill_sparse_thickness = 0.16
infill_pattern = gyroid
infill_before_walls = False
xy_offset_layer_0 = -0.1
material_flow = 100
speed_print = 40
speed_infill = 70
speed_topbottom = 25
speed_wall_0 = 18
speed_wall_x = 45
speed_layer_0 = 15
speed_print_layer_0 = 15
speed_travel_layer_0 = 60
speed_slowdown_layers = 3
speed_travel = 150
small_feature_max_length = 30
small_feature_speed_factor = 50
small_feature_speed_factor_0 = 50
retraction_enable = True
retraction_amount = 4.5
retraction_speed = 60
retraction_min_travel = 2
travel_retract_before_outer_wall = True
wall_0_wipe_dist = 0.2
cool_fan_enabled = True
cool_fan_speed = 100
cool_fan_speed_max = 100
cool_fan_speed_0 = 0
cool_fan_full_layer = 4
cool_min_layer_time = 10
cool_min_speed = 8
cool_lift_head = False
"""

def sec(body, extra_meta):
    return ("[general]\nversion = 4\nname = %s\ndefinition = creality_ender3pro\n\n"
            "[metadata]\ntype = quality_changes\nquality_type = super\n%ssetting_version = 27\n\n"
            "[values]\n%s" % (name, extra_meta, body))

tag = name.replace(" ", "+")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("Creality+Ender-3+Pro_" + tag, sec(common, ""))
    z.writestr("creality_base_extruder_0+%232_" + tag,
               sec(extruder, "intent_category = default\nposition = 0\n"))
print("written", out)
