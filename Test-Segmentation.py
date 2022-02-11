import functions 
import gdal
import ogr
import os
from skimage import exposure
from skimage.segmentation import quickshift, felzenszwalb
import time


def resize_raster(fn, dest):
    """ Diminue la résolution de l'image si trop grande"""
    ds = gdal.Open(fn)
    
    X= ds.RasterXSize
    Y= ds.RasterYSize
    
    x = X/2
    y = Y/2
    
    out_fn = imgDir + fn.split(sep = "/")[-1][:-4] + f"_rescaled.tif"
    gdal.Warp(out_fn, ds, height = y, width = x, resampleAlg="cubic")
    
    return out_fn

def segmentation(img_fn, dest, scale = 100, sigma = 1, min_size=50):    
    if not os.path.isdir(dest) : os.mkdir(dest)
    
    ref_ds, bdata_ortho = functions.readFiles(img_fn)
    toc = time.time() #timer
    print("segments start ")
    img = exposure.rescale_intensity(bdata_ortho)
    
    # Segmentation Felzenszwalb
    segments = felzenszwalb(img, scale=scale, sigma=sigma, min_size=min_size)
    
    #Segmentation QuickShift
    
    segments_fn = os.path.join(dest, "segments_{}x{}x{}.tif".format(int(scale),int(sigma),int(min_size)))
    functions.writeRaster(segments, segments_fn, ref_ds)
    polygonize_raster(segments_fn, )
    tic= time.time()

    print(f"{segments_fn} crée en : {tic-toc}")
    
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
    out_ds = driver.CreateDataSource(raster_fn.replace(".tif", "_blank.shp") )
    out_lyr = out_ds.CreateLayer("Segments", srs = ras_srs)
    
    #Ajout des champs d'attributs
    newField = ogr.FieldDefn('DN', ogr.OFTInteger)
    out_lyr.CreateField(newField)
    newField = ogr.FieldDefn('Cid', ogr.OFTInteger)
    out_lyr.CreateField(newField)

    # Fonction de vectorisation
    gdal.Polygonize(band, None, out_lyr, 0, [])
    
    out_ds = raster_ds = out_lyr = None

 
# #input
os.chdir(os.path.dirname(__file__))
imgDir = '../02-inputs/'

#Output
resultats= '../03-resultats/'
if not os.path.isdir(resultats) :   os.mkdir(resultats) #créer le dossier si inexistant

#Scan les fichier dans le dossier d'inputs
for folder in [_.path for _ in os.scandir(imgDir) if _.is_dir()][0:1]:
    ortho_fn = [_.path for _ in os.scandir(folder) if _.is_file() if not "rescaled" in _.path][0]
    
    ortho_rescaled = resize_raster(ortho_fn, imgDir)
    
    seg_dir = os.path.join(folder, "segments")
    if not os.path.exists(seg_dir) :
        os.mkdir(seg_dir)
        
    for i in [100,200]:
        for j in [1,2]:
            for k in [50,150]:
                segmentation(ortho_rescaled, seg_dir, i,j,k)
    
    
    
        




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
        


