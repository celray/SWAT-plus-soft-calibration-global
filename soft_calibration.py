"""
Author      : Celray James CHAWANDA
Institution : VUB
Contact     : celray.chawanda@outlook.com

"""
import os, sys, time

class parameter:
    def __init__(self, name, chg_type, r_):
        self.par_name = name
        self.chg_type = chg_type
        self.l_limit = None
        self.u_limit = None
        self.value = 0

        self.set_bound_u = None
        self.set_bound_l = None

        self.ratio_type = r_

class ratios:
    def __init__(self):
        self.name = None
        self.et_r = None
        self.pe_r = None
        self.la_r = None
        self.sr_r = None
class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def get_x_intercept(point_1, point_2):
    if (point_2.x-point_1.x) == 0:
        m = "infinity"
        y_int = None
        x_int = None
    else:
        m = float((point_2.y-point_1.y))/(point_2.x-point_1.x)
        y_int = point_1.y - (m*point_1.x)   
        if float((point_2.y-point_1.y)) == 0:
            x_int = None
        else:
            x_int = float(0 - y_int)/m

    return x_int

def write_to(filename, string):
    """
    function to write string to file
    """
    fl = open(filename, "w")
    fl.write(string)
    fl.close()

def read_from(filename):
    """
    function to read from file; lines are lists
    """
    fl = open(filename, "r")
    raw = fl.readlines()
    fl.close()
    return raw

def change_parms(current_parms, name, chg_type, value, txtinout_dir_, print_ = False):
    """
    function to change the parameter value in parameter file (callibration.cal)
    """
    calibration_cal = "calibration.cal for soft data calibration\n  {0}\nNAME           CHG_TYP                  VAL   CONDS  LYR1   LYR2  YEAR1  YEAR2   DAY1   DAY2  OBJ_TOT\n".format(
        len(current_parms))
    for parm in current_parms:
        if parm.par_name == name:
            print("\t> changing parameter {0} to value, {1} with change type {2}".format(parm.par_name, value, chg_type))
            parm.chg_type = chg_type
            parm.value = value
        calibration_cal += "{0}{1}{2}      0     0      0      0      0      0      0        0      0\n".format("{0}".format(str(parm.par_name).ljust(16)), str(parm.chg_type).ljust(16), '{0:.3f}'.format(parm.value).rjust(12))
    write_to("{0}/calibration.cal".format(txtinout_dir_), calibration_cal)
    
    if print_:
        print("\n-------------------------------------------------------------------------------------------------------------")
        print(calibration_cal)
        print("-------------------------------------------------------------------------------------------------------------")

def run_in_dir_with_update(txtinout_dir_, executable = "rev52_64rel.exe" , final_line = "Execution successfully completed", running = False):
    """
    changes to directory and runs a program providing updates and returns to previous directory
    """
    current_dir = os.getcwd()
    
    new_dir = txtinout_dir_
    os.chdir(new_dir)
    ended = False
    while True:
        if not running == True:
            running = True
            os.system("START /B " + executable + " > tmp_log_file.txt")
        else:
            try:
                lines = read_from("tmp_log_file.txt")
                if final_line.lower().replace(" ", "") == lines[-1].strip('\n').lower().replace(" ", ""):
                    if not ended == True:
                        ended = True
                        print("\n\t " + lines[-1].strip('\n') + "\n")
                    time.sleep(1)
                    os.remove("tmp_log_file.txt")
                    return 

                sys.stdout.write("\r\t\t\t\t\t\t\t")
                sys.stdout.flush()
                sys.stdout.write("\r\t" + lines[-1].strip('\n'))
                sys.stdout.flush()
            except: 
                pass
    os.chdir(current_dir)

