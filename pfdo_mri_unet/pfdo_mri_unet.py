# Turn off all logging for modules in this libary.
import logging
logging.disable(logging.CRITICAL)

# System imports
import      os
import      json
import      pathlib
from        argparse            import  Namespace

# Project specific imports
import      pfmisc
from        pfmisc._colors      import  Colors
from        pfmisc              import  other
from        pfmisc              import  error

from        mri_unet     import  mri_unet
import      pfdo

import      pudb
import      pftree

class pfdo_mri_unet(pfdo.pfdo):
    """

    A class for navigating down a dir tree and providing
    hooks for some (subclass) analysis

    """

    _dictErr = {
        'outputDirFail'   : {
            'action'        : 'trying to check on the output directory, ',
            'error'         : 'directory not specified. This is a *required* input.',
            'exitCode'      : 1},
        'outputFileExists'   : {
            'action'        : 'attempting to write an output file, ',
            'error'         : 'it seems a file already exists. Please run with --overwrite to force overwrite.',
            'exitCode'      : 2}
        }


    def declare_selfvars(self):
        """
        A block to declare self variables
        """

        #
        # Object desc block
        #
        self.str_desc                   = ''
        self.__name__                   = "pfdo_mri_unet"

    def __init__(self, *args, **kwargs):
        """
        Constructor for pfdo_mri_unet.

        This basically just calls the parent constructor and
        adds some child-specific data.
        """

        super().__init__(*args, **kwargs)

        pfdo_mri_unet.declare_selfvars(self)

    def inputReadCallback(self, *args, **kwargs):
        """
        This method does not actually read in any files, but
        exists to preserve the list of files associated with a
        given input directory. 

        By preserving and returning this file list, the next
        callback function in this pipeline is able to receive an
        input path and a list of files in that path.
        """
        str_path        : str       = ''
        l_fileProbed    : list      = []
        b_status        : bool      = True
        filesProbed     : int       = 0
        str_outputWorkingDir: str       = ""

        if len(args):
            at_data         = args[0]
            str_path        = at_data[0]
            l_fileProbed    = at_data[1]

        # Need to create the output dir appropriately here!
        str_outputWorkingDir    = str_path.replace(
                                        self.args['inputDir'],
                                        self.args['outputDir']
        )
        self.dp.qprint("mkdir %s" % str_outputWorkingDir,
                        level = 3)
        other.mkdir(str_outputWorkingDir)

        if not len(l_fileProbed): b_status = False

        return {
            'status':           b_status,
            'l_fileProbed':     l_fileProbed,
            'str_path':         str_path,
            'filesProbed':      filesProbed
        }

    def inputAnalyzeCallback(self, *args, **kwargs):
        """
        Callback stub for doing actual work. Since the `mri_unet`
        is a mostly stand-apart module, the inputRead and outputWrite
        callbacks are not applicable here, since calling the
        `mri_unet` module appropriately reads an input and saves
        an output.
        """

        def l_fileToAnalyze_determine(l_fileProbed):
            """
            Return the list of files to process, based on l_fileProbed
            and self.args['analyzeFileIndex']
            """

            def middleIndex_find(l_lst):
                """
                Return the middle index in a list.
                If list has no length, return None.
                """
                middleIndex     = None
                if len(l_lst):
                    if len(l_lst) == 1:
                        middleIndex = 0
                    else:
                        middleIndex = round(len(l_lst)/2+0.01)
                return middleIndex

            def nIndex_find(l_lst, str_index):
                """
                For a string index, say "2", return the index at l_lst[2].
                If index is out of bounds return None.
                """
                index:  int = 0
                try:
                    index   = int(str_index)
                    if len(l_lst):
                        if index >= -1 and index < len(l_lst):
                            return index
                except:
                    pass
                return None

            l_fileToAnalyze:    list    = []
            if len(l_fileProbed):
                if self.args['analyzeFileIndex'] == 'f': l_fileToAnalyze.append(l_fileProbed[0])
                if self.args['analyzeFileIndex'] == 'l': l_fileToAnalyze.append(l_fileProbed[-1])
                if self.args['analyzeFileIndex'] == 'm':
                    if middleIndex_find(l_fileProbed) >= 0:
                        self.dp.qprint(l_fileProbed, level = 5)
                        l_fileToAnalyze.append(l_fileProbed[middleIndex_find(l_fileProbed)])
                nIndex  = nIndex_find(l_fileProbed, self.args['analyzeFileIndex'])
                if nIndex:
                    if nIndex == -1:
                        l_fileToAnalyze = l_fileProbed
                    else:
                        l_fileToAnalyze.append(nIndex)
            return l_fileToAnalyze

        b_status            : bool  = False
        l_fileProbed        : list  = []
        d_inputReadCallback : dict  = {}
        d_convert           : dict  = {}
        

        for k, v in kwargs.items():
            if k == 'path':         str_path    = v

        if len(args):
            at_data             = args[0]
            str_path            = at_data[0]
            d_inputReadCallback = at_data[1]
            l_fileProbed        = d_inputReadCallback['l_fileProbed']

        # pudb.set_trace()
        mri_unet_args                  = self.args.copy()

        for str_file in l_fileToAnalyze_determine(l_fileProbed):
            mri_unet_args['inputDir']      = str_path
            mri_unet_args['outputDir']     = str_path.replace(
                                                self.args['inputDir'], 
                                                self.args['outputDir']
                                            )

            mri_unet_args['outputDir'] = os.path.join(mri_unet_args['outputDir'], str_file)
            os.mkdir(mri_unet_args['outputDir'])

           

            mri_unet_ns    = Namespace(**mri_unet_args)
            unet    = mri_unet.object_factoryCreate(mri_unet_ns).C_convert

            # At time of dev, the `unet.run()` does not return anything.
            unet.run()

        return {
            'status':           b_status,
            'str_path':         str_path,
            'l_fileProbed':     l_fileProbed,
            'd_convert':        d_convert
        }

    def filelist_prune(self, at_data, *args, **kwargs) -> dict:
        """
        Given a list of files, possibly prune list by
        interal self.args['filter'].
        """

        # pudb.set_trace()

        b_status    : bool      = True
        l_file      : list      = []
        str_path    : str       = at_data[0]
        al_file     : list      = at_data[1]

        if len(self.args['filter']):
            al_file = [x for x in al_file if self.args['filter'] in x]

        if len(al_file):
            al_file.sort()
            l_file      = al_file
            b_status    = True
        else:
            self.dp.qprint( "No valid files to analyze found in path %s!" %
                            str_path, comms = 'warn', level = 5)
            l_file      = None
            b_status    = False
        return {
            'status':   b_status,
            'l_file':   l_file
        }

    def mri_unet(self) -> dict:
        """
        The main entry point for connecting methods of this class
        to the appropriate callbacks of the `pftree.tree_process()`.
        Note that the return json of each callback is available to
        the next callback in the queue as the second tuple value in
        the first argument passed to the callback.
        """
        d_mri_unet     : dict    = {}

        other.mkdir(self.args['outputDir'])
        d_mri_unet     = self.pf_tree.tree_process(
                            inputReadCallback       = self.inputReadCallback,
                            analysisCallback        = self.inputAnalyzeCallback,
                            outputWriteCallback     = None,
                            persistAnalysisResults  = False
        )
        return d_mri_unet

    def run(self, *args, **kwargs) -> dict:
        """
        This base run method should be called by any descendent classes
        since this contains the calls to the first `pftree` prove as well
        as any (overloaded) file filtering.
        """

        # pudb.set_trace()
        b_status        : bool  = False
        b_timerStart    : bool  = False
        d_pfdo          : dict  = {}
        d_mri_unet     : dict  = {}

        self.dp.qprint(
                "Starting pfdo_mri_unet run... (please be patient while running)",
                level = 1
        )

        for k, v in kwargs.items():
            if k == 'timerStart':   b_timerStart    = bool(v)

        if b_timerStart:    other.tic()

        d_pfdo          = super().run(
                            JSONprint   = False,
                            timerStart  = False
        )

        if d_pfdo['status']:
            d_mri_unet     = self.mri_unet()

        d_ret = {
            'status':           b_status,
            'd_pfdo':           d_pfdo,
            'd_mri_unet':      d_mri_unet,
            'runTime':          other.toc()
        }

        if self.args['json']:
            self.ret_dump(d_ret, **kwargs)
        else:
            self.dp.qprint('Returning from pfdo_mri_unet class run...', level = 1)

        return d_ret
