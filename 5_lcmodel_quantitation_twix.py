__author__ = 'kanaan' 'July 3 2015'


import os
import subprocess
import shutil
from variables.subject_list import *
from utilities.utils import mkdir_path


def run_JN_frequency_and_phase_drift_correction(population, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- Running Freuquency and Phase Drift Correction for  subject %s_%s' %(count,subject, workspace_dir[-10:-9])
        print '.'

        # inputs
        twix_dir = os.path.join(workspace_dir, subject, 'svs_TWIX')

        print 'ACC: Running Spectral Registration at 1.8ppm with 0,0,3.75,0 Phase drift correction'
        ### ACC spectral registration at at  1.8 PPM
        acc_dir = os.path.join(twix_dir, 'ACC')
        os.chdir(acc_dir)
        preproc_acc = ['matlab',  '-nodesktop', '-nosplash', '-noFigureWindows', '-r "run_pressproc_LimitedRange(\'ACC\') ; quit;"']
        subprocess.call(preproc_acc)

        print 'THA: Running Spectral Registration at 4.2ppm with 0,0,3.75,0 Phase drift correction'
        ### THA spectral registration at at  4.2 PPM
        tha_dir = os.path.join(twix_dir, 'THA')
        os.chdir(tha_dir)
        preproc_tha = ['matlab',  '-nodesktop', '-nosplash', '-noFigureWindows', '-r "run_pressproc_WaterRange(\'THA\') ; quit;"']
        subprocess.call(preproc_tha)

        print 'STR: Running Spectral Registration at 4.2ppm with 0,0,3.75,0 Phase drift correction'
        # ### STR spectral registration at at  4.2 PPM
        str_dir = os.path.join(twix_dir, 'STR')
        os.chdir(str_dir)
        preproc_str = ['matlab',  '-nodesktop', '-nosplash', '-noFigureWindows', '-r "run_pressproc_WaterRange(\'STR\') ; quit;"']
        subprocess.call(preproc_str)


        def run_lcmodel_raw(voxel_name):
            print ''
            print 'PROCESSING SPECTRA WITH LCMODEL FOR %s'%voxel_name

            mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_twix',  '%s'%voxel_name, 'met'))
            mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_twix', '%s'%voxel_name, 'h2o'))
            lcmodel_dir = os.path.join(workspace_dir, subject, 'lcmodel_twix', '%s'%voxel_name)


            shutil.copy(os.path.join(twix_dir, '%s'%voxel_name, '%s'%voxel_name, '%s_lcm'%voxel_name),
                        os.path.join(lcmodel_dir, 'met', 'RAW'))

            shutil.copy(os.path.join(twix_dir, '%s'%voxel_name, '%s_w'%voxel_name, '%s_w_lcm'%voxel_name),
                        os.path.join(lcmodel_dir, 'h2o', 'RAW'))

            met = os.path.join(lcmodel_dir, 'met', 'RAW')
            h2o = os.path.join(lcmodel_dir, 'h2o', 'RAW')

            # twix parameters
            nunfil = 2078
            hzpppm = 123.242398
            echot  = 30.0
            deltat = 0.000417

            print 'Processing Spectra'
            print '...building control file'
            file = open(os.path.join(lcmodel_dir, 'control'), "w")
            file.write(" $LCMODL\n")
            file.write(" title= '%s_%s_%s' \n" %(subject, workspace_dir[-10:-9], voxel_name))
            file.write(" srcraw= '%s' \n" %met)
            file.write(" srch2o= '%s' \n" %h2o)
            file.write(" savdir= '%s' \n" %lcmodel_dir)
            file.write(" ppmst= 4.0 \n")
            file.write(" ppmend= 0.3\n")
            file.write(" nunfil= %s\n"%nunfil)
            file.write(" ltable= 7\n")
            file.write(" lps= 8\n")
            file.write(" lprint= 6\n")
            file.write(" lcsv= 11\n")
            file.write(" lcoraw= 10\n")
            file.write(" lcoord= 9\n")
            file.write(" hzpppm= %s\n"%hzpppm)
            file.write(" filtab= '%s/table'\n" %lcmodel_dir)
            file.write(" filraw= '%s/met/RAW'\n" %lcmodel_dir)
            file.write(" filps= '%s/ps'\n" %lcmodel_dir)
            file.write(" filpri= '%s/print'\n" %lcmodel_dir)
            file.write(" filh2o= '%s/h2o/RAW'\n" %lcmodel_dir)
            file.write(" filcsv= '%s/spreadsheet.csv'\n" %lcmodel_dir)
            file.write(" filcor= '%s/coraw'\n" %lcmodel_dir)
            file.write(" filcoo= '%s/coord'\n" %lcmodel_dir)
            file.write(" filbas= '/home/raid3/kanaan/.lcmodel/basis-sets/press_te30_3t_01a.basis'\n")
            file.write(" echot= %s \n" %echot)
            file.write(" dows= T \n")
            #file.write(" DEGPPM =0 \n")
            file.write(" doecc= T\n")
            file.write(" deltat= %s\n"%deltat)
            file.write(" $END\n")
            file.close()

            lcm_command = ['/bin/sh','/home/raid3/kanaan/.lcmodel/execution-scripts/standardA4pdfv3','%s' %lcmodel_dir,'19','%s' %lcmodel_dir,'%s' %lcmodel_dir]
            print '... running execution script'
            print subprocess.list2cmdline(lcm_command)
            subprocess.call(lcm_command)

            reader = open(os.path.join(lcmodel_dir, 'table'), 'r')
            for line in reader:
                if 'FWHM' in line:
                    fwhm = float(line[9:14])
                    snrx  = line[29:31]

                    fwhm_hz = fwhm * 123.24
                    file = open(os.path.join(lcmodel_dir, 'snr.txt'), "w")
                    file.write('%s, %s, %s' %(fwhm,fwhm_hz, snrx))
                    file.close()


        ##########################################################################################
        #ACC
        if os.path.isfile(os.path.join(workspace_dir, subject, 'lcmodel_twix', 'ACC', 'ps.pdf')):
            print 'ACC already processed'
        else:
            run_lcmodel_raw('ACC')

        #THA
        if os.path.isfile(os.path.join(workspace_dir, subject, 'lcmodel_twix', 'THA', 'ps.pdf')):
            print 'THA already processed'
        else:
            run_lcmodel_raw('THA')

        #STR
        if os.path.isfile(os.path.join(workspace_dir, subject, 'lcmodel_twix', 'STR', 'ps.pdf')):
            print 'STR already processed'
        else:
            run_lcmodel_raw('STR')
        ##########################################################################################

if __name__ == "__main__":
    run_JN_frequency_and_phase_drift_correction(test_subject2, workspace_patients_a)

