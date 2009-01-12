#!/usr/bin/python

# NetFdiff is released under the GNU GENERAL PUBLIC LICENSE v3
# 
# BUGS
# focus of wheel of the mouse (windows)
# upload recent files also takes .files (beginning with a dot)
#    but they are hidden. so this is not coherent.

# TODO list
# several languages
# add a search bar or filter bar.
# configuration with dialog box
# create and upload remote php script
# optimize creation of remote folders: do not create when not necessary
# #

import os
import urllib2
import traceback
from Tkinter import *
import tkMessageBox
import ftplib
import ConfigParser
import re
import locale
import md5

# get the locale
lang, encoding = locale.getdefaultlocale()
lang = lang[0:2]
# supported languages are 'en' (default) and 'fr'.
MESSAGES = [ [ 'en', 'fr' ], 

[ 'Validate', 'Valider' ],
[ 'Cancel', 'Annuler' ],
[ 'Cancelled.', 'Annulation.' ],
[ 'Error:', 'Erreur :' ],
[ 'FTP: Connecting...', 'Connexion FTP...' ],
[ 'FTP: Cannot connect:', 'Echec de la connexion FTP :' ],
[ 'Directory %s ignored for download', 'Download inoperant sur les dossiers (%s)' ],
[ 'Creating directory %s...', 'Creation du dossier %s...' ],
[ 'Error during upload of %s:', "Erreur lors de l'upload de %s :" ],
[ 'Remote Web Site', 'Sur le site web' ],
[ 'Local Files', 'Fichiers Locaux' ],
[ 'Rename', 'Renommer' ],
[ 'Delete', 'Supprimer' ],
[ 'Quit', 'Quitter' ],
[ 'View', 'Affichage' ],
[ 'Overwrite a file', 'Ecraser un fichier' ],

[   'Download selected remote files\nto local directory',
    'Transferer les fichiers depuis le site web\nvers le dossier local' ],

[   'Upload selected files to the web site',
    'Transferer les fichiers locaux vers le site web' ],

[   'Upload Recent Files >>',
    'Upload Fichiers Recents >>' ],

[   'Hide identical files',
    'Cacher les fichiers identiques' ],

[   'Hide directories',
    'Cacher les dossiers' ],

[   'Update Display',
    'Actualiser' ],

[   'Create and upload PHP find-file script',
    "Creer et uploader le scipt PHP 'find-file'" ],

[   'Creating local file %s',
    'Creation du fichier %s' ],

[   'Cannot delete file:',
    'Echec de la suppression de fichier :' ],

[   'Are you sure you want to delete this file ?\n%s',
    'Supprimer le fichier ?\n%s' ],

[   'Delete a file',
    'Supprimer un fichier' ],

[   'Cannot delete more than 1 file at a time.',
    "Impossible de supprimer plus d'1 fichier a la fois." ],

[   'Rename file:\n%s\nNew name:\n',
    'Renommer le fichier :\n%s\nNouveau nom:\n' ],

[   'Cannot rename more than 1 file at a time.',
    "Impossible de renommer plus d'1 fichier a la fois." ],

[   'Local files: %d',
    'Fichiers locaux : %d' ],

[   'Remote files: %d',
    'Fichiers distants : %d' ],

[   'Cannot read remote files:',
    'Echec lors de la lecture des fichiers distants :' ],

[   'Reading files... (%s)',
    'Lecture des fichiers distants... (%s)' ],

[   'You must select at least 1 file for downloading.',
    'Vous devez selectionner un ou plusieurs fichiers du site web pour pouvoir le(s) downloader.' ],

[   'No recent file.',
    'Pas de fichier recent.' ],

[   'You must select at least 1 file for uploading.',
    'Vous devez selectionner un ou plusieurs fichiers locaux pour pouvoir les uploader.' ],

[   'Initialising timestamp file : %s',
    'Initialisation du fichier de date : %s' ],

[   'Are you sure you want to overwrite this file ?\n%s',
    'Ecraser ce fichier ?\n%s' ],

[   'No change on local file %s.',
    'Pas de modification du fichier %s.' ],

[   'Initialise timestamp',
    'Initialiser le fichier de date' ],

[   'Update the 2 lists:\n  - local files\n  - remote files\n(this action makes a connection to the web site)',
    'Actualiser les 2 listes :\n  - la liste des fichiers locaux\n  - la liste des fichiers distants\n(cette action se connecte au site distant)' ],

[   'Upload the recent local files\n(in red) to the web site',
    'Transferer les fichiers locaux recents\n(indiques en rouge) vers le site web' ],

[   'Display only recent files',
    'Afficher seulement les fichiers recents' ],

[   'Loading configuration file %s.',
    'Chargement du fichier de configuration %s.' ],

[   'Error: configuration file %s has no section!',
    "Erreur: le fichier de configuration %s n'a aucune section !" ],

[   "Using section '%s'.",
    "Lecture de la section '%s'." ],

[   "Click on 'Update' in order to display the lists.",
    "Clicker sur 'Actualiser' pour afficher les listes." ],

[   '',
    '' ],

[   '',
    '' ],

]

