#!/usr/bin/env xmipp_python
'''
/***************************************************************************
 * Authors:     J.M. de la Rosa Trevin (jmdelarosa@cnb.csic.es)
 *
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/
 '''

###########################################################################
#                                                                         #
#     This script will serve to update, configure and compile             #
#     It should run from the $XMIPP_HOME directory                        #
#                                                                         #
###########################################################################

import os, sys

from subprocess import Popen

################ Classes for a Console based configuration ######################
class ConsoleOptionsTab():
    def __init__(self, master, text, **opts):
        self.name = text
        self.optionsDict = {}
        self.optionsValue = {}
        
    def addOption(self, name, comment, default='', cond=None, wiz=None, browse=False):
        self.optionsDict[name] = (name, comment, default, cond)
        self.optionsValue[name] = default
        
    def setValue(self, name, value):
        self.optionsValue[name] = value
        
    def getValue(self, name):
        return self.optionsValue[name]
        
    def getConfigOptions(self):
        optStr = ""
        for key, comment, default, cond in self.optionsDict.values():
            value = self.optionsValue[key]
            if (cond is None or self.getValue(cond) == 'yes'): 
                optStr += ' %s="%s"' % (key, value)
        return optStr
	
    def addSeparator(self):
        pass

class ConsoleConfigNotebook():
    def __init__(self, options):
        self.tabs = {}
        self.options = options
        
    def addTab(self, text):
        tab = ConsoleOptionsTab(self, text)
        self.tabs[text] =  tab
        return tab
    
    def getConfigOptions(self):
        '''return string with configs settings '''
        return ' '.join([t.getConfigOptions() for t in self.tabs.values()])
    
    def setValue(self, tab, option, value):
        self.tabs[tab].setValue(option, value)
        
    def getValue(self, tab, option):
        return self.tabs[tab].getValue(option)
    
    def notifyRun(self, process):
        self.proc = process


################### Helper functions ####################
def detectJava():
    from protlib_utils import which
    java_home = None
    javac = which('javac')
    if javac:
        from os.path import dirname
        from protlib_filesystem import findRealFile
        java_home = dirname(dirname(findRealFile(javac)))
    return java_home
    
def detectMpi():
    from protlib_filesystem import findFilePath
    inc_dirs = ['/usr/include', '/usr/local/include']
    lib_dirs = ['/usr/lib64', '/usr/lib']
    inc_mpi = findFilePath('mpi.h', *(inc_dirs + lib_dirs))
    if sys.platform  == 'darwin':
        lib_mpi = findFilePath('libmpi.dylib', *lib_dirs)
    else:
        lib_mpi = findFilePath('libmpi.so', *lib_dirs)
    
    return (inc_mpi, lib_mpi)

def detectQt():
    from protlib_filesystem import findFilePath
    from os.path import dirname
    possible_dirs = [s+'/qt3/include' for s in ['/usr/lib64', '/usr/lib', '/usr/share']]
    inc_qt = findFilePath('qt.h', *possible_dirs)
    if inc_qt:
    	return dirname(inc_qt)
    else:
    	return None

def addTabOption(tab, option, comment, default, cond=None, wiz=None, browse=False):
    defaultsDic = globals()
    if defaultsDic.has_key(option):
        value = defaultsDic[option]
        if value in [True, 1, 'True','true', 'Yes', 'yes']:
            default = 'yes'
        elif value in [False, 0, 'False', 'false', 'No', 'no']:
            default = 'no'
        elif isinstance(value, list):
            default = ' '.join(value)
        else:
            default = value
    tab.addOption(option, comment, default, cond, wiz, browse) 
   
''' Following wizards functions will try to detect
some values automatically, and return a list with
errors if can't found the desired files''' 
def wizardMpi(tab_mpi):   
    inc_mpi, lib_mpi = detectMpi()
    errors = ""
    
    if inc_mpi:
        tab_mpi.setValue('MPI_INCLUDE', inc_mpi)
    else: errors = "Header mpi.h not found in include dirs"
    
    if lib_mpi:
        tab_mpi.setValue('MPI_LIBDIR', lib_mpi)
    else: errors += "\nLibrary libmpi.so not found in libraries dirs"
    
    return errors
    
