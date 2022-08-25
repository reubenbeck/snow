#%%
import glob
from PIL import Image

# filepaths
fp_in = 'D:\\Users\\Reuben\\Internship\\Monthly_Plots\\*.jpg'
fp_out = 'D:\\Users\\Reuben\\Internship\\snow_monthly_swe.gif'

# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
imgs = (Image.open(f) for f in sorted(glob.glob(fp_in)))
img = next(imgs)  # extract first image from iterator
img.save(fp=fp_out, format='GIF', append_images=imgs,
         save_all=True, duration=150, loop=0)
# %%