def gettext(message) :
    if lang == 'en' :
        # default language, no translation
        return message

    # else
    # find out which column is related to the language
    listOfLanguagues = MESSAGES[0]
    try :
        i = listOfLanguagues.index(lang)
    except :
        # lang not found in MESSAGES
        # use default language (no translation)
        return message

    for msg in MESSAGES :
        if msg[0] == message :
            # get the translation
            return msg[i]
    
    # no translation found
    return message

_ = gettext

def log(message, tag=None) :
    "Log a message in the console."
    console.text.configure(state=NORMAL)
    console.text.insert(END, message+'\n', tag)
    console.text.configure(state=DISABLED)
    console.text.see(END)
    console.text.update()

def logCommand(message) :
    "Log a message into the console with a special style."
    log(message, 'command')

def logError(message) :
    "Log a message into the console with a special style."
    log(message, 'error')

class EntryDialog :
    def __init__(self, parent, msg, defaultValue,  **options) :
        self.root = Toplevel(parent, options)
        messageLabel = Label(self.root, text=msg)
        messageLabel.config(justify=LEFT, anchor=NW)
        messageLabel.pack(side=TOP, expand=1, fill=X)

        self.entry = Entry(self.root, width=40)
        self.entry.insert(0, defaultValue)
        self.entry.pack(side=TOP, expand=1, fill=X)
        self.value = ''

        buttonCancel = Button(self.root, text=_('Cancel'), command=self.cancel)
        buttonCancel.pack(side=RIGHT)
        buttonOk = Button(self.root, text=_('Validate'), command=self.validate)
        buttonOk.pack(side=RIGHT)

        self.root.bind('<Return>', self.validate)


    def cancel(self) :
        self.value = ''
        self.root.quit()

    def validate(self, event = None) :
        self.value = self.entry.get()
        self.root.quit()
        

    def go(self) :
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        self.root.destroy()
        return self.value


class HelpBalloon(Label) :
    currentTimer = None
    def __init__(self, master, **options) :
        Label.__init__(self, root, options)

        self.config(relief=RIDGE, background='#ffff57')
        self.config(justify=LEFT, padx=3, pady=3)
        master.bind("<Enter>", self.enter)
        master.bind("<Leave>", self.leave)

    def enter(self, event) :
        self.currentTimer = self.after(1000, self.displayBalloon, event)

    def leave(self, event) :
        self.after_cancel(self.currentTimer)
        self.place_forget()

    def displayBalloon(self, event) :
        x_mouse = root.winfo_pointerx()-root.winfo_rootx()+8
        y_mouse = root.winfo_pointery()-root.winfo_rooty()+3
        self.place(x=x_mouse, y=y_mouse)
        self.lift()
        
