
import gdal
import ogr
from skimage import exposure
from skimage.segmentation import quickshift, felzenszwalb
import time
import numpy as np
import gc
from skimage.util import img_as_ubyte, img_as_uint
import os
os.chdir(os.path.dirname(__file__))
import functions 



def resize_raster(fn, dest):
    """ Réechantillonage de l'image à une nouvelle résolution (x, y)"""
    ds = gdal.Open(fn)
    
    X= ds.RasterXSize
    Y= ds.RasterYSize
    
    #modifier ces deux expressions pour changer la résolution finale
    x = X/2
    y = Y/2
    
    #chemin de l'output
    out_fn = fn.replace(".tif" , "_rescaled.tif")   
    gdal.Warp(out_fn, ds, height = y, width = x, resampleAlg="cubic")
    
    ds.FlushCache()
    ds = None
    
    return out_fn

def segmentation(img_fn, dest, in_scale = 150, in_sigma = 0.8, in_min_size=100): 
    
    """Segmentation felzenszwalb prends le chemin du fichier en entrée et créer deux fichier de segments sur le disque : raster et vecteur."""
    if not os.path.isdir(dest) : os.mkdir(dest)
    
    #lecture de l'image sous forme de np.array
    ref_ds, bdata_ortho = functions.readFiles(img_fn)
    bdata_ortho = bdata_ortho.astype(np.uint8)
    print(bdata_ortho.dtype)
    
    toc = time.time() #début du timer
    
    img = exposure.rescale_intensity(bdata_ortho, out_range=np.uint8)
    img = img_as_ubyte(bdata_ortho)
    print("segments start :  ")
    
    # Appel de la fonction de Segmentation Felzenszwalb
    segments =img_as_uint(felzenszwalb(img, scale=in_scale, sigma=in_sigma, min_size=in_min_size)) 
    #Création du Raster
    segments_fn = os.path.join(dest, os.path.basename(img_fn).replace("rescaled", "segments"))
    functions.writeRaster(segments, segments_fn, ref_ds)
    #Création du shapefile
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
 
# dossier des inputs
imgDir = '../02-inputs/'
imgDir = "C:/Users/Karim/Desktop/Newfolder"

#Scan les dossiers qui se trouvent dans imgDir, et effectue le reéchantillonage et la segmentations des images (*.tif) qui s'y trouvent.
for folder in [_.path for _ in os.scandir(imgDir) if _.is_dir()]:
    files = [_.path for _ in os.scandir(folder) if not "rescaled" in _.path if ".tif" in _.path]
    
    for ortho_fn in files:    
        print("Traitement du fichier :", ortho_fn)
        # appel à la fonction de reéchantillonage
        # ortho_rescaled = resize_raster(ortho_fn, imgDir)
        print("Rescaling Done.")
        gc.collect() #garbage collector 
        
        #creation d'output des segments
        seg_dir = os.path.join(folder, "segments")
        if not os.path.exists(seg_dir) :
            os.mkdir(seg_dir)
        
        # appel à la fonction de segmentation
        # segmentation(ortho_rescaled, seg_dir, 150, 0.8, 100)
        print("\n"*2)
    
    
    