def wizardJava(tab_java):
    java_home = detectJava()
    if java_home:
        tab_java.setValue('JAVA_HOME', java_home)  
        return ""
    return "JAVA_HOME could not be found."  
    
def wizardQt(tab_qt):
    qtdir = detectQt()
    if qtdir:
        tab_qt.setValue('QTDIR', qtdir)  
        return ""
    return "QTDIR could not be found."  

def addTabs(nb):
    tab = nb.addTab("Compiler")
    addTabOption(tab,'CC', 'The C compiler', 'gcc')
    addTabOption(tab,'CXX', 'The C++ compiler', 'g++')
    addTabOption(tab,'LINKERFORPROGRAMS', 'Linker for programs', 'g++')
    addTabOption(tab,'CCFLAGS', 'The C compiler flags', '')
    addTabOption(tab,'CXXFLAGS', 'The C++ compiler flags', '')
    
    tab = nb.addTab("  MPI  ")
    addTabOption(tab,'mpi', 'Build the MPI programs?', 'yes')
    addTabOption(tab,'MPI_CC', 'MPI C compiler', 'mpicc', cond='mpi')
    addTabOption(tab,'MPI_CXX', 'MPI C++ compiler', 'mpiCC', cond='mpi')
    addTabOption(tab,'MPI_LINKERFORPROGRAMS', 'MPI Linker for programs', 'mpiCC', cond='mpi')
    addTabOption(tab,'MPI_INCLUDE', 'MPI headers dir ', '/usr/include', cond='mpi', browse=True, wiz=wizardMpi)
    addTabOption(tab,'MPI_LIBDIR', 'MPI libraries dir ', '/usr/lib', cond='mpi', browse=True)
    addTabOption(tab,'MPI_LIB', 'MPI library', 'mpi', cond='mpi')
    tab_mpi = tab
    
    tab = nb.addTab("Java & QT")
    addTabOption(tab,'java', 'Build the java programs?', 'yes')
    addTabOption(tab,'JAVAC', 'Java compiler', 'javac', cond='java')
    addTabOption(tab,'JAVA_HOME', 'Java installation directory', '', cond='java', wiz=wizardJava, browse=True)
    tab.addSeparator()
    addTabOption(tab,'qt', 'Build the GUI (qt) programs?', 'yes')
    addTabOption(tab,'QTDIR', 'Where is QT installed', '/usr/share/qt3', cond='qt', wiz=wizardQt, browse=True)
    addTabOption(tab,'QT_LIB', 'QT library to use', 'qt-mt', cond='qt', browse=True)
    addTabOption(tab,'QT4', 'Use Qt4 instead of Qt3?', 'no', cond='qt', browse=True)
    tab_gui = tab
    
    tab = nb.addTab("Advanced")
    addTabOption(tab,'debug', 'Build debug version?', 'no')
    addTabOption(tab,'profile', 'Build profile version?', 'no')
    addTabOption(tab,'warn', 'Show warnings?', 'no')
    addTabOption(tab,'fast', 'Fast?', 'no')
    addTabOption(tab,'static', 'Prevent dynamic linking?', 'no')
    addTabOption(tab,'prepend', 'What to prepend to executable names', 'xmipp')
    addTabOption(tab, 'gtest', 'Build tests?', 'no')
    addTabOption(tab, 'cuda', 'Build CUDA support?', 'no')
    addTabOption(tab, 'release', 'Release mode', 'yes')
   

    defaultsDic = globals()
    
    if not defaultsDic.has_key('JAVA_HOME'):
        wizardJava(tab_gui)
    
    if not defaultsDic.has_key('MPI_INCLUDE'):
        wizardMpi(tab_mpi)
        
    if not defaultsDic.has_key('QTDIR'):
        wizardQt(tab_gui)
        
        