class Ftp :
    errorOccurred = False # initialised at connection, and set to true if an error occurs

    def rename(old, new) :
        # don't use os.path.join() here, as
        # the FTP serveur uses '/' and not '\'
        old = config['ftp-remote-dir'] + '/' + old
        new = config['ftp-remote-dir'] + '/' + new
        logCommand('FTP: rename(%s, %s)' % (old, new))
        try :
            ftp = Ftp.connect()
            ftp.rename(old, new)
            ftp.quit()
            log('OK.')
        except :
            logError(_('Error:'))
            logError(traceback.format_exc())
            Ftp.errorOccurred = True

    def delete(filename) :
        # don't use os.path.join() here, as
        # the FTP serveur uses '/' and not '\'
        filename = config['ftp-remote-dir'] + '/' + filename
        logCommand('FTP: delete(%s)' % (filename))
        try :
            ftp = Ftp.connect()
            if filename[-1] == '/' :
                # it is a directory
                ftp.rmd(filename)
            else :
                # regular file
                ftp.delete(filename)

            ftp.quit()
            log('OK.')
        except :
            logError(_('Cannot delete file:'))
            logError(traceback.format_exc())
            Ftp.errorOccurred = True
    
    def connect() :
        log(_('FTP: Connecting...'))
        try :
            ftpHandler = ftplib.FTP(config['ftp-server'])
            ftpHandler.login(config['ftp-user'], config['ftp-password'])
            Ftp.errorOccurred = False
        except :
            logError(_('FTP: Cannot connect:'))
            logError(traceback.format_exc())
            ftpHandler = None
            Ftp.errorOccurred = True

        return ftpHandler

    def download(file, ftpHandler = None) :

        if file[-1] == '/' :
            # it is a directory
            log(_('Directory %s ignored for download') % file) 

        else :
            # don't use os.path.join() here, as
            # the FTP serveur uses '/' and not '\'
            remoteFile = config['ftp-remote-dir'] + '/' + file
            localFile = os.path.join( config['local-root-dir'], file)
            logCommand('FTP: download(%s) -> %s' % (remoteFile, localFile))
            try :
                if ftpHandler is None :
                    ftpHandler = Ftp.connect()
                    doQuit = True
                else :
                    doQuit = False
    
                # prepare local file
                localDestinationDir = os.path.dirname(localFile)
                if not os.path.exists(localDestinationDir) :
                    os.makedirs(localDestinationDir)
                localStorage = open(localFile, 'wb')

                # proceed with the download
                ftpHandler.retrbinary('RETR ' + remoteFile, localStorage.write)
                localStorage.close()
    
                if doQuit :
                    ftpHandler.quit()
                log('OK.')
            except :
                logError(_('Error:'))
                logError(traceback.format_exc())
                Ftp.errorOccurred = True

    def mkdir(dir, ftpHandler = None) :
        "Make a remote directory, with all needed intermediate directories."
        if dir == '' :
            return

        if ftpHandler is None :
            ftpHandler = Ftp.connect()
            doQuit = True
        else :
            doQuit = False
        # remove possible '.' (like in DIR1/./DIR2)
        remoteDirectory = os.path.normpath(dir)

        # create all necessary intermediate directories
        dirList = remoteDirectory.split(os.path.sep)
        while len(dirList) > 0 :
            dir = dirList.pop(0)
            # create the directory
            log(_('Creating directory %s...') % dir)
            try :
                ftpHandler.mkd(dir)
            except :
                # ignore any error as we have not checked 
                # if the dir existed before creating it
                pass
            
            # concatenate with next element, if any.
            if len(dirList) > 0 :
                dirList[0] = dir + '/' + dirList[0]

        if doQuit :
            ftpHandler.quit()

    def upload(file, ftpHandler = None) :

        if file[-1] == '/' :
            # it is a directory
            # ignore
            return

        else :
            # don't use os.path.join() here, as
            # the FTP serveur uses '/' and not '\'
            if config['ftp-remote-dir'] != '' :
                remoteFile = config['ftp-remote-dir'] + '/' + file
            else :
                remoteFile = file

            localFile = os.path.join(config['local-root-dir'], file)
            logCommand('FTP: upload(%s) -> %s' % (localFile, remoteFile))
            try :
                if ftpHandler is None :
                    ftpHandler = Ftp.connect()
                    doQuit = True
                else :
                    doQuit = False
    
                # prepare directories for remote file
                remoteDirectory = os.path.dirname(remoteFile)
                Ftp.mkdir(remoteDirectory, ftpHandler)


                # proceed with the upload
                ftpHandler.storbinary('STOR ' + remoteFile, open(localFile, 'rb'))
    
                if doQuit :
                    ftpHandler.quit()
                log('OK.')
            except :
                logError(_("Erreur lors de l'upload de %s :") % localFile)
                logError(traceback.format_exc())
                Ftp.errorOccurred = True
        
    mkdir = staticmethod(mkdir)
    connect = staticmethod(connect)
    download = staticmethod(download)
    upload = staticmethod(upload)
    rename = staticmethod(rename)
    delete = staticmethod(delete)

        

