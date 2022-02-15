
import gdal
import ogr
import os
from skimage import exposure
from skimage.segmentation import quickshift, felzenszwalb
import time
import numpy as np
import gc
from skimage.util import img_as_ubyte, img_as_uint


def resize_raster(fn, dest):
    """ Diminue la résolution de l'image si trop grande"""
    ds = gdal.Open(fn)
    
    X= ds.RasterXSize
    Y= ds.RasterYSize
    
    x = X/2
    y = Y/2
    
    out_fn = imgDir + fn.split(sep = "/")[-1][:-4] + f"_rescaled.tif"
    gdal.Warp(out_fn, ds, height = y, width = x, resampleAlg="cubic")
    
    ds.FlushCache()
    ds = None
    
    return out_fn

def segmentation(img_fn, dest, scale = 100, sigma = 1, min_size=50):    
    if not os.path.isdir(dest) : os.mkdir(dest)
    
    ref_ds, bdata_ortho = functions.readFiles(img_fn)
    
    bdata_ortho = bdata_ortho.astype(np.uint8)
    print(bdata_ortho.dtype)
    
 
    toc = time.time() #timer
    img = exposure.rescale_intensity(bdata_ortho, out_range=np.uint8)
    img = img_as_ubyte(bdata_ortho)
    print("segments start :  ")
    # Segmentation Felzenszwalb
    segments =img_as_uint(felzenszwalb(img, scale=scale, sigma=sigma, min_size=min_size)) 
    
    #Segmentation QuickShift
    # segments = quickshift(img, convert2lab=False)
    segments_fn = os.path.join(dest, os.path.basename(img_fn).replace("rescaled", "segments"))
    functions.writeRaster(segments, segments_fn, ref_ds)
    polygonize_raster(segments_fn, )
    tic= time.time()

    print(f"Segmentation done. \n {segments_fn} crée en : {tic-toc} seconds ")
    
    ref_ds.FlushCache()
    ref_ds = bdata_ortho = None
    
    return segments_fn

def polygonize_raster(raster_fn, out_fn=""):
    """ verctorise un raster en ESRI shapefile"""
    #lecture du raster
    raster_ds = gdal.Open(raster_fn)
    band = raster_ds.GetRasterBand(1)
    
    #Set la projection
    ras_srs = ogr.osr.SpatialReference()
    ras_srs.ImportFromWkt(raster_ds.GetProjection())
    
    #Creation du shapeFile
    driver = ogr.GetDriverByName("ESRI Shapefile")
    out_ds = driver.CreateDataSource(raster_fn.replace(".tif", ".shp") )
    out_lyr = out_ds.CreateLayer("Segments", srs = ras_srs)
    
    #Ajout des champs d'attributs
    newField = ogr.FieldDefn('DN', ogr.OFTInteger)
    out_lyr.CreateField(newField)
    newField = ogr.FieldDefn('Cid', ogr.OFTInteger)
    out_lyr.CreateField(newField)

    # Fonction de vectorisation
    gdal.Polygonize(band, None, out_lyr, 0, [])
    
    out_ds.FlushCache()
    raster_ds.FlushCache()
    out_ds = raster_ds = out_lyr = None
 
# #input
os.chdir(os.path.dirname(__file__))
import functions 
imgDir = '../02-inputs/'

#Output
resultats= '../03-resultats/'
if not os.path.isdir(resultats) :   os.mkdir(resultats) #créer le dossier si inexistant

#Scan les fichier dans le dossier d'inputs
for folder in [_.path for _ in os.scandir(imgDir) if _.is_dir()]:
    files = [_.path for _ in os.scandir(folder) if not "rescaled" in _.path if ".tif" in _.path]
    for ortho_fn in files:
        print(ortho_fn)
        
        ortho_rescaled = resize_raster(ortho_fn, imgDir)
        print("Rescaling Done.")
        seg_dir = os.path.join(folder, "segments")
        if not os.path.exists(seg_dir) :
            os.mkdir(seg_dir)
        
        gc.collect()
        segmentation(ortho_rescaled, seg_dir, 150, 0.8, 100)
        
    
    
    
        




# resize_raster(Po_fn[0], imgDir)



# file_name = path.split(sep="/")[-1] #nom du fichier
# # Lecture des donnés de l'ortho
# ref_ds, bdata_ortho = functions.readFiles(path)

# img = exposure.rescale_intensity(bdata_ortho) #rescale des valeurs à 0-1


# # Segmentation Quickshift :         
# # segments = quickshift(img, convert2lab=0, kernel_size=7)
# # segments_fn = resultats+file_name[:-4]+'_qshift_ker7.tif'
# # functions.writeRaster(segments, segments_fn, ref_ds)

# # boucle pour different parametres de segmentation
# for i in [150]:
#     for j in [1]:
#         toc = time.time() #timer
#         print("segments start ")
        
#         # Segmentation Felzenszwalb
#         segments = felzenszwalb(img, scale=i, sigma=j, min_size=50)
#         segments_fn = resultats+file_name[:-4]+f'_felz-scale{i}-sigma{j}.tif'
        
#         functions.writeRaster(segments, segments_fn, ref_ds)
#         tic= time.time()
    
#         print(f"{segments_fn} crée en : {tic-toc}")
        


