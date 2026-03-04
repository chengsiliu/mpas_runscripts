#!/bin/bash
#SBATCH --partition=PARTION
#SBATCH -J JOBNAME
#SBATCH --ntasks=NOPART CPUSPEC
#SBATCH -t 00:10:00
#SBATCH --output=WRKDIR/rediag_%a_%j.log
ACCTSTR
EXCLSTR

time1=$(date '+%s')
printf "Job Started: %(%a %b %d %H:%M:%S %Z %Y)T. Job Id: %s, Array Task: %s\n\n" $time1 $SLURM_JOBID $SLURM_ARRAY_TASK_ID

if [[ "MACHINE" == "Jet" || "MACHINE" == "Hercules" || "MACHINE" == "Ursa" ]]; then
    source /etc/profile.d/modules.sh
    module purge
    module use MPASDIR/modulefiles
    module load MODULE
else
    source ROOTDIR/modules/MODULE
fi

nnode=NNODES
if (( NOPART % nnode == 0 )); then
    ncores=$(( NOPART/nnode ))
fi

ulimit -s unlimited

mem=${SLURM_ARRAY_TASK_ID}
memstr=$(printf "%02d" $mem)

cd WRKDIR/fcst_${memstr}

touch running.rediag_$memstr
rm -rf error.rediag_$memstr

sed -i -e "/config_pio_num_iotasks/s/=.*/= $nnode/g;/config_pio_stride/s/=.*/= $ncores/" namelist.atmosphere

RUNMPCMD -n NOPART EXEDIR/atmosphere_model

istatus=$?
if [[ $istatus -eq 0 ]]; then
    touch done.rediag_$memstr
else
    touch error.rediag_$memstr
fi

rm -rf running.rediag_$memstr

time2=$(date '+%s')
diff=$((time2-time1))
printf "\nJob Ended: %(%a %b %d %H:%M:%S %Z %Y)T. Runtime: %s.\n" $time2 $(date -d@$diff -u +%H:%M:%S)