class List(Frame) :
    LIST_WIDTH = 70
    LIST_HEIGHT = 20
    def __init__(self, parent, remoteOrLocal, **options) :
        Frame.__init__(self, parent, options)

        # title
        if remoteOrLocal == 'remote' :
            name = _('Remote Web Site')
            self.isRemote = True
        else :
            name = _('Local Files')
            self.isRemote = False

        self.title = Label(self, text=name)
        self.title.pack(side=TOP)

        # listbox
        self.list = Listbox(self, selectmode=EXTENDED)
        self.list.config(width=self.LIST_WIDTH, height=self.LIST_HEIGHT)
        self.list.pack(side=TOP, fill=BOTH, expand=1)

        # contextual menu for remote files
        if self.isRemote :
            self.list.bind("<Button-3>", self.rightClick)

            # contextual menu
            self.contextualMenu = Menu(self, tearoff=0)
            self.contextualMenu.add_command(label=_('Rename'), command=self.renameFile)
            self.contextualMenu.add_command(label=_('Delete'), command=self.deleteFile)

    def deleteFile(self) :
        "Delete the selected file."
        currentSelection = self.list.curselection()
        if len(currentSelection) == 1 :
            currentFile = self.list.get(self.list.curselection()[0])

            msg = _('Are you sure you want to delete this file ?\n%s') % currentFile
            confirm = tkMessageBox.askokcancel(_('Delete a file'), msg, default=tkMessageBox.CANCEL)
            if confirm :
                Ftp.delete(currentFile)
                if not Ftp.errorOccurred :
                    # update the display
                    diffFrame.readRemoteFiles()
                    diffFrame.updateDisplay()
                    
            else :
                log(_('Cancelled.'))


        else :
            # renaming several files is not supported
            log(_('Cannot delete more than 1 file at a time.'))

    def renameFile(self) :
        currentSelection = self.list.curselection()
        if len(currentSelection) == 1 :
            currentFile = self.list.get(self.list.curselection()[0])

            msg = _('Rename file:\n%s\nNew name:\n') % currentFile
            x = EntryDialog(root, msg, currentFile)
            new = x.go()
            if new != '' and currentFile != new :
                Ftp.rename(currentFile, new.encode('iso-8859-1'))

                # update the display
                diffFrame.readRemoteFiles()
                diffFrame.updateDisplay()
            else :
                log('Cancelled.')
        else :
            # renaming several files is not supported
            log(_('Cannot rename more than 1 file at a time.'))


    def rightClick(self, event) :
        "Pop-up a contextual menu."
        list = event.widget
        index = list.nearest(event.y)
        currentItem = list.get(index)

        if currentItem != '' :
            list.select_clear(0, list.size())
            list.select_set(index)
            self.contextualMenu.tk_popup(event.x_root, event.y_root, entry='')

    def setScrollContext(self, _scrollbar, _otherList) :
        self.scrollbar = _scrollbar
        self.theOtherList = _otherList
        self.list.config(yscrollcommand=self.set)

    def set(self, *args) :
        self.scrollbar.set(*args)
        x, y = args
        self.theOtherList.list.yview_moveto(x)


