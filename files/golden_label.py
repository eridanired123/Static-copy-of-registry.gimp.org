#!/usr/bin/env python
#
#   Gimp plugin to create envelope labels with golden text.
#   Tested with python 2.5, GIMP 2.4.4, and MySQL 5.045
#
#   Written by Andy Zobro.  This script is my first, based on code written by
#   Werner Hartnagel (Yin Yang) and a tutorial by Simon Budig.  The tutorial can
#   be found at (http://www.gimp.org/tutorials/Golden_Text/)
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from gimpfu import *

import re
import os
import MySQLdb

try:
   debug_environment
except:
   debug_environment = False
# end try

# Examples of the types of sql code that will work
#  WHERE name REGEXP '.*daub.*' ORDER BY name LIMIT 1
#  WHERE invite = 'Y' AND street1 REGEXP '.*[0-9].*' ORDER BY name LIMIT 1 

# this function can easily be stripped out and made into its own golden test function
# that doesn't rely on sql or deal with multiple lines of text
def golden(line1, line2, line3, line4,
      env_width,
      env_height,
      dpi,
      fontname,    # font = "Hancock Ultra-Light"
      envmap_file, # see the tutorial by Simon Budig for info on how to make a good one
      do_return_label,
      return_image,
      export_type,
      save_to
     ):
   # these are starting values ONLY, in case there is some big text coming up
   width = 1000
   height = 500

   # create an image
   img1 = gimp.Image(width, height, GRAY)
   
   name_layer = None
   address1_layer = None
   address2_layer = None
   citystatezip_layer = None

   # make white text
   fontcolor = (255, 255, 255)
   fontsize_pixels = 0.375 * dpi
   border = 0.3 * fontsize_pixels
   y = border
   if (line1 != '' and line1 != None):
      name_layer =         add_bw_text(img1, border, y, "name",
         line1,
         fontcolor, fontname, fontsize_pixels)
      y = y + (fontsize_pixels * 1.1)
   # end if
   if (line2 != '' and line2 != None):
      address1_layer =     add_bw_text(img1, border, y, "address1",
         line2,
         fontcolor, fontname, fontsize_pixels)
      y = y + (fontsize_pixels * 1.1)
   # end if
   if (line3 != '' and line3 != None):
      address2_layer =     add_bw_text(img1, border, y, "address2",
         line3,
         fontcolor, fontname, fontsize_pixels)
      y = y + (fontsize_pixels * 1.1)
   # end if
   if (line4 != '' and line4 != None):
      citystatezip_layer = add_bw_text(img1, border, y, "citystatezip", 
         line4,
         fontcolor, fontname, fontsize_pixels)
   # end if

   # make whole image correct size for text provided
   pdb.gimp_image_resize_to_layers(img1)
   pdb.gimp_image_resize(img1, (img1.width  + 2*border),
                               (img1.height + 2*border),
                               (border),
                               (border))
   
   # make black background
   gimp.set_background(0,0,0)
   black_bg_layer = gimp.Layer(img1, "black_bg", img1.width, img1.height, GRAYA_IMAGE, 100, NORMAL_MODE)
   img1.add_layer(black_bg_layer, 0)
   img1.active_layer = black_bg_layer
   draw = pdb.gimp_image_get_active_drawable(img1)
   draw.fill(BACKGROUND_FILL)
   # move said "background" to the background
   pdb.gimp_image_lower_layer_to_bottom(img1, black_bg_layer)

   # do a gaussian blur
   radius = 2.0
   if (name_layer is not None):
      pdb.plug_in_gauss(img1, name_layer, radius, radius, 1)
   # end if
   if (address1_layer is not None):
      pdb.plug_in_gauss(img1, address1_layer, radius, radius, 1)
   # end if
   if (address2_layer is not None):
      pdb.plug_in_gauss(img1, address2_layer, radius, radius, 1)
   # end if
   if (citystatezip_layer is not None):
      pdb.plug_in_gauss(img1, citystatezip_layer, radius, radius, 1)
   # end if

   # flatten image
   flat_layer = pdb.gimp_image_flatten(img1)
   # copy layer
   success = pdb.gimp_edit_copy(flat_layer)

   img2 = gimp.Image(img1.width, img1.height, RGB)
   img2.undo_group_start()
   if (debug_environment):
      disp2 = gimp.Display(img2)
   # end if debug
   
   # paste layer from img1 to img2
   golden_layer = gimp.Layer(img2, "golden_layer", img2.width, img2.height, RGBA_IMAGE, 100, NORMAL_MODE)
   img2.add_layer(golden_layer, 0)
   floater = pdb.gimp_edit_paste(golden_layer, 1)
   # purge the original/old img1 file
   pdb.gimp_image_delete(img1)
   # open the environment map
   envmap = pdb.gimp_file_load(envmap_file, envmap_file)
   #disp_envmap = gimp.Display(envmap)
   envdraw = pdb.gimp_image_get_active_drawable(envmap)
   bumpdraw = pdb.gimp_image_get_active_drawable(img2)

