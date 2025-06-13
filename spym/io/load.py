import os
from . import rhksm4

def load(filename, scaling=True):
    """Import data from an RHK ``.sm4`` file.

    Only the subset required by ``rhkpy`` is implemented.

    Args:
        filename: path to the SPM file.
        scaling: if True convert data to physical units (default), if False keep raw data.

    Returns:
        xarray Dataset with data and metadata.

    """

    if filename.lower().endswith(".sm4"):
        try:
            ds = rhksm4.to_dataset(filename, scaling=scaling)
        except Exception:
            print("Error: the file does not appear to be valid.")
            return None
    else:
        print("Error: unsupported file format")
        return None

    for dr in ds:
        ds[dr].attrs["filename"] = os.path.basename(filename)

    return ds
