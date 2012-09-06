import sys
import os
from shutil import move
from shutil import Error as ShutilError


class CleanMV:

    def __init__(self, directory, datafile):
        self.directory = directory
        self.datafile = datafile
        self.verbose = False
        self.fileCount = 0
        self.fileMovedCount = 0
        self.backupdir = None

    def setVerbose(self, is_verbose):
        self.verbose = is_verbose

    def setBackupDirectory(self, backupdir):
        self.backupdir = backupdir

    def __mkbackup(self):
        """Tworzy katalog backup"""
        if "backup" in os.listdir(self.directory):
            return
        path = "%s/backup" % self.directory
        try:
            os.mkdir(path,0770)
        except OSError:
            print "Nie mozna utworzyc katalogu we wskazanej sciezce %s" % (
                    self.directory)

    def __isFileExist(self):
        return True

    def __opendatafile(self):
        """Otwiera plik do odczytu, zapisuje jako parametr klasy - self.f"""
        path = "%s/%s" % (
                self.directory,
                self.datafile)

        self.f = open(path,'r')

    def __prepareFilepath(self,filepath):
        """Przygotowuje sciezke pliku do przeniesienia. Usuwa z konca lini
        znak konca lini 'n' i zwraca dokladno sciezke bezwzgledna pliku"""
        dirs = filepath.split('/')
        filename_to_move = dirs.pop()
        if filename_to_move.endswith('\n'):
            filename_to_move = filename_to_move[:-1] # usun znak konca lini
        dirs.append(filename_to_move)
        filepath = "/".join(dirs)
        return filepath

    def __prepareDirectoryPath(self,path):
        """Tworzy strukture katalogow ze zmiennej path i zwraca sciezke do
        katalogu gdzie plik ma zostac zapisany"""
        dirs = path.split('/')
        dirs.pop() #zdejmij ostatnia nazwe - plik do utworzenia
        directPath = "%s/backup/" % self.directory
        # dirs - katalogi do utworzenia
        # directPath - aktualny katalog do tworzenia nowego katalogu

        for d in dirs:
            path = "%s/%s" % (
                    directPath, d)
            if d in os.listdir(directPath):
                directPath = path
                continue
            try:
                os.mkdir(path,0770)
            except OSError,err:
                print "ERROR: Nie mozna utworzyc katalogu %s! - %s" % (
                        path,err)
                sys.exit(2)
            directPath = path


        # katalog bezposredni do zapisu pliku, np:
        # /root/skrypty/path/to/dir #
        # return directPath

    def __createDirectories(self):
        """Dla kazdej lini w pliku self.f stworzy katalogi"""
        self.__opendatafile()
        for line in self.f:
            self.__prepareDirectoryPath(line)
        self.__closeDataFile()

    def __createBackupPath(self,line):
        dirs = line.split('/') # > ['dir1','dir2','filename'
        dirs.pop() # usun ostatni element (nazwa pliku) > ['dir1','dir2']
        path = '/'.join(dirs)
        backupPath = "%s/backup/%s" % (self.directory,path)
        return backupPath

    def __moveFiles(self):
        """Dla kazdej lini w pliku, wywoluje tworzenie katalogow, a nastepnie
        przenosi plik do stworzonej sciezki backupdir"""
        # otworz plik
        self.__opendatafile()

        for line in self.f:
            filepath = "%s/%s" % (
                    self.directory,
                    line)
            #if ~self.__isFileExist():
            #    print "Plik '%s' nie istnieje!" % filepath

            filepath = self.__prepareFilepath(filepath)

            backupdir = self.__createBackupPath(line)

            self.fileCount += 1

            if self.verbose:
                print filepath

            try:
                move(filepath,backupdir)
            except IOError, err:
                print "ERROR: Wystapil blad w trakcie przenoszenia plikow..."
                print str(err)
                continue
                #sys.exit()
            except ShutilError, err:
                if self.verbose:
                    print "ERROR: Wystapil problem w trakcie \
                            przenoszenia plikow..."
                    print str(err)
                continue
            #inkrementuj licznik plikow przeniesionych
            self.fileMovedCount += 1
        # zamknij plik po zakonczonej pracy
        self.__closeDataFile()

    def __howManyMoved(self):
        print "Plikow do przeniesienia: %i " % self.fileCount
        print "Przeniesiono plikow: %i " % self.fileMovedCount

    def __closeDataFile(self):
        self.f.close()

    def move(self):
        self.__mkbackup()
        self.__createDirectories() #stworzy katalogi
        self.__moveFiles()
        self.__howManyMoved()

