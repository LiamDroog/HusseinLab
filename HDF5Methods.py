import h5py, os

"""
Methods for easily working with HDF5 files outside of any program
"""


def createFile(filename):
    if os.path.exists(filename):
        return False
    else:
        f = h5py.File(filename, mode='a')
        f.close()
        return True


def setMetadata(filename, attribute, value, path='/'):
    with h5py.File(filename, mode='a') as h5f:
        h5f[path].attrs[attribute] = value


def createGroup(filename, groupname):
    with h5py.File(filename, mode='a') as h5f:
        h5f.create_group(groupname)


def createDataset(filename, name, data, group='/', compression='gzip'):
    with h5py.File(filename, mode='a') as h5f:
        h5f[group].create_dataset(
            name,
            data=data,
            compression=compression)

def getDataset(filename, name, group='/'):
    with h5py.File(filename, mode='a') as h5f:
        return h5f[group][name]


def getMetadata(filename, path='/'):
    with h5py.File(filename, mode='a') as h5f:
        return list(h5f[path].attrs.items())


def getData(filename, dataset, path=None):
    if path is None:
        path = '/'
    with h5py.File(filename, mode='a') as h5f:
        return h5f[path][dataset][()]


def getSubGroups(filename, path='/'):
    with h5py.File(filename, mode='a') as h5f:
        return list(h5f[path].keys())


def tree(filename):
    with h5py.File(filename, mode='a') as h5f:
        h5f.visititems(__print_attrs)

    
def __print_attrs(name, obj):
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