def get_aa_ratios(txtinout_dir_):
    aa_raw = read_from("{0}/waterbal_aa_bsn.txt".format(txtinout_dir_))[2]
    for i in range(0,12):
        aa_raw = aa_raw.replace("  ", " ")
    aa_raw = aa_raw.split(" ")
    precip = float(aa_raw[8])
    # evapotranspiration ratio,       +++++      # percolation ratio,       +++++      # lateral flow ratio,       +++++      # surface runoff ratio is it the difference between lateral flow and yield?
    aa_ratios = ratios()
    aa_ratios.et_r, aa_ratios.pe_r, aa_ratios.la_r, aa_ratios.sr_r = float(aa_raw[15])/precip, float(aa_raw[14])/precip, float(aa_raw[12])/precip, float(aa_raw[13])/precip
    return aa_ratios, precip

def get_obj_ratios(txtinout_dir_):
    obj_raw = read_from("{0}/ls_regions.cal".format(txtinout_dir_))[5]
    for i in range(0,12):
        obj_raw = obj_raw.replace("  ", " ")
    obj_raw = obj_raw.split(" ")
    obj_ratios = ratios()

    obj_ratios.et_r, obj_ratios.pe_r, obj_ratios.la_r, obj_ratios.sr_r = float(obj_raw[5]), float(obj_raw[4]), float(obj_raw[3]), float(obj_raw[2])    
    return obj_ratios

def get_difference(bsn_ratios, obj_ratios, precip, ratio_name):
    if ratio_name == "et_r":
        diff = (obj_ratios.et_r * precip) - (bsn_ratios.et_r * precip)
    if ratio_name == "la_r":
        diff = (obj_ratios.la_r * precip) - (bsn_ratios.la_r * precip)
    if ratio_name == "pe_r":
        diff = (obj_ratios.pe_r * precip) - (bsn_ratios.pe_r * precip)
    if ratio_name == "sr_r":
        diff = (obj_ratios.sr_r * precip) - (bsn_ratios.sr_r * precip)

    return diff

def get_parm_properties(parms_, txtinout_dir_):
    parms_done = []
    ls_parms_raw = read_from("{0}/ls_parms.cal".format(txtinout_dir_))
    ls_parms = []
    for line__ in ls_parms_raw:
        for i in range (0,100):
            line__ = line__.replace("  ", " ")
            line__ = line__.replace("\t", "  ")
            line__ = line__.strip("\n")
        ls_parms.append(line__.split(" "))
    for par in parms_:
        for ls_ine in ls_parms:
            if par.par_name == ls_ine[0]:
                par.u_limit     = float(ls_ine[5])
                par.l_limit     = float(ls_ine[4])
                par.set_bound_l = float(ls_ine[2])
                par.set_bound_u = float(ls_ine[3])
                par.chg_type    = ls_ine[1]

                parms_done.append(par)
    return parms_done

# initialisation
txtinout_dir_ = os.getcwd() + "/txtinout"

cn2 = parameter("cn2", "abschg", "sr_r")
esco = parameter("esco", "abschg", "et_r")
epco = parameter("epco", "abschg", "et_r")
lat_len = parameter("lat_len", "pctchg", "la_r")
k_lo = parameter("k_lo", "abschg", "et_r")
slope = parameter("slope", "abschg", "et_r"    )
tconc = parameter("tconc", "abschg", "et_r")
perco = parameter("perco", "abschg", "pe_r")
cn3_swf = parameter("cn3_swf", "abschg", "sr_r")
dep_imp = parameter("dep_imp", "abschg", "et_r")
revapc = parameter("revapc", "abschg", "et_r")
etco = parameter("etco", "abschg", "et_r")


active_parms = [cn2, esco, lat_len, perco, cn3_swf, epco, dep_imp, tconc] # parameters for soft calibration
active_parms = get_parm_properties(active_parms, txtinout_dir_)           # getting parameter attributes

#creating a dictionary of list for performance
perf_history = {}

for active_par in active_parms:
    perf_history[active_par.par_name] = [active_par.value]

#for parm_ in active_parms:
#    print("{0}{1}{2}{3}{4}{5}".format(str(parm_.par_name).rjust(10), str(parm_.chg_type).rjust(10), str(parm_.set_bound_l).rjust(10), str(parm_.set_bound_u).rjust(10), str(parm_.l_limit).rjust(10), str(parm_.u_limit).rjust(10)))

