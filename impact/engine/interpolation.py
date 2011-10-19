"""Wrapper around SciPy interpolation.

This module takes care of differences in assumptions about axes and
ordering of dimensions between raster files and numpy arrays.
"""

import numpy
from impact.engine.interpolation2d import interpolate_raster
from impact.storage.vector import Vector
from impact.storage.vector import convert_polygons_to_centroids


def raster_spline(longitudes, latitudes, values):
    """Create spline for bivariate interpolation

    Input
        longitudes: array of monotoneously increasing latitudes (west to east)
        latitudes: array of monotoneously increasing latitudes (south to north)
        values: 2d array of values defined on grid points corresponding to
                given longitudes and latitudes

    Output
        Callable object F that returns interpolated values for arbitrary
        points within the specified domain.
        F is called as F(lon, lat) where lon and lat are either
        single valued or vector valued. Values outside domain raises an
        exception. (NOT YET IMPLEMENTED)
    """

    # Input checks
    assert len(longitudes) == values.shape[1]
    assert len(latitudes) == values.shape[0]

    # Flip matrix A up-down so that scipy will interpret latitudes correctly.
    A = numpy.flipud(values)

    # Call underlying spline
    try:
        F = RectBivariateSpline(latitudes, longitudes, A)
    except:
        msg = 'Interpolation failed. Please zoom out a bit and try again'
        raise Exception(msg)

    # Return interpolator
    return Interpolator(F, longitudes, latitudes)


class Interpolator:
    """Class providing callable 2D interpolator

    To instantiate run Interpolator(F, longitudes, latitudes), where
        F is the spline e.g. generated by RectBivariateSpline
        longitudes, latitudes: Vectors of coordinates used to create F
    """

    def __init__(self, F, longitudes, latitudes):
        self.F = F
        self.minlon = longitudes[0]
        self.maxlon = longitudes[-1]
        self.minlat = latitudes[0]
        self.maxlat = latitudes[-1]

    def __call__(self, lon, lat):
        """Interpolate to specified location

        Input
            lon, lat: Location in WGS84 geographic coordinates where
                      interpolated value is sought

        Output
            interpolated value at lon, lat
        """

        msg = ('Requested interpolation longitude %f lies outside '
               'interpolator bounds [%f, %f]. '
               'Assigning NaN.' % (lon, self.minlon, self.maxlon))
        if not self.minlon <= lon <= self.maxlon:
            #print msg
            return numpy.nan

        msg = ('Requested interpolation latitude %f lies outside '
               'interpolator bounds [%f, %f]. '
               'Assigning NaN.' % (lat, self.minlat, self.maxlat))
        if not self.minlat <= lat <= self.maxlat:
            #print msg
            return numpy.nan

        return self.F(lat, lon)


def interpolate_raster_vector_points(R, V, name=None):
    """Interpolate from raster layer to point data

    Input
        R: Raster data set (grid)
        V: Vector data set (points)
        name: Name for new attribute.
              If None (default) the name of R is used

    Output
        I: Vector data set; points located as V with values interpolated from R

    """

    # FIXME: I think this interpolation can do grids as well if the
    #        interpolator is called with x and y being 1D arrays (axes)

    # Input checks
    assert R.is_raster
    assert V.is_vector
    assert V.is_point_data

    # Get raster data and corresponding x and y axes
    A = R.get_data(nan=True)
    longitudes, latitudes = R.get_geometry()
    assert len(longitudes) == A.shape[1]
    assert len(latitudes) == A.shape[0]

    # Get vector point geometry as Nx2 array
    coordinates = numpy.array(V.get_geometry(),
                              dtype='d',
                              copy=False)

    # Interpolate and create new attribute
    N = len(V)
    attributes = []
    if name is None:
        name = R.get_name()

    values = interpolate_raster(longitudes, latitudes, A,
                                coordinates, mode='linear')

    # Create list of dictionaries for this attribute and return
    for i in range(N):
        attributes.append({name: values[i]})

    return Vector(data=attributes, projection=V.get_projection(),
                  geometry=coordinates)


def interpolate_raster_vector(R, V, name=None):
    """Interpolate from raster layer to vector data

    Input
        R: Raster data set (grid)
        V: Vector data set (points or polygons)
        name: Name for new attribute.
              If None (default) the name of R is used

    Output
        I: Vector data set; points located as V with values interpolated from R

    Note: If target geometry is polygon, data will be interpolated to
    its centroids and the output is a point data set.
    """

    # Input checks
    assert R.is_raster
    assert V.is_vector

    if V.is_polygon_data:
        # Use centroids, in case of polygons
        P = convert_polygons_to_centroids(V)
    else:
        P = V

    return interpolate_raster_vector_points(R, P, name=name)