#def other ():

   #plug_in_lighting
   image = img2         #Input image
   drawable = bumpdraw      #Input drawable
   bumpdrawable = bumpdraw      #Bumpmap drawable (set to 0 if disabled)
   envdrawable = envdraw      #Environmentmap drawable (set to 0 if disabled)
   dobumpmap = 1         #Enable bumpmapping (TRUE/FALSE)
   doenvmap = 1         #Enable envmapping (TRUE/FALSE)
   bumpmaptype = 0         #Type of mapping (0=linear,1=log, 2=sinusoidal, 3=spherical)
   lighttype = 1         #Type of lightsource (0=point,1=directional,3=spot,4=none)
   lightcolor = (255,255,255)   #Lightsource color (r,g,b)
   lightposition_x   = -1      #Lightsource position (x,y,z)
   lightposition_y   = -1      #Lightsource position (x,y,z)
   lightposition_z   = 1      #Lightsource position (x,y,z)
   lightdirection_x = -1 # unused   #Lightsource direction [x,y,z]
   lightdirection_y = -1 # unused   #Lightsource direction [x,y,z]
   lightdirection_z =  1 # unused   #Lightsource direction [x,y,z]
   # from http://source.macgimp.org/plug-ins/Lighting/lighting_main.c
   #mapvals.material.ambient_int  =  0.2;
   #mapvals.material.diffuse_int  =  0.5;
   #mapvals.material.diffuse_ref  =  0.4;
   #mapvals.material.specular_ref =  0.5;
   #mapvals.material.highlight    = 27.0;
   #mapvals.material.metallic     = FALSE;
   ambient_intensity = 0.2      #Material ambient intensity (0..1)
   diffuse_intensity = 0.5      #Material diffuse intensity (0..1)
   diffuse_reflectivity = 0.4   #Material diffuse reflectivity (0..1)
   specular_reflectivity =   0.5   #Material specular reflectivity (0..1)
   highlight = 27.0      #Material highlight (0..->), note: it's expotential
   # there doesn't seem to be a way to set the max height of a bump-map :-(
   # from http://source.macgimp.org/plug-ins/Lighting/lighting_main.c
     # mapvals.bumpmaptype = 0;   
     # mapvals.bumpmin     = 0.0;
     # mapvals.bumpmax     = 0.1;
   antialiasing = 1      #Apply antialiasing (TRUE/FALSE)
   newimage = 0         #Create a new image (TRUE/FALSE)
   transparentbackground = 0   #Make background transparent (TRUE/FALSE)
   
   pdb.plug_in_lighting(image,
              drawable,
              bumpdrawable,
              envdrawable,
              dobumpmap,
              doenvmap,
              bumpmaptype,
              lighttype,
              lightcolor,
              lightposition_x,
              lightposition_y,
              lightposition_z,
              lightdirection_x,
              lightdirection_y,
              lightdirection_z,
              ambient_intensity,
              diffuse_intensity,
              diffuse_reflectivity,
              specular_reflectivity,
              highlight,
              antialiasing,
              newimage,
              transparentbackground)

   # all this effort so far has been on a floating selection, anchor it.
   pdb.gimp_floating_sel_anchor(floater)
   
   # make a layer mask of the golden layer
   golden_mask = pdb.gimp_layer_create_mask(golden_layer, ADD_WHITE_MASK)
   pdb.gimp_layer_add_mask(golden_layer, golden_mask)
   #img2.active_layer = golden_mask
   #img2.active_channel = golden_mask
   #pdb.gimp_image_set_active_channel(img2, golden_mask)
   gold_mask = pdb.gimp_layer_get_mask(golden_layer)
   
   # paste existing copy buffer into the mask
   floater = pdb.gimp_edit_paste(gold_mask, 1)
   pdb.gimp_floating_sel_anchor(floater)

   # make the background the prefered color (white)
   gimp.set_background(255,255,255)
   bg_layer = gimp.Layer(img2, "bg_layer", img2.width, img2.height, RGBA_IMAGE, 100, NORMAL_MODE)
   img2.add_layer(bg_layer, 0)
   img2.active_layer = bg_layer
   draw = pdb.gimp_image_get_active_drawable(img2)
   draw.fill(BACKGROUND_FILL)
   # move said "background" to the background
   pdb.gimp_image_lower_layer_to_bottom(img2, bg_layer)

   # finish & print
   # resize image to match envelope
   pdb.gimp_image_resize(img2, ( env_width * dpi),
                               ( env_height * dpi),
                               ( 0 * dpi),      # will be centered
                               ( 0 * dpi))
   place_and_scale_address(img2, golden_layer, dpi)
   place_and_scale_address(img2, bg_layer, dpi)

   #draw.fill(BACKGROUND_FILL)
   if (do_return_label):
      return_label = pdb.gimp_file_load_layer(img2, return_image)
      pdb.gimp_image_add_layer(img2, return_label, 0)
      return_label.set_offsets(int(0.15 * dpi), int(0.15 * dpi))
   # end if
   
   # Disable Undo
   img2.undo_group_end()
   image.undo_group_start()
   envelope_layer = pdb.gimp_image_flatten(img2)
   img2.undo_group_end()

   #show_text(export_type)
   #show_text(save_to)
   if (save_to != '' and save_to is not None):
      filename = "untitled"
      if (export_type != 'None'):
         if (line1 != '' and line1 != None):
            filename = line1
         elif (line2 != '' and line2 != None):
            filename = line2
         # end if
      # end if

      # make a nicer filename (after the ^ is the list of acceptable characters)
      filename = re.sub("[^a-zA-Z0-9_-]", "", filename)
      save_to = re.sub("[\\/]$", "", save_to) # remove trailing [back]slash if there is one
      filename = save_to + os.sep + filename
      
      if (export_type == 'jpg'):
         # save as jpeg
         filename = filename + ".jpg"
         # I attempted to guess at the defaults... the lists might be wrong
         pdb.file_jpeg_save(img2, envelope_layer, filename, filename, 0.85, 0, 1, 0, "golden address label, created with gimp-python", 3, 1, 0, 1) 
         #Input:
         #IMAGE	image	Input image
         #DRAWABLE	drawable	Drawable to save
         #STRING	filename	The name of the file to save the image in
         #STRING	raw_filename	The name of the file to save the image in
         #SUCCESS	quality	Quality of saved image (0 <= quality <= 1)
         #SUCCESS	smoothing	Smoothing factor for saved image (0 <= smoothing <= 1)
         #INT32	optimize	Optimization of entropy encoding parameters (0/1)
         #INT32	progressive	Enable progressive jpeg image loading (0/1)
         #STRING	comment	Image comment
         #INT32	subsmp	The subsampling option number
         #INT32	baseline	Force creation of a baseline JPEG (non-baseline JPEGs can't be read by all decoders) (0/1)
         #INT32	restart	Frequency of restart markers (in rows, 0 = no restart markers)
         #INT32	dct	DCT algorithm to use (speed/quality tradeoff)
         pass
      elif (export_type == 'png'):
         # save as PNG
         filename = filename + ".png"
         pdb.file_png_save_defaults(img2, envelope_layer, filename, filename)
         # file_png_save_defaults
         # IMAGE	image	Input image
         # DRAWABLE	drawable	Drawable to save
         # STRING	filename	The name of the file to save the image in
         # STRING	raw_filename	The name of the file to save the image in
         pass
      # end if
      if (export_type != 'None'):
         pdb.gimp_image_delete(img2)
      else:
         disp2 = gimp.Display(img2)
      # end if
   # end if
      