def applyFilter(filepath) :
    "Return True if the file is to be excluded. False otherwise."

    if filepath == '' : return False

    # hide files beginning with '.'
    s1 = re.search('/\.', filepath)
    if s1 is not None :
        return True

    #s1 = re.search('^\./\.', os.path.basename(filename))
    #if s1 is not None :
    #   return True


class DiffFrame(Frame) :

    # - 
    showOnlyDiff = 0
    showRedOnly = 0 # recent files are "Red"
    dontShowDirectories = 0
    recentLocalFiles = []
    remoteFiles = []
    localFiles = []
    remoteFilesForDiff = []
    localFilesForDiff = []

    def __init__(self, parent, **options) :
        Frame.__init__(self, parent, options)

        self.scrollbar = Scrollbar(self)
        self.panedWindow = PanedWindow(self, orient=HORIZONTAL)

        self.remoteList = List(self.panedWindow, 'remote')
        self.scrollbar.config(command=self.scroll)

        self.localList = List(self.panedWindow, 'local')
        self.scrollbar.config(command=self.scroll)

        self.remoteList.setScrollContext(self.scrollbar, self.localList)
        self.localList.setScrollContext(self.scrollbar, self.remoteList)

        # left 
        self.panedWindow.add(self.localList)
        # right
        self.panedWindow.add(self.remoteList)
        #
        self.panedWindow.pack(side=LEFT, fill=BOTH, expand=1)
        self.scrollbar.pack(side=LEFT, fill=Y)


    def scroll(self, *args) :
        "Scroll Left and Right lists."
        self.localList.list.yview(*args)
        self.remoteList.list.yview(*args)



    def readLocalFiles(self) :
        "Read the local directory, and update the local file list."
        # retrieve local files
        self.localFiles, self.recentLocalFiles = findFiles()

        log(_('Local files: %d') % len(self.localFiles))

        self.localFiles.sort()


    def readRemoteFiles(self) :
        "Read the remote directory, and update the remote file list."
        # retrieve remote files
        try :
            self.remoteFiles = findFilesByHttpGet(config['http-remote-dir'])
            log(_('Remote files: %d') % len(self.remoteFiles))
            self.remoteFiles.sort()

        except :
            logError(_('Cannot read remote files:'))
            logError(traceback.format_exc())


    def makeDiff(self) :
        "Make a diff between local and remote files."

        self.remoteFilesForDiff = []
        self.localFilesForDiff = []
        copyOflocalFiles = self.localFiles[:]

        for remoteFile in self.remoteFiles :
            while (len(copyOflocalFiles) > 0) and (copyOflocalFiles[0] < remoteFile) :
                localFile = copyOflocalFiles.pop(0)
                self.remoteFilesForDiff.append('')
                self.localFilesForDiff.append(localFile)

            # at this point, self.localFiles[0] is >= remoteFile

            if (len(copyOflocalFiles) > 0) and (remoteFile == copyOflocalFiles[0]) :
                localFile = copyOflocalFiles.pop(0)
                self.remoteFilesForDiff.append(remoteFile)
                self.localFilesForDiff.append(localFile)
            else :
                self.remoteFilesForDiff.append(remoteFile)
                self.localFilesForDiff.append('')

        # remaining local files (> remote files)
        for localFile in copyOflocalFiles :
            self.remoteFilesForDiff.append('')
            self.localFilesForDiff.append(localFile)



    def updateDisplay(self) :
        self.makeDiff()

        self.remoteList.list.delete(0, END)
        self.localList.list.delete(0, END)

        # both list are supposed to be synchronised (same number of elements)
        L = len(self.localFilesForDiff)
        i = 0
        while i < L :
            remoteFile = self.remoteFilesForDiff[i]
            localFile = self.localFilesForDiff[i]
            i = i+1

            hide = False
            # check filters to see if it shall be hidden
            if self.showOnlyDiff and remoteFile != '' and localFile != '' :
                hide = True

            if self.dontShowDirectories and \
               ( (len(remoteFile)>0 and remoteFile[-1] == '/') \
               or (len(localFile)>0 and localFile[-1] == '/') ) :
                hide = True

            if self.showRedOnly and not localFile in self.recentLocalFiles :
                hide = True
            
            if applyFilter(localFile) or applyFilter(remoteFile) :
                hide = True

            if not hide :
                # do display
                self.remoteList.list.insert(END, remoteFile)
                self.localList.list.insert(END, localFile)

                if localFile in self.recentLocalFiles :
                    size = self.localList.list.size()
                    self.localList.list.itemconfig(size-1, fg='red', selectforeground='red')
            
    def toggleShowDiffOnly(self) :
        self.showOnlyDiff = 1 - self.showOnlyDiff
        self.updateDisplay()

    def toggleDontShowDirectories(self) :
        self.dontShowDirectories = 1 - self.dontShowDirectories
        self.updateDisplay()

    def toggleShowRedOnly(self) :
        self.showRedOnly = 1 - self.showRedOnly
        self.updateDisplay()


