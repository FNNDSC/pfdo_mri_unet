This is an application that combine pfdo mechanism on mri_unet(A U-net classification application) to iteratively process various sub directories containing input training data.

As of now, the training data that mri_unet requires are 2 npy files: imgs_train.npy & imgs_train_mask.npy

So each of the sub-directories should contain these 2 files inorder to be a viable input for pfdo_mri_unet.

How do I get these input training data?
----------------------------------------------

The easiest way for a quick and dirty trial is to run the plug-in `pl-mgz_converter` on the dataset `mgz_converter_dataset`
The output folder will contain the 2 above mentioned npy files as well a 2 directories `masks` & `train` containing .png slices for reference



Barebones example to run pfdo_mri_unet
-----------------------------------------------

Create an input directory, say `mri_input`
Create multiple sub-directories like `sub-1`, `sub-2`, ...
Inside each of the sub-directory, place the input training data.
Now `mri_input` becomes a valid input directory for `pfdo_mri_unet`

