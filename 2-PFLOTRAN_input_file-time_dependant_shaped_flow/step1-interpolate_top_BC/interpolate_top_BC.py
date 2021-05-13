"""
Template to interpolate a set of raster files to a PFLOTRAN mesh
"""
# import PyFLOTRAN.utils.globals as globals
import PyFLOTRAN.readers as readers
import PyFLOTRAN.interpolation as interpolation
import PyFLOTRAN.writers as writers
from PyFLOTRAN.config import config

import glob
import numpy as np
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


def set_ellipse(center, a, b, x, y):
    eq_ellipse = (x-center[0])**2/a**2 + (y-center[1])**2/b**2
    return eq_ellipse <= 1


def main(argv):
    output_filename = "top_BC_velocities.h5"

    # parameters
    nx = config.general.nx
    ny = config.general.ny
    center_ellipse = (config.general.center_ellipse_x, config.general.center_ellipse_y)
    a = config.general.a
    b = config.general.b

    # arr_x, arr_y = np.meshgrid(np.linspace(0, x, nx), np.linspace(0, y, ny))
    arr_x, arr_y = np.meshgrid(range(nx), range(ny))
    bc_arr = set_ellipse(center_ellipse, a, b, arr_x, arr_y)
    bc_arr = bc_arr.astype(int)
    print(arr_x.shape)
    # bc_arr = bc_arr*config.general.constant_recharge

    arr_x = arr_x*4
    arr_y = arr_y*4

    cloud_of_point = []
    for i in range(nx):
        for j in range(ny):
            cloud_of_point.append([arr_x[j, i], arr_y[j, i], bc_arr[j, i]])
    cloud_of_point = np.array(cloud_of_point)
    cloud_of_point_pd = pd.DataFrame(cloud_of_point).astype(np.float32)
    cloud_of_point_pd.to_csv("cop.csv", index=False)
    interpolated_data = []
    for index, time in enumerate(config.time_series.time):
        temp_arr = cloud_of_point.copy().astype(np.float32)
        temp_arr[:, 2] = temp_arr[:, 2] * config.time_series.flow[index]
        temp_arr_pd = pd.DataFrame(temp_arr)
        # temp_arr_pd.to_csv(f"cop_{index}.csv")
        bc_interpolator = interpolation.SparseDataInterpolator()
        bc_interpolator.add_data(temp_arr)
        bc_interpolator.create_regular_mesh(n_x=nx, n_y=ny, dilatation_factor=config.general.dilatation_factor)
        bc_interpolator.interpolate(method='nearest')
        interpolated_data.append(bc_interpolator.interpolated_data)

    # temp_array = np.reshape(interpolated_data[0], (interpolated_data[0].shape[0], 1))
    # print(temp_array.shape)
    temp_array = interpolated_data[0].reshape(750, 400)
    temp_array = temp_array.T
    plt.imshow(temp_array)
    plt.show()

    base_writer = writers.HDF5RasterWriter(filename=output_filename, data=np.array(interpolated_data),
                                           info=bc_interpolator.info, times=np.array(config.time_series.time))
    base_writer.run(filename=output_filename)


if __name__ == "__main__":
    main(sys.argv)