# run first run of zero parameters
print("\n\t> running SWAT+ to get default run ratios\n")
change_parms(active_parms, None, None, None, txtinout_dir_)
run_in_dir_with_update(txtinout_dir_)
default_ratios, precip_tot = get_aa_ratios(txtinout_dir_)
objective_ratios = get_obj_ratios(txtinout_dir_)

max_iterations = 5
for cal_par in active_parms:
    if (not cal_par.par_name == "cn2") or (not cal_par.par_name == "esco") or (not cal_par.par_name == "epco") or (not cal_par.par_name == "lat_len") or (not cal_par.par_name == "cn3_swf"):
        pass
    diff_history = []
    x_intercept = None
    # calibrate parameter number
    print("\t--------------------------------------------------\n\n\t callibrating {0}".format(cal_par.par_name))
    for i in range(0,max_iterations):

        bsn_ratios, precip_tot = get_aa_ratios(txtinout_dir_)
        
        try:
            if diff_history[-1] == diff_history[-2]:
                cal_par.value = 0
                print("\t> {0} does not appear to be sensitive, value set to {1}".format(cal_par.par_name, cal_par.value))
                break
        except:
            pass
        if x_intercept is None:
            diff_history.append(get_difference(bsn_ratios, objective_ratios, precip_tot, cal_par.ratio_type))
            cal_par.value = (cal_par.set_bound_u - cal_par.value)/2.10
        else:
            if abs(diff_history[-1]) < 20:
                if cal_par.value > cal_par.set_bound_u:
                    cal_par.value = cal_par.set_bound_u
                elif cal_par.value < cal_par.set_bound_l:
                    cal_par.value = cal_par.set_bound_l
                print("\t> {0} value set to {1}".format(cal_par.par_name, cal_par.value))
                break
            elif i >= max_iterations - 1:
                if cal_par.value > cal_par.set_bound_u:
                    cal_par.value = cal_par.set_bound_u
                elif cal_par.value < cal_par.set_bound_l:
                    cal_par.value = cal_par.set_bound_l
                print("\t> {0} value set to {1}".format(cal_par.par_name, cal_par.value))
                break
            else:
                if x_intercept > cal_par.set_bound_u:
                    x_intercept = cal_par.set_bound_u
                elif x_intercept < cal_par.set_bound_l:
                     x_intercept = cal_par.set_bound_l
                cal_par.value = x_intercept
            if cal_par.value == perf_history[cal_par.par_name][-1]:
                print("\t> {0} value set to {1}".format(cal_par.par_name, cal_par.value))
                break
        print("\n\t> iteration {0}: testing parameter value : {1}".format(i + 1, cal_par.value))

        perf_history[cal_par.par_name].append(cal_par.value)      # logging
        change_parms(active_parms, None, None, None, txtinout_dir_)

        run_in_dir_with_update(txtinout_dir_)
        bsn_ratios, precip_tot = get_aa_ratios(txtinout_dir_)
        diff_history.append(get_difference(bsn_ratios, objective_ratios, precip_tot, cal_par.ratio_type))

        pt_1 = point(perf_history[cal_par.par_name][len(perf_history[cal_par.par_name]) - 2], diff_history[len(diff_history) - 2])
        pt_2 = point(perf_history[cal_par.par_name][len(perf_history[cal_par.par_name]) - 1], diff_history[len(diff_history) - 1])

        print("\t> adjustment data\n\t    x = {0}y = {1}\n\t    x = {2}y = {3}".format(str(round(pt_1.x, 4)).ljust(10), str(round(pt_1.y, 4)).ljust(10), str(round(pt_2.x, 4)).ljust(10), str(round(pt_2.y, 4)).ljust(10)))

        x_intercept = get_x_intercept(pt_1, pt_2)

        #print("\t> x_intercept : {0}\n".format(x_intercept))

change_parms(active_parms, None, None, None, txtinout_dir_, print_ = True)
