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
    
    x = X/Y*3000
    y = 3000
    
    gdal.Warp(dest, ds, height = y, width = x)



# #input
os.chdir(os.path.dirname(__file__))
imgDir = '../02-inputs/'

#Output
resultats= '../03-resultats/'
if not os.path.isdir(resultats) :   os.mkdir(resultats) #créer le dossier si inexistant

#Scan les fichier dans le dossier d'inputs
file_paths = [file.path for file in os.scandir(imgDir) if file.is_file()]

# Lance la segmentation sur tout les fichiers present dans imgDir
for path in file_paths:    
    
    file_name = path.split(sep="/")[-1] #nom du fichier
    # Lecture des donnés de l'ortho
    ref_ds, bdata_ortho = functions.readFiles(path)

    img = exposure.rescale_intensity(bdata_ortho) #rescale des valeurs à 0-1
    
    # boucle pour different parametres de segmentation
    for i in [20,100,200]:
        for j in [0.2, 0.5, 1, 5]:
            toc = time.time() #timer
            print("segments start ")
            
            #Segmentation Quickshift :            
            # segments = quickshift(img, convert2lab=0, kernel_size=k, ratio=r)
            # segments_fn = resultats+f'seg-ker{k}-ratio{r*100}-'+file
            
            # Segmentation Felzenszwalb
            segments = felzenszwalb(img, scale=i, sigma=j, min_size=50)
            segments_fn = resultats+f'felz-scale{i}-sigma{j*10}'+file_name
            
            functions.writeRaster(segments, segments_fn, ref_ds)
            tic= time.time()
        
            print(f"{segments_fn} crée en : {tic-toc}")
        