class Console(Frame) :
    CONSOLE_HEIGHT = 10

    def __init__(self, parent, **options) :
        Frame.__init__(self, parent, options)

        self.title = Label(self, text="Console")
        self.title.pack(side=TOP, anchor=NW)
        self.scrollbar = Scrollbar(self)

        self.text = Text(self, height=self.CONSOLE_HEIGHT)
        self.text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)

        self.text.pack(side=LEFT, fill=BOTH, expand=1)
        self.scrollbar.pack(side=LEFT, fill=Y)

        # make it read-only
        self.text.configure(state=DISABLED)
        self.text.tag_config('command', foreground='blue', background='pink')
        self.text.tag_config('error', foreground='white', background='red')




def findFilesByHttpGet(dir) :
    "Find remote files by a HTTP GET request."

    HTTP_SERVER = config['http-server']
    HTTP_USER = config['http-user']
    HTTP_PASSWORD = config['http-password']
    HTTP_REALM = config['http-realm']

    url = 'http://' + HTTP_SERVER
    if dir != '' :
        url = url + '/' + dir
    url = url + '/' + config['http-find-script']
    url = url + '?key=' + config['http-find-key']

    logCommand(_('Reading files... (%s)') % url)
    auth_handler = urllib2.HTTPBasicAuthHandler()
    if HTTP_USER != '' :
        auth_handler.add_password(
            HTTP_REALM,
            url,
            HTTP_USER,
            HTTP_PASSWORD)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(url)

    return response.read().strip().split('\n')

def findFiles(dir = '.') :
    "Find all files in the specified directory."

    result = []
    recentFiles = []
    files = os.listdir(dir)
    for file in files :
        if file == '.' or file == '..' :
            continue

        completePath = os.path.join(dir, file)

        if os.path.isdir(completePath) :
            result.append(completePath.replace('\\', '/') + '/')
            subFiles, subRecentFiles = findFiles(completePath)
            result = result + subFiles
            recentFiles = recentFiles + subRecentFiles
        else :
            # regular file
            result.append(completePath.replace('\\', '/'))
            if Timestamp.isNew(completePath) :
                recentFiles.append(completePath.replace('\\', '/'))

    return result, recentFiles

def downloadFiles() :
    "Download the files selected in the remote list."
    list = diffFrame.remoteList.list
    selection = list.curselection()
    if len(selection) > 0 :
        ftpHandler = Ftp.connect()
        if ftpHandler is not None :
            for index in selection :
                file = list.get(index)
    
                if file != '' :
                    Ftp.download(file, ftpHandler)

            ftpHandler.quit()

        # update the display
        diffFrame.readLocalFiles()
        diffFrame.updateDisplay()

    else :
        # no file selected
        log(_('You must select at least 1 file for downloading.'))


def uploadNewFiles() :
    "Upload the recent file and update the timestamp if the upload was successful."
    recentFiles = diffFrame.recentLocalFiles
    if len(recentFiles) > 0 :
        ftpHandler = Ftp.connect()
        if ftpHandler is not None :
            for file in recentFiles :
                Ftp.upload(file, ftpHandler)

            ftpHandler.quit()

        if not Ftp.errorOccurred :
            Timestamp.touch()

        # update the display
        diffFrame.readRemoteFiles()
        diffFrame.updateDisplay()

    else :
        log(_('No recent file.'))

