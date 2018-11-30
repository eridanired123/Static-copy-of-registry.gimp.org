; icefire logo
; Copyright (C) 2002-2003 Michael Schalla
; Copyright (C) 2004-2008 Eric Lamarque

; This program is free software; you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation; either version 2 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program; if not, write to the Free Software
; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

;  
; --------------------------------------------------------------------
; version 1.0 by Michael Schalla 2003/02/17
; version 2.0 by Eric Lamarque 2004/08/20
;   - support Gimp 2.0
; version 2.4 by Eric Lamarque 2007/05/21
;   - support Gimp 2.4
; version 2.4.1 by Eric Lamarque 2008/10/28
;   - do not rely on external def set-pt
; version 2.4.2 by Eric Lamarque 2008/11/03
;   - fix License
;   - update script register
; --------------------------------------------------------------------
;

(define (apply-ice-fire-logo-effect img inLayer inGrow inFire inFire2 inColor)
  (define (set-pt a index x y)
    (begin
      (aset a (* index 2) x)
      (aset a (+ (* index 2) 1) y)
    )
  )

  (let*
    (
			(width (car (gimp-drawable-width inLayer)))
			(height (car (gimp-drawable-height inLayer)))

			(theIceFireLayer (car (gimp-layer-new img width height RGBA-IMAGE "IceFire" 100 NORMAL)))

			(old-fg (car (gimp-context-get-foreground)))
			(old-bg (car (gimp-context-get-background)))
    )

		(gimp-image-resize img width height 0 0)
		(gimp-image-add-layer img theIceFireLayer 0)
		(gimp-edit-clear theIceFireLayer)

		(gimp-selection-layer-alpha inLayer)

		(if (> inGrow 0)
			(gimp-selection-grow img inGrow)
			(if (< inGrow 0)
				(gimp-selection-shrink img (- 0 inGrow))
			)	
		)
			
		(gimp-context-set-foreground '(255 255 255))
		(gimp-edit-fill theIceFireLayer FG-IMAGE-FILL)
		(gimp-selection-none img)

		(plug-in-cubism 1 img theIceFireLayer inFire2 2.5 0)
		(plug-in-rotate 1 img theIceFireLayer 3 FALSE)
		(plug-in-wind 1 img theIceFireLayer 10 1 inFire 1 1)
		(plug-in-rotate 1 img theIceFireLayer 1 FALSE)
;    (plug-in-ripple 1 img theIceFireLayer inFire inFire2 1 0 1 TRUE FALSE)
    (plug-in-ripple 1 img theIceFireLayer (* 2 inFire2) (/ inFire2 3) 1 0 1 TRUE FALSE)
    (plug-in-spread 1 img theIceFireLayer inFire2 inFire2)

    (plug-in-gauss-iir 1 img theIceFireLayer 3 TRUE TRUE)
		
    (define (splineValue)
      (let* ((a (cons-array 33 'byte)))
        (set-pt a 0   0   0)
        (set-pt a 1  32 255)
        (set-pt a 2  64 128)
        (set-pt a 3  96  72)
        (set-pt a 4 128 184)
        (set-pt a 5 160 128)
        (set-pt a 6 192 255)
        (set-pt a 7 224 128)
        (set-pt a 8 240 255)
        (set-pt a 9 252 128)
        (set-pt a 10 255 255)
        a
      )
    )
    (gimp-curves-spline theIceFireLayer VALUE-LUT 22 (splineValue))

    (define (larg-default l n v) 
      (if (> (nth n l) v)
	  (nth n l)
	  v))
		(define red (larg-default inColor 0 0))
		(if (= red 0)
			(set! red 1)
	 		(if (= red 255)
 				(set! red 254)
 			)
		)
		(define green (larg-default inColor 1 0))
		(if (= green 0)
			(set! green 1)
	 		(if (= green 255)
 				(set! green 254)
 			)
		)
		(define blue (larg-default inColor 2 0))
		(if (= blue 0)
			(set! blue 1)
	 		(if (= blue 255)
 				(set! blue 254)
 			)
		)
		(define gray (/ (+ (* red 299) (* green 587) (* blue 114)) 1000))

    (define (splineRed)
      (let* ((a (cons-array 6 'byte)))
        (set-pt a 0 0 0)
        (set-pt a 1 gray red)
        (set-pt a 2 255 255)
        a
      )
    )
    (gimp-curves-spline theIceFireLayer RED-LUT 6 (splineRed))

    (define (splineGreen)
      (let* ((a (cons-array 6 'byte)))
        (set-pt a 0 0 0)
        (set-pt a 1 gray green)
        (set-pt a 2 255 255)
        a
      )
    )
    (gimp-curves-spline theIceFireLayer GREEN-LUT 6 (splineGreen))

    (define (splineBlue)
      (let* ((a (cons-array 6 'byte)))
        (set-pt a 0 0 0)
        (set-pt a 1 gray blue)
        (set-pt a 2 255 255)
        a
      )
    )
    (gimp-curves-spline theIceFireLayer BLUE-LUT 6 (splineBlue))

    (gimp-curves-spline theIceFireLayer ALPHA-LUT 22 (splineValue))

    (gimp-context-set-background old-bg)
    (gimp-context-set-foreground old-fg)
	)
)

(define (script-fu-ice-fire-alpha img theLayer inGrow inFire inFire2 inFireColor)
  (begin
    (gimp-undo-push-group-start img)

		(apply-ice-fire-logo-effect img theLayer inGrow inFire inFire2 inFireColor)
		
    (gimp-undo-push-group-end img)
    (gimp-displays-flush)))

(script-fu-register "script-fu-ice-fire-alpha"
	_"MS - Ice Fire..."
	"Creates a ice-fire logo."
	"Michael Schalla"
	"Michael Schalla"
	"Februar 2001"
	"RGBA"
	SF-IMAGE    "Image"						 0
	SF-DRAWABLE "Drawable"				 0
  SF-ADJUSTMENT "Grow"					 '(-6 -50 50 1 1 0 1)
  SF-ADJUSTMENT "Fire-Dim1"			 '(32 2 100 1 1 0 1)
  SF-ADJUSTMENT "Fire-Dim2"			 '(8 2 100 1 1 0 1)
  SF-COLOR  "Fire Color"          '(32 64 128)
)

(script-fu-menu-register "script-fu-ice-fire-alpha"
			 "<Image>/Filters/Alpha to Logo")

(define (script-fu-ice-fire-logo inText inFont inFontSize inFireColor inTextColor inGrow inFire inFire2 inAbsolute inImageWidth inImageHeight inFlatten)
  (let*
    (
      ; Definition unserer lokalen Variablen

      ; Erzeugen des neuen Bildes

      (img  ( car (gimp-image-new 10 10 RGB) ) )
      (theText)
      (theTextWidth)
      (theTextHeight)
      (imgWidth)
      (imgHeight)
      (theBufferX)
      (theBufferY)
      (theTextLayer2)

      ; Erzeugen einer neuen Ebene zum Bild
      (theLayer (car (gimp-layer-new img 10 10 RGB-IMAGE "Ebene 1" 100 NORMAL) ) )
      (theTextLayer (car (gimp-layer-new img 10 10 RGBA-IMAGE "Ebene 2" 100 NORMAL) ) )

      (old-fg (car (gimp-context-get-foreground) ) )
      (old-bg (car (gimp-context-get-background) ) )
      ; Ende unserer lokalen Variablen
    )

    (gimp-image-add-layer  img theLayer 0)
    (gimp-image-add-layer  img theTextLayer 0)

    ; zum Anzeigen des leeren Bildes
    ; (gimp-display-new img)

    (gimp-context-set-background '(0 0 0) )
    (gimp-context-set-foreground inTextColor)

    (gimp-selection-all  img)
    (gimp-edit-clear     theLayer)
    (gimp-edit-clear     theTextLayer)
    (gimp-selection-none img)

    (set! theText (car (gimp-text-fontname img theTextLayer 0 0 inText 0 TRUE inFontSize PIXELS inFont)))

    (set! theTextWidth  (car (gimp-drawable-width  theText) ) )
    (set! theTextHeight (car (gimp-drawable-height theText) ) )

    (set! imgWidth inImageWidth )
    (set! imgHeight inImageHeight )

    (if (= inAbsolute FALSE)
      (set! imgWidth (+ theTextWidth theTextHeight inFire inFire2 ) )
    )

    (if (= inAbsolute FALSE)
      (set! imgHeight (+ (* theTextHeight 1.5 ) (* 4 (+ inFire inFire2 inGrow ) ) ) )
    )

    (set! theBufferX      (/ (- imgWidth theTextWidth) 2) )
    (set! theBufferY      (+ (/ (- imgHeight theTextHeight) 2) (+ inFire inFire inFire2 inGrow ) ) )

    (gimp-image-resize img imgWidth imgHeight 0 0)
    (gimp-layer-resize theLayer imgWidth imgHeight 0 0)
    (gimp-layer-resize theTextLayer imgWidth imgHeight 0 0)

    (gimp-layer-set-offsets   theText theBufferX theBufferY )
    (gimp-floating-sel-anchor theText)

    (set! theTextLayer2 (car (gimp-layer-copy theTextLayer TRUE)))
    (gimp-image-add-layer img theTextLayer2 1)

    (plug-in-gauss-iir 1 img theTextLayer2 16 TRUE TRUE)
    (plug-in-bump-map 1 img theTextLayer theTextLayer2 135.0 45.0 32 0 0 0 0 TRUE FALSE 0)

    (gimp-selection-layer-alpha theTextLayer)
    (gimp-selection-grow img 2)
    (gimp-selection-feather img 8)
		
		(gimp-context-set-foreground '(255 255 255))
		(gimp-edit-fill theTextLayer2 FG-IMAGE-FILL)
		(gimp-selection-none img)
		
		(apply-ice-fire-logo-effect img theTextLayer inGrow inFire inFire2 inFireColor)

    (if (= inFlatten TRUE)
      (gimp-image-flatten img)
      ()
    )

    (gimp-context-set-background old-bg)
    (gimp-context-set-foreground old-fg)

    (gimp-display-new     img)
    (list  img theLayer theText)

    ; Bereinigen Dirty-Flag
    (gimp-image-clean-all img)

  )
)

(script-fu-register
  "script-fu-ice-fire-logo"
  "MS - Ice Fire..."
  "Creates a ice-fire logo."
  "Michael Schalla"
  "Michael Schalla"
  "October 2002"
  ""
  SF-STRING "Text"               "ice fire"
  SF-FONT   "Font"               "-*-Arial Black-*-r-*-*-24-*-*-*-p-*-*-*"
  SF-ADJUSTMENT "Font Size"      '(200 2 1000 1 10 0 1)
  SF-COLOR  "Fire Color"         '(32 64 128)
  SF-COLOR  "Text Color"         '(64 128 128)
  SF-ADJUSTMENT "Grow"					 '(-6 -50 50 1 1 0 1)
  SF-ADJUSTMENT "Fire-Dim1"			 '(32 2 100 1 1 0 1)
  SF-ADJUSTMENT "Fire-Dim2"			 '(8 2 100 1 1 0 1)
  SF-TOGGLE "Absolute Size?"     FALSE
  SF-VALUE  "Image Width"        "400"
  SF-VALUE  "Image Height"       "150"
  SF-TOGGLE "Flatten Layers?"    FALSE
)

(script-fu-menu-register "script-fu-ice-fire-logo"
                         "<Toolbox>/Xtns/Logos")