def center_layer_horizontal(image, layer):
   x = (image.width - layer.width) / 2
   y = layer.offsets[1]
   layer.set_offsets(x, y)
# end def

def place_and_scale_address(image, layer, dpi):
   # specify the maximum size of the main address in terms of inches and percentage
   max_width = min(5.0 * dpi, 0.85 * image.width)
   max_height = min(1.5 * dpi, 0.30 * image.height)
   if (layer.width > max_width):
      # address label is too wide, rescale the whole thing.
      new_width = min(layer.width, max_width)
      new_height = (layer.height/float(layer.width)) * new_width
      pdb.gimp_layer_scale(layer, new_width, new_height, 1)
   # end if
   if (layer.height > max_height):
      # address label is too tall, rescale the whole thing.
      new_height = min(layer.height, max_height)
      new_width = (layer.width/float(layer.height)) * new_height
      pdb.gimp_layer_scale(layer, new_width, new_height, 1)
   # end if

   x = int((-layer.width/2.0) + (image.width * 0.55))          # centered 55% from the left
   y = int((-layer.height/2.0) + (image.height * 0.60))        # centered 60% from the top
   layer.set_offsets(x, y)
# end def

def center_layer(image, layer):
   x = (image.width - layer.width) / 2
   y = (image.height - layer.height) / 2
   layer.set_offsets(x, y)
