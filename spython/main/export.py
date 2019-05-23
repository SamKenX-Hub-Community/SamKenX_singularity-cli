
# Copyright (C) 2017-2019 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


from spython.logger import bot
from spython.utils import stream_command
import re
import os


def export(self,
           image_path,
           pipe=False,
           output_file=None,
           command=None,
           sudo=False):
    '''export will export an image, sudo must be used. If we have Singularity
       versions after 3, export is replaced with building into a sandbox.

       Parameters
       ==========
       image_path: full path to image
       pipe: export to pipe and not file (default, False)
       output_file: if pipe=False, export tar to this file. If not specified, 
       will generate temporary directory.
    '''
    from spython.utils import check_install
    check_install()

    # If not version 3, run deprecated command
    if 'version 3' not in self.version():
        return _export(image_path=image_path,
                       pipe=pipe,
                       output_file=output_file,
                       command=command)

    if output_file == None:
        output_file = self._get_filename(image_path, 'sandbox')

    # Otherwise, we run a build
    bot.warning('Export is not supported for Singularity 3.x. Building to sandbox instead.')
    return self.build(recipe=image_path,
                      image=output_file,
                      sandbox=True,
                      sudo=sudo)


def _export(self,
           image_path,
           pipe=False,
           output_file=None,
           command=None):
    ''' the older deprecated function, running export for previous
               versions of Singularity that support it

           USAGE: singularity [...] export [export options...] <container path>
           Export will dump a tar stream of the container image contents to standard
           out (stdout). 
           note: This command must be executed as root.
           EXPORT OPTIONS:
               -f/--file       Output to a file instead of a pipe
                  --command    Replace the tar command (DEFAULT: 'tar cf - .')
           EXAMPLES:
               $ sudo singularity export /tmp/Debian.img > /tmp/Debian.tar
               $ sudo singularity export /tmp/Debian.img | gzip -9 > /tmp/Debian.tar.gz
               $ sudo singularity export -f Debian.tar /tmp/Debian.img

    '''
    sudo = True
    cmd = self._init_command('export')
    
    # If the user has specified export to pipe, we don't need a file
    if pipe == True:
        cmd.append(image_path)
    else:
        _,tmptar = tempfile.mkstemp(suffix=".tar")
        os.remove(tmptar)
        cmd = cmd + ["-f",tmptar,image_path]
        self.run_command(cmd,sudo=sudo)

        # Was there an error?            
        if not os.path.exists(tmptar):
            print('Error generating image tar')
            return None

        # if user has specified output file, move it there, return path
        if output_file != None:
            shutil.copyfile(tmptar, output_file)
            return output_file
        else:
            return tmptar

    # Otherwise, return output of pipe    
    return self.run_command(cmd, sudo=sudo)
