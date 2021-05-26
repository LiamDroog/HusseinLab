import h5py, os

"""
Methods for easily working with HDF5 files outside of any program. Replaces methods present in 
droogCNC.py (yet to be removed)
"""


def createFile(filename):
    """
    Creates HDF5 file in current directory.

    :param filename: Name of file to create
    :return: False if file exists else true
    """
    if os.path.exists(filename):
        return False
    else:
        f = h5py.File(filename, mode='a')
        f.close()
        return True


def setMetadata(filename, attribute, value, path='/'):
    """
    Sets metadata of a specified hdf5 file or group/dataset within

    :param filename: Name of target file, string
    :param attribute: Metadata attribute, string
    :param value: Value corresponding to attribute, string
    :param path: Path to desired group/dataset ('/' is parent file)
    :return: None
    """
    with h5py.File(filename, mode='a') as h5f:
        h5f[path].attrs[attribute] = value


def createGroup(filename, groupname):
    """
    Creates group within given hdf5 file

    :param filename: Target hdf5 file
    :param groupname: Name of group to create
    :return: None
    """
    with h5py.File(filename, mode='a') as h5f:
        h5f.create_group(groupname)


def createDataset(filename, name, data, group='/', compression='gzip'):
    """
    Creates dataset within specified file.

    :param filename: Name of target hdf5 file
    :param name: Name of dataset to create
    :param data: Numpy data array to append into dataset
    :param group: Subgroup of parent file to place dataset, optional.
    :param compression: Compression style. GZIP is immortal
    :return: None. Breaks if dataset exists though.
    """
    with h5py.File(filename, mode='a') as h5f:
        h5f[group].create_dataset(
            name,
            data=data,
            compression=compression)


def getDataset(filename, name, group='/'):
    """
    Gets target dataset from a specified hdf5 file.

    :param filename: Target file
    :param name: Target dataset within file
    :param group: Group dataset is in, only if applicable.
    :return: Target dataset
    """
    with h5py.File(filename, mode='a') as h5f:
        return h5f[group][name]


def getMetadata(filename, path='/'):
    """
    Gets metadata from target file and path

    :param filename: Target file
    :param path: Path to target group or dataset. '/' is parent file path
    :return: List of metadata and corresponding values
    """
    with h5py.File(filename, mode='a') as h5f:
        return list(h5f[path].attrs.items())


def getData(filename, dataset, path=None):
    """
    Gets data from specified hdf5 file and dataset.

    :param filename: Target file
    :param dataset: Target dataset
    :param path: Path to target dataset. '/' is parent file path with no groups
    :return: data in numpy array (I think, or a list)
    """
    if path is None:
        path = '/'
    with h5py.File(filename, mode='a') as h5f:
        return h5f[path][dataset][()]


def getSubGroups(filename, path='/'):
    """
    Gets subgroups from a specified hdf5 file.

    :param filename: Target file
    :param path: Path to directory to scan for subgroups. '/' is top level
    :return: List of subgroups
    """
    with h5py.File(filename, mode='a') as h5f:
        return list(h5f[path].keys())


def tree(filename):
    """
    Similar to windows style tree command, displays all groups and datasets for a given hdf5 file

    :param filename: target filename, string
    :return: None
    """
    with h5py.File(filename, mode='a') as h5f:
        h5f.visititems(__print_attrs)


def __print_attrs(name, obj):
    """
    Used for H5py's visititems method to get all group and dataset metadata in one fell swoop
    :param name: Group in question
    :param obj: Dataset in question
    :return: None
    """
    try:
        print('/' + name)
        n = 5
        print(' ' * n + 'Metadata:')

        for key, val in obj.attrs.items():
            print(' ' * n + "%s: %s" % (key, val))
        print(obj[()])
        print('\n')

    except Exception as e:
        print(e)