def run(notebook):
    
    options = notebook.options
    out = OUTPUT
    procs = options.getNumberOfCpu()
    scons = os.path.join("external", "scons", "scons.py")
    os.environ['JAVA_HOME'] = notebook.getValue('Java & QT', 'JAVA_HOME')
    cmd = ''   
    if out != STDOUT and os.path.exists(out):
        os.remove(out)
    
    if options.hasOption('update'):
        cmd += 'echo "*** RUNNING SVN UPDATE..." >> %(out)s 2>&1\n svn up >> %(out)s 2>&1\n'
    
    if options.hasOption('configure'):        
        opts = notebook.getConfigOptions()
        cmd += 'echo "*** RUNNING SCONS.CONFIGURE..." >> %(out)s 2>&1 \n'
        cmd1 = "xmipp_python %(scons)s mode=configure -j %(procs)s --config=force %(opts)s >> %(out)s 2>&1 " % locals()
        cmd += 'echo "%(cmd1)s" >> %(out)s \n'
        cmd += cmd1 + '\n'
    
    if options.hasOption('compile'):
        opts = ' '.join(options.getOption('compile'))
        cmd += 'echo "*** RUNNING SCONS.COMPILE..." >> %(out)s \n'
        cmd2 = "xmipp_python %(scons)s mode=compile -j %(procs)s  %(opts)s >> %(out)s 2>&1 "% locals()
        cmd += 'echo "%(cmd2)s" >> %(out)s \n'
        cmd += cmd2 + '\n'
    if options.hasOption('install'):
        cmd += ('echo "*** CREATING PROGRAMS DATABASE..." >> %(out)s 2>&1\n xmipp_apropos --update >> %(out)s' % locals())    
        
    proc = Popen(cmd % locals(), shell=True)    
    notebook.notifyRun(proc)   
    
####### Simple parsing of arguments ###########
# Acepted options:
# configure arg1 arg2 ... 
# compile arg1 arg2 ...
# update arg1 arg2 ...    
# clean 
class ArgDict():
    def __init__(self, argv):
        self.options = {}
        self.setOption('default')
        
        for arg in argv:
            if arg in ['configure', 'compile', 'update', 'clean', 'gui', 'install', '-j']:
                self.setOption(arg)
            else:
                self.addArgument(arg)
        
    def hasOption(self, option):
        return self.options.has_key(option)
    
    def setOption(self, option):
        self.arguments = []
        self.options[option] = self.arguments
        
    def getOption(self, option):
        if self.hasOption(option):
            return self.options[option]
        return None
    
    def getNumberOfCpu(self):
        if self.hasOption('-j'):
            return self.getOption('-j')[0]
        return '1'
        
    def setNumberOfCpu(self, cpu):
        self.options['-j'] = [cpu]
        
    def addArgument(self, argument):
        self.arguments.append(argument)
    
    def getNumberOfOptions(self):
        return len(self.options)

import sys
options = ArgDict(sys.argv)
#
#import pprint
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(options.options)    


# Output file
OUTPUT = 'build/scons_output.log'
STDOUT = '/dev/stdout'
if os.path.exists(OUTPUT):
    os.remove(OUTPUT)
# TRY TO READ CONFIG FILE
CONFIG = '.xmipp_scons.options'

if os.path.exists(CONFIG):
    for line in open(CONFIG):
        exec(line) # Take options from options file, be carefull with exec

if options.hasOption('configure'):
    for arg in options.getOption('configure'):
        parts = arg.split('=')
        if len(parts) == 2:
            assign = '%s = "%s"' % (parts[0], parts[1])
            exec(assign) # Take options from command line, override options file, be carefull with exec
    
GUI = options.hasOption('gui')
# Check if Tkinter is available
if GUI:    
    try:
        import Tkinter
        from compile_gui import createGUINotebook
        nb = createGUINotebook(OUTPUT, options, addTabs, run)
        exit(0)
    except Exception, e:
        print '-'*60
        print "*** Could not create GUI. Error: ", e
        import traceback
        traceback.print_exc(file=sys.stderr)
        print '-'*60
        answer = raw_input("Do you want to proceed from command line? [Y/n]:")
        if len(answer) and answer.lower() != 'y':
            exit(0)

# Run configuration and compile from command line
nb = ConsoleConfigNotebook(options)
addTabs(nb)
OUTPUT = STDOUT
run(nb)
nb.proc.wait()
if nb.proc.returncode != 0:
    print "Errors on Xmipp compilation, see '%s' for more details" % OUTPUT
elif options.hasOption('compile'):
    print "Xmipp has been successfully compiled"
    if options.hasOption('install'):
        print "INSTALLATION FINISHED!!!"
        print "Include file .xmipp.bashrc or .xmipp.csh to your startup shell file"
elif options.getNumberOfOptions() == 1: # Script name is passed as argument, so at least is 1
    print "Xmipp has successfully remained equal"
        
        