def uploadFiles() :
    "Upload the files selected in the local list."
    list = diffFrame.localList.list
    selection = list.curselection()
    if len(selection) > 0 :
        ftpHandler = Ftp.connect()
        if ftpHandler is not None :
            for index in selection :
                file = list.get(index)
    
                if file != '' :
                    Ftp.upload(file, ftpHandler)

            ftpHandler.quit()

        # update the display
        diffFrame.readRemoteFiles()
        diffFrame.updateDisplay()

    else :
        # no file selected
        log(_('You must select at least 1 file for uploading.'))


def updateBothLists() :
    
    diffFrame.readRemoteFiles()
    diffFrame.readLocalFiles()
    diffFrame.updateDisplay()
    log('OK.')


class Timestamp :

    TIMESTAMP_FILE = '.timestamp'

    def touch() :
        "Update the timestamp with the current time."
        log(_('Initialising timestamp file : %s') % Timestamp.TIMESTAMP_FILE)
        if os.path.exists(Timestamp.TIMESTAMP_FILE) :
            os.utime(Timestamp.TIMESTAMP_FILE, None)
        else :
            f = open(Timestamp.TIMESTAMP_FILE, 'a')
            f.close()

        diffFrame.recentLocalFiles = []
        diffFrame.updateDisplay()

    def isNew(file) :
        "Indicate if a file is newer than the timestamp."
        timestamp = os.stat(Timestamp.TIMESTAMP_FILE).st_mtime
        fileTime = os.stat(file).st_mtime
        return fileTime > timestamp

    touch = staticmethod(touch)
    isNew = staticmethod(isNew)


def createPHPfindScript() :
    """
    Create (if needed) a local PHP script file and upload it. This script is used for retrieving the list of remote files.
    If a local file already exists with the same name, it does not create it. It simply uploads it.
    """
    phpscript = """<?
if (md5($_GET['key']) != '%s') {
    header('HTTP/1.1 403 Forbidden');
    echo "Forbidden";
    exit(0);
}
function find($dirpath) {
    $files = array();
    if ($dirpath == '') $dirpath = '.';
    if ($dir = opendir($dirpath)) {
        while (false !== ($filename = readdir($dir))) {
            $file = $dirpath.'/'.$filename;
            if ($filename != "." && $filename != "..") {
                if (is_dir($file)) {
                    array_push($files, $file . '/');
                    $sub_list = find($file);
                    $files = array_merge($files, $sub_list);
                } else {
                    array_push($files, $file);
                }
            }
        }
    }
    return $files;
}
$list =  find('.');
foreach ($list as $file) {
    echo "$file\\n";
}
?>
""" % (md5.md5(config['http-find-key']).hexdigest())

    scriptName = os.path.join(config['local-root-dir'], config['http-find-script'])
    if not os.path.lexists(scriptName) :
        confirm = True
    else :
        msg = _('Are you sure you want to overwrite this file ?\n%s') % scriptName
        confirm = tkMessageBox.askokcancel(_('Overwrite a file'), msg, default=tkMessageBox.CANCEL)

    if confirm :
        log(_('Creating local file %s') % scriptName)
        # create the file locally
        f = open(scriptName, 'w')
        f.write(phpscript)
        f.close()
    else :
        log(_('No change on local file %s.') % scriptName)

    Ftp.upload(config['http-find-script'])
    

def quit(event) :
    root.quit()
    
# main part of the program
root = Tk()
n = 0
root.bind("<Control-Q>", quit)
root.bind("<Control-q>", quit)

# build the menu bar
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label=_('Initialise timestamp'), command=Timestamp.touch)
filemenu.add_command(label=_('Create and upload PHP find-file script'), command=createPHPfindScript)
filemenu.add_command(label=_('Quit') + ' (Ctrl+q)', command=root.quit)
menubar.add_cascade(label=_('Action'), menu=filemenu)

display_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label=_('View'), menu=display_menu)

