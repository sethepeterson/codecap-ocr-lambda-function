# Based off of:
# https://stackoverflow.com/questions/434641/how-do-i-set-permissions-attributes-on-a-file-in-a-zip-file-using-pythons-zip

# Orignial code:
# https://github.com/python/cpython/blob/3.6/Lib/zipfile.py#L1648

from zipfile import ZipFile, ZipInfo
import time


class FullPermissionZipFile(ZipFile):
    def writestr(self, zinfo_or_arcname, data, compress_type=None):
        """Write a file into the archive.  The contents is 'data', which
        may be either a 'str' or a 'bytes' instance; if it is a 'str',
        it is encoded as UTF-8 first.
        'zinfo_or_arcname' is either a ZipInfo instance or
        the name of the file in the archive."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not isinstance(zinfo_or_arcname, ZipInfo):
            zinfo = ZipInfo(filename=zinfo_or_arcname,
                            date_time=time.localtime(time.time())[:6])
            zinfo.compress_type = self.compression
            if zinfo.filename[-1] == '/':
                zinfo.external_attr = 0o40775 << 16   # drwxrwxr-x
                zinfo.external_attr |= 0x10           # MS-DOS directory flag
            else:
                zinfo.external_attr = 0o600 << 16     # ?rw-------
        else:
            zinfo = zinfo_or_arcname
            zinfo.external_attr = 2180972544          # -rwxrwxrwx
            

        if not self.fp:
            raise ValueError(
                "Attempt to write to ZIP archive that was already closed")
        if self._writing:
            raise ValueError(
                "Can't write to ZIP archive while an open writing handle exists."
            )

        if compress_type is not None:
            zinfo.compress_type = compress_type

        zinfo.file_size = len(data)            # Uncompressed size
        zinfo.external_attr = 0x81ed0000          # -rwxrwxrwx

        with self._lock:
            with self.open(zinfo, mode='w') as dest:
                dest.write(data)