# end def

def add_bw_text(image, x, y, layer_name, text, color, fontname, fontsize):
   image.undo_group_start()
   foreground = gimp.get_foreground();
   gimp.set_foreground(color)

   textlayer = gimp.Layer(image, layer_name, image.width, image.height, GRAYA_IMAGE, 100, NORMAL_MODE)
   image.add_layer(textlayer, 0)
   pdb.gimp_drawable_fill(textlayer, 3) # transparent fill

   gimp.set_background(255, 255, 255)
   gimp.set_foreground(color)

   floattext = pdb.gimp_text_fontname(image, textlayer, x, y, text, 1, 1, fontsize, PIXELS, fontname)
   pdb.gimp_layer_resize(textlayer, floattext.width, floattext.height, -x, -y)

   pdb.gimp_floating_sel_anchor(floattext)

   gimp.set_foreground(foreground)
   image.undo_group_end()
   return textlayer
# end def add_line

def show_text(text):
   if (text != '' and text != None):
      img1 = gimp.Image(400,400, GRAY)
      disp1 = gimp.Display(img1)

      fontcolor = (255, 0, 0)
      fontsize_pixels = 30
      border = 0.3 * fontsize_pixels
      y = border
      name_layer =         add_bw_text(img1, border, y, text,
         text,
         fontcolor, "Sans", fontsize_pixels)
   # end if
# end def show_text

def process_addresses( dpi, width, height, 
                       do_return_label, return_label_filename, 
                       environment_map_filename, font,
                       sql_server_name, sql_user_name, sql_password, sql_database, sql_table,
                       sql_field_names, sqlcode, export_type, save_to):
   connection = MySQLdb.connect(host = sql_server_name, user = sql_user_name, passwd = sql_password, db = sql_database)
   cursor = connection.cursor()
   query = "SELECT %s FROM %s %s;"%(sql_field_names, sql_table, sqlcode)
   cursor.execute(query)
   row = cursor.fetchone()
   while (row != None):
      (name, street1, street2, city, state, zip) = row
      line1 = name
      line2 = street1
      if (street2 != ""):
         line3 = street2
         line4 = "%s, %s %s"%(city, state, zip)
      else:
         line3 = "%s, %s %s"%(city, state, zip)
         line4 = None
      # end if
      golden(line1, line2, line3, line4, 
             width, height, dpi,
             font,
             environment_map_filename,
             do_return_label,
             return_label_filename,
             export_type,
             save_to)
      row = cursor.fetchone()
   # end while
# end def

register("golden_label",
         "Create Golden Labels", # tool tip in menu
         "Batch creation of Golden Address Labels from a MySQL Database",
         "Andy Zobro",
         "Andy Zobro",
         "2008",
         "<Toolbox>/Xtns/Languages/Python-Fu/Create Golden Mailing Labels...",
         None,
         [
            (PF_INT32, "dpi", "dpi", 300),
            (PF_FLOAT, "width", "Width (inches)", 5.75), #8.75),
            (PF_FLOAT, "height", "Height (inches)", 4.38),  #5.68),
            (PF_TOGGLE, "do_return_label", "Add Return Label", 1),
            (PF_FILENAME, "return_label_filename", "Return Label \"Sticker\"", ""),
            (PF_FILENAME, "environment_map_filename", "Environment Map (Golden)", "C:\\Documents and Settings\\Andy\\.gimp-2.4\\patterns\\envmap_gold3.jpg"),
            (PF_FONT, "font", "Font", "Hancock Ultra-Light"),
            (PF_STRING, "sql_server_name", "MySQL server", "server"),
            (PF_STRING, "sql_user_name", "MySQL username", "weddingdbuser"),
            (PF_STRING, "sql_password", "MySQL password", "password"),
            (PF_STRING, "sql_database", "MySQL dbname", "weddingdb"),
            (PF_STRING, "sql_table", "MySQL table", "guests"),
            (PF_STRING, "sql_field_names", "[unchecked] MySQL fields for:\r name, street1, street2, city, state, zip", "name, street1, street2, city, state, zip"),
            (PF_STRING, "sqlcode", "Additional [unchecked] MySQL code", "WHERE invite = 'Y' ORDER BY name LIMIT 1"),
            (PF_RADIO, "export_type", "Export as", "png", (("NONE","None"), ("JPEG","jpg"), ("PNG","png"))),
            (PF_DIRNAME, "save_to", "Export files to", ""), #str
         ],
         [],
         process_addresses)   # the function handle

if (not debug_environment):
   main()      # this should only be called once...
else:
   print "debugging... did not execute main()"
# end if not in a debugging environment