root.config(menu=menubar)

# Action Bar ################################

actionBar = Frame(root)

updateButton = Button(actionBar, text=_('Update Display'), command=updateBothLists)
helpUpdate = HelpBalloon(updateButton, text=_('Update the 2 lists:\n  - local files\n  - remote files\n(this action makes a connection to the web site)'))
updateButton.pack(side=LEFT)

downloadButton = Button(actionBar, text=_('<< Download'), command=downloadFiles)
helpUpload = HelpBalloon(downloadButton, text=_('Download selected remote files\nto local directory'))
downloadButton.pack(side=LEFT)

uploadButton = Button(actionBar, text=_('Upload >>'), command=uploadFiles)
helpUpload = HelpBalloon(uploadButton, text=_('Upload selected files to the web site'))
uploadButton.pack(side=LEFT)

uploadButtonRed = Button(actionBar, text=_('Upload Recent Files >>'), command=uploadNewFiles)
helpUpload = HelpBalloon(uploadButtonRed, text=_('Upload the recent local files\n(in red) to the web site'))
uploadButtonRed.pack(side=LEFT)

actionBar.pack(side=TOP)



panedWindow = PanedWindow(orient=VERTICAL)
panedWindow.pack(fill=BOTH, expand=1)

diffFrame = DiffFrame(panedWindow)
panedWindow.add(diffFrame)

display_menu.add_checkbutton(label=_('Hide identical files'), command=diffFrame.toggleShowDiffOnly)

display_menu.add_checkbutton(label=_('Hide directories'), command=diffFrame.toggleDontShowDirectories)

display_menu.add_checkbutton(label=_('Display only recent files'), command=diffFrame.toggleShowRedOnly)

console = Console(panedWindow) 
panedWindow.add(console)

# create timestamp file if needed
if not os.path.exists(Timestamp.TIMESTAMP_FILE) :
    Timestamp.touch()

# load .ini file
def readConfigFile() :
    config = {}
    progname = os.path.basename(sys.argv[0])
    configFile = re.sub('\.pyw?$', '.conf', progname)
    if configFile == progname :
        configFile = progname + '.conf'
    logCommand(_('Loading configuration file %s.') % configFile)
    c = ConfigParser.SafeConfigParser()
    c.read(configFile)
    # only first section supported
    if len(c.sections()) == 0 :
        logError(_('Error: configuration file %s has no section!') % configFile)
    else :
        sectionName = c.sections()[0]
        log(_("Using section '%s'.") % (sectionName))
        for (option, value) in c.items(sectionName) :
            config[option] = value

    # verification that all needed options are set
    for o in [ 'local-root-dir', 'ftp-user', 'ftp-server', 'ftp-password', 'ftp-remote-dir', 'http-server', 'http-user', 'http-password', 'http-realm', 'http-remote-dir', 'http-find-script' ] :
        if not config.has_key(o) :
            logError(_("Option '%s' manquante.") % o)

    # put some default values for missing options
    if not config.has_key('http-find-key') :
        config['http-find-key'] = ''

    return config

config = readConfigFile()
#print config

log(_("Click on 'Update' in order to display the lists."))

root.mainloop()

############### example of configuration file ##############
configFileSample = """
[john]

# root directory for local files (may be .)
local-root-dir: .

# ftp account ###############
ftp-server: ftp.example.com
ftp-user: john.doe
ftp-password: thechicken

# all remote FTP operations will be conducted under this directory
ftp-remote-dir: abcd

# the remote ftp directory is:
# ftp://<ftp-server>/<ftp-remote-dir>/

# http account ###############
http-server: www.example.com
http-user: john1
http-password: johnP
http-realm: MyRealm
http-remote-dir: %(ftp-remote-dir)s
http-find-script: find_files.php5
http-find-key: %(http-user)s

# the remote directory is:
# http://<http-server>/<http-remote-dir>/
# the php script:
# http://<http-server>/<http-remote-dir>/<http-find-script>?key=<http-find-key>
#
# the remote ftp directory and the remote directory are supposed
# to point to the same place.

"""
